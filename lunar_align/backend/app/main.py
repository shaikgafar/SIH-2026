from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as api_router
from app.core.pipeline import pipeline

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="")

@app.on_event("startup")
def startup_event():
    print(f"[INFO] Initializing {settings.PROJECT_NAME}...")
    _ = pipeline.get_available_datasets()
    # Pre-warm primary datasets into memory so UI renders instantly
    try:
        pipeline.run_correspondence("dataset_scale_ohrc_tmc2")
        pipeline.run_correspondence("dataset_sun_angle_crater")
    except Exception as e:
        print(f"[WARN] Pre-warm note: {e}")
    print("[INFO] Chandrayaan-2 & LRO reference datasets ready!")

# Production static files mount for Vite frontend
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "dist"))

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static_assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        target_file = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "title": settings.PROJECT_NAME,
            "docs_url": "/docs",
            "api_v1": settings.API_V1_STR,
            "supported_payloads": ["OHRC", "TMC-2", "IIRS", "LRO NAC", "SELENE"]
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
