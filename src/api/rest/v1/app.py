import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from worker.index import handle_job
from api.index import health as get_health
from python_shared.http.middleware.correlation_middleware import CorrelationAndTelemetryMiddleware


class JobRequest(BaseModel):
    job_name: str
    message: dict


def create_app() -> FastAPI:
    app = FastAPI(title="Queue Embedding Worker API", version="1.1.0")
    app.add_middleware(CorrelationAndTelemetryMiddleware)

    @app.get("/health")
    async def health():
        return get_health()

    @app.post("/execute")
    async def execute_job(request: JobRequest):
        try:
            result = handle_job(request.job_name, request.message)
            return {
                "status": "success",
                "job": request.job_name,
                "result": result,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
