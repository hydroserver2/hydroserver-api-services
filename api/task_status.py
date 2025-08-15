import uuid
from ninja import Router, Path
from django_tasks import default_task_backend
from hydroserver.http import HydroServerHttpRequest
from api.schemas import TaskStatusResponse


task_router = Router(tags=["Tasks"])


@task_router.get(
    "/{task_id}/status",
    response={
        200: TaskStatusResponse,
        404: str,
    },
    by_alias=True,
)
def get_task_status(
    request: HydroServerHttpRequest,
    task_id: Path[uuid.UUID],
):
    """
    Get the status of a task.
    """

    result = default_task_backend.get_result(task_id)

    return 200, {
        "id": result.id,
        "name": result.task.func.__name__,
        "arguments": result.kwargs or None,
        "status": result.status,
        "received_at": result.enqueued_at,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "message": "\n".join([e.traceback.strip().splitlines()[-1] for e in result.errors]) or None,
    }
