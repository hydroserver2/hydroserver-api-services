from __future__ import annotations
from uuid import UUID
from dataclasses import dataclass
from typing import Any

from hydroserverpy.etl.loaders.base import Loader
import logging
import pandas as pd
from datetime import datetime, timezone as dt_timezone
from django.db.models import Min, Value
from django.db.models.functions import Coalesce
from domains.etl.models import Task
from domains.sta.services import ObservationService
from domains.sta.models import Datastream
from interfaces.api.schemas.observation import ObservationBulkPostBody

observation_service = ObservationService()


@dataclass(frozen=True)
class LoadSummary:
    cutoff: str
    timestamps_total: int
    timestamps_after_cutoff: int
    observations_available: int
    observations_loaded: int
    datastreams_loaded: int


class HydroServerInternalLoader(Loader):
    """
    A class that extends the HydroServer client with ETL-specific functionalities.
    """

    def __init__(self, task):
        self._begin_cache: dict[str, pd.Timestamp] = {}
        self.task = task

    def load(self, data: pd.DataFrame, task: Task) -> LoadSummary:
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
        timestamps_total = len(data)
        timestamps_after_cutoff = len(new_data)
        observations_available = 0
        observations_loaded = 0
        datastreams_loaded = 0

        for col in new_data.columns.difference(["timestamp"]):
            df = (
                new_data[["timestamp", col]]
                .rename(columns={col: "value"})
                .dropna(subset=["value"])
            )
            available = len(df)
            observations_available += available
            if available == 0:
                logging.warning(
                    "No new observations for %s after filtering; skipping.", col
                )
                continue

            df = df.rename(columns={"timestamp": "phenomenonTime", "value": "result"})

            loaded = 0
            # Chunked upload
            CHUNK_SIZE = 5000
            total = len(df)
            chunks = (total + CHUNK_SIZE - 1) // CHUNK_SIZE
            logging.info(
                "Uploading %s observation(s) to datastream %s (%s chunk(s), chunk_size=%s)",
                total,
                col,
                chunks,
                CHUNK_SIZE,
            )
            for start in range(0, total, CHUNK_SIZE):
                end = min(start + CHUNK_SIZE, total)
                chunk = df.iloc[start:end]
                logging.debug(
                    "Uploading chunk to datastream %s: rows %s-%s (%s rows)",
                    col,
                    start,
                    end - 1,
                    len(chunk),
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

            if loaded > 0:
                datastreams_loaded += 1
            observations_loaded += loaded

        return LoadSummary(
            cutoff=cutoff_value,
            timestamps_total=timestamps_total,
            timestamps_after_cutoff=timestamps_after_cutoff,
            observations_available=observations_available,
            observations_loaded=observations_loaded,
            datastreams_loaded=datastreams_loaded,
        )

    @staticmethod
    def _fetch_earliest_begin(task: Task) -> pd.Timestamp:
        logging.info(
            "Checking HydroServer for the most recent data already stored (so we only extract new observations)..."
        )

        return Datastream.objects.filter(
            id__in={
                path.target_identifier
                for mapping in task.mappings.all()
                for path in mapping.paths.all()
            }
        ).aggregate(
            earliest_end=Coalesce(
                Min("phenomenon_end_time"), Value(datetime(1880, 1, 1, tzinfo=dt_timezone.utc))
            )
        )[
            "earliest_end"
        ]

    def earliest_begin_date(self, task: Task) -> pd.Timestamp:
        """
        Return earliest begin date for a payload, or compute+cache it on first call.
        """
        key = task.name
        if key not in self._begin_cache:
            self._begin_cache[key] = self._fetch_earliest_begin(task)
        return self._begin_cache[key]
