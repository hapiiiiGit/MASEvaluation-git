import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import router as api_router
from backend.auth.facebook_oauth import router as facebook_oauth_router
from backend.auth.hubspot_oauth import router as hubspot_oauth_router
from backend.sync.scheduler import scheduler_start

app = FastAPI(
    title="Facebook-HubSpot Sync API",
    description="Backend API for securely syncing Facebook Marketing API ad metrics to HubSpot CRM and providing dashboard data.",
    version="1.0.0"
)

# CORS settings for frontend dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(facebook_oauth_router, prefix="/auth/facebook", tags=["Facebook OAuth"])
app.include_router(hubspot_oauth_router, prefix="/auth/hubspot", tags=["HubSpot OAuth"])
app.include_router(api_router, prefix="/api", tags=["API"])

# Start the sync scheduler on startup
@app.on_event("startup")
async def startup_event():
    scheduler_start()

@app.get("/")
async def root():
    return {"message": "Facebook-HubSpot Sync API is running."}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)