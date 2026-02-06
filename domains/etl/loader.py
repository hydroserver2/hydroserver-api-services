from __future__ import annotations
from uuid import UUID
from typing import Any, Dict

from hydroserverpy.etl.loaders.base import Loader
import logging
import pandas as pd
from datetime import datetime
from django.db.models import Min, Value
from django.db.models.functions import Coalesce
from domains.etl.models import Task
from domains.sta.services import ObservationService
from domains.sta.models import Datastream
from interfaces.api.schemas.observation import ObservationBulkPostBody

observation_service = ObservationService()


class HydroServerInternalLoader(Loader):
    """
    A class that extends the HydroServer client with ETL-specific functionalities.
    """

    def __init__(self, task):
        self._begin_cache: dict[str, pd.Timestamp] = {}
        self.task = task

    def load(self, data: pd.DataFrame, task: Task) -> Dict[str, Any]:
        """
        Load observations from a DataFrame to the HydroServer.
        """
        begin_date = self.earliest_begin_date(task)
        new_data = data[data["timestamp"] > begin_date]

        cutoff_value = (
            begin_date.isoformat()
            if hasattr(begin_date, "isoformat")
            else str(begin_date)
        )
        stats: Dict[str, Any] = {
            "cutoff": cutoff_value,
            "timestamps_total": len(data),
            "timestamps_after_cutoff": len(new_data),
            "timestamps_filtered_by_cutoff": max(len(data) - len(new_data), 0),
            "observations_available": 0,
            "observations_loaded": 0,
            "observations_skipped": 0,
            "datastreams_total": 0,
            "datastreams_available": 0,
            "datastreams_loaded": 0,
            "per_datastream": {},
        }

        for col in new_data.columns.difference(["timestamp"]):
            stats["datastreams_total"] += 1
            df = (
                new_data[["timestamp", col]]
                .rename(columns={col: "value"})
                .dropna(subset=["value"])
            )
            available = len(df)
            stats["observations_available"] += available
            if available == 0:
                logging.warning("No new data for %s after filtering; skipping.", col)
                stats["per_datastream"][str(col)] = {
                    "available": 0,
                    "loaded": 0,
                    "skipped": 0,
                }
                continue

            stats["datastreams_available"] += 1
            df = df.rename(columns={"timestamp": "phenomenonTime", "value": "result"})

            loaded = 0
            # Chunked upload
            CHUNK_SIZE = 5000
            total = len(df)
            for start in range(0, total, CHUNK_SIZE):
                end = min(start + CHUNK_SIZE, total)
                chunk = df.iloc[start:end]
                logging.info(
                    "Uploading %s rows (%s-%s) to datastream %s",
                    len(chunk),
                    start,
                    end - 1,
                    col,
                )

                chunk_data = ObservationBulkPostBody(
                    fields=["phenomenonTime", "result"],
                    data=chunk.values.tolist(),
                )

                try:
                    observation_service.bulk_create(
                        principal=self.task.data_connection.workspace.owner,
                        data=chunk_data,
                        datastream_id=UUID(col),
                        mode="append",
                    )
                    loaded += len(chunk)
                except Exception as e:
                    status = getattr(e, "status_code", None) or getattr(
                        getattr(e, "response", None), "status_code", None
                    )
                    if status == 409 or "409" in str(e) or "Conflict" in str(e):
                        logging.info(
                            "409 Conflict for datastream %s on rows %s-%s; skipping remainder for this stream.",
                            col,
                            start,
                            end - 1,
                        )
                        break
                    raise

            stats["observations_loaded"] += loaded
            stats["observations_skipped"] += max(available - loaded, 0)
            if loaded > 0:
                stats["datastreams_loaded"] += 1
            stats["per_datastream"][str(col)] = {
                "available": available,
                "loaded": loaded,
                "skipped": max(available - loaded, 0),
            }

        return stats

    @staticmethod
    def _fetch_earliest_begin(task: Task) -> pd.Timestamp:
        logging.info("Querying HydroServer for earliest begin date for payload...")

        return Datastream.objects.filter(id__in={
            path.target_identifier
            for mapping in task.mappings.all()
            for path in mapping.paths.all()
        }).aggregate(
            earliest_end=Coalesce(Min("phenomenon_end_time"), Value(datetime(1970, 1, 1)))
        )["earliest_end"]

    def earliest_begin_date(self, task: Task) -> pd.Timestamp:
        """
        Return earliest begin date for a payload, or compute+cache it on first call.
        """
        key = task.name
        if key not in self._begin_cache:
            self._begin_cache[key] = self._fetch_earliest_begin(task)
        return self._begin_cache[key]
