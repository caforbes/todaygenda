from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from api.routes.auth import get_current_user
from api.utils import error_detail
from src.models import ActionResult, NewTask, Task, User
import src.operations as backend


router = APIRouter(prefix="/task")


@router.post("/", summary="Add a new pending task", status_code=status.HTTP_201_CREATED)
def create_task(
    current_user: Annotated[User, Depends(get_current_user)], task: NewTask
) -> Task:
    """Add a new task into your list for today.

    Provide new task details with a time estimate less than 24hours. Today's task list
    must already exist for this to succeed. On a 404 failure, visit `/today` to set up
    today's list.
    """
    created_task = backend.create_task(current_user.id, task)
    if not created_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_detail("No list exists - can't add a new task."),
        )
    return created_task


@router.post("/bulk/do", summary="Mark many tasks as done")
def bulk_task_done(
    current_user: Annotated[User, Depends(get_current_user)], task_ids: list[int]
) -> ActionResult:
    """Mark a list of tasks from your list as done/completed in bulk."""
    successful, result_ids = backend.mark_tasks_done(current_user.id, task_ids=task_ids)

    if successful:
        return ActionResult(success=result_ids)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail(
                f"ERROR: Tasks not found in today's list: {result_ids}"
            ),
        )


@router.post("/{id}/do", summary="Mark a task as done")
def mark_task_done(
    current_user: Annotated[User, Depends(get_current_user)], id: int
) -> ActionResult:
    """Mark a task from your list as done/completed."""
    successful, result_ids = backend.mark_tasks_done(current_user.id, task_ids=[id])

    if successful:
        return ActionResult(success=result_ids)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail(f"ERROR: Task not found in today's list: {result_ids}"),
        )


@router.post("/{id}/undo", summary="Mark a done task as pending")
def mark_task_pending(
    current_user: Annotated[User, Depends(get_current_user)], id: int
) -> ActionResult:
    """Mark a done task from your list as pending."""
    successful, result_ids = backend.mark_tasks_pending(current_user.id, task_ids=[id])

    if successful:
        return ActionResult(success=result_ids)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail(f"ERROR: Task not found in today's list: {result_ids}"),
        )
