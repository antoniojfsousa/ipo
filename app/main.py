import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import engine
from app import models
from app.routers import patients, consents, gmnf, therapy, exams, alerts, timeline, consultas, suggestions
from app.services.alert_service import run_all_alerts
from app.database import SessionLocal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all DB tables
    models.Base.metadata.create_all(bind=engine)
    # Run initial alert check
    db = SessionLocal()
    try:
        run_all_alerts(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Sistema de Gestão Clínica NF-IPO Lisboa",
    description="Sistema de gestão clínica para doentes com Neurofibromatose tipo 1 no IPO Lisboa",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(FRONTEND_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include all routers
app.include_router(patients.router)
app.include_router(consents.router)
app.include_router(gmnf.router)
app.include_router(therapy.router)
app.include_router(exams.router)
app.include_router(alerts.router)
app.include_router(timeline.router)
app.include_router(consultas.router)
app.include_router(suggestions.router)


@app.get("/", include_in_schema=False)
def serve_dashboard():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Sistema NF-IPO Lisboa", "docs": "/docs"}


@app.get("/patients-view", include_in_schema=False)
def serve_patient_view():
    patient_path = os.path.join(FRONTEND_DIR, "patient.html")
    if os.path.exists(patient_path):
        return FileResponse(patient_path)
    return {"message": "Patient view"}
