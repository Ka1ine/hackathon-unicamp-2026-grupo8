import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.api.routes import router as monitoring_router

# Initialize the main FastAPI application
app = FastAPI(title="Enter AI Legal Engine - Case Progression API")

# Configure Cross-Origin Resource Sharing (CORS) for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"],
)

# Register application routers
app.include_router(monitoring_router)


@app.get("/", include_in_schema=False)
def root():
    """Redirects root endpoint traffic to the interactive Swagger UI documentation."""
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    # Launch the ASGI server
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
