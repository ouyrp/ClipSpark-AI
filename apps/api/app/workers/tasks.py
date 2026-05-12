from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.render_video")
def render_video(edit_plan_id: str) -> dict:
    return {
        "edit_plan_id": edit_plan_id,
        "status": "not_implemented",
        "message": "FFmpeg rendering will be connected after Edit Plan validation.",
    }
