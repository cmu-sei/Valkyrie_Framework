from fastapi import FastAPI
from routers import searches, application

app = FastAPI(
    title="Beacon Huntress API",
    version="1.0.0",
    description="API endpoints for beacon hunting."
)

app.include_router(application.router)
app.include_router(searches.router)
