"""
Nuraxi Foundry Demo Prototype
King Faisal Specialist Hospital & Research Centre
Version 1.0 - January 2026

Main FastAPI application entry point.
"""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api import router

app = FastAPI(
    title="Nuraxi Foundry Demo",
    description="""
## Nuraxi Foundry Demo Prototype

Interactive demonstration of the Nuraxi Foundry platform capabilities for
King Faisal Specialist Hospital & Research Centre (KFSHRC).

### Demo Objectives

1. **Cross-system Patient Linkage**: Tokenization enables building longitudinal
   patient records across multiple disconnected hospital systems while maintaining
   complete anonymity.

2. **Data Transformation**: Conversion of fragmented, unstructured clinical data
   into standardized OMOP Common Data Model format.

3. **De-identification**: Safe Harbor compliant de-identification with realistic
   surrogate data (HiPS methodology).

4. **Research Capabilities**: Cohort queries and analytics on the transformed data.

5. **AI Clinical Intelligence**: Clinical agents reviewing patient encounters
   and generating actionable insights.

### Getting Started

1. Generate synthetic data: `POST /api/demo/generate-data`
2. Run tokenization: `POST /api/demo/tokenize`
3. De-identify data: `POST /api/demo/deidentify`
4. Transform to OMOP: `POST /api/demo/transform-to-omop`
5. Query cohorts: `POST /api/demo/cohort/query`
6. Analyze with AI: `GET /api/demo/ai/analyze-patient/{person_id}`

Or run the full pipeline: `POST /api/demo/full-pipeline`
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

# Check if frontend build exists (for single-service deployment)
FRONTEND_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "nuraxi-foundry-demo"}


# Serve frontend static files if they exist
if FRONTEND_DIR.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend application."""
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """Serve SPA for any non-API routes."""
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return {"error": "Not found"}

        # Check if it's a static file
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Return index.html for SPA routing
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        """Root endpoint with demo information."""
        return {
            "name": "Nuraxi Foundry Demo Prototype",
            "version": "1.0.0",
            "organization": "King Faisal Specialist Hospital & Research Centre",
            "description": "Interactive demo showcasing clinical data transformation capabilities",
            "api_docs": "/api/docs",
            "demo_capabilities": [
                "Synthetic Saudi Patient Data Generation",
                "Cross-System Patient Linkage via Tokenization",
                "Safe Harbor + HiPS De-identification",
                "OMOP CDM v5.4 Transformation",
                "Research Cohort Queries",
                "AI Clinical Intelligence",
            ],
            "quick_start": "POST /api/demo/full-pipeline to run the complete demonstration",
        }
