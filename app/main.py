"""
TaxMate Backend Application
FastAPI application with organized API routers for tax filing automation.
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add app to path so we can import modules
current_dir = Path(__file__).resolve().parent
if str(current_dir.parent) not in sys.path:
    sys.path.append(str(current_dir.parent))

# Import routers
from app.api import orchestrator_component, form_extraction_component, chat_component

# Initialize FastAPI app
app = FastAPI(
    title="TaxMate API",
    description="Tax filing automation and advisory system",
    version="1.0.0"
)

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orchestrator_component.router)
app.include_router(form_extraction_component.router)
app.include_router(chat_component.router)

# Import and include filing router
from app.api import filing_routes
app.include_router(filing_routes.router)

# Import and include auth router
from app.api import auth_routes
app.include_router(auth_routes.router)



@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "TaxMate API",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
