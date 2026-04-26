from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import telemetry_routes
from services.simulator import start_simulator_background
from config.database import engine, Base

# CREATE DATABASE TABLES
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IOTConnect - Mold Detector", 
    version="2.0.0",
    description="IoT Mold Detection System with Real-time Risk Analysis"
)

# CORS MIDDLEWARE (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INCLUDE ROUTES
app.include_router(telemetry_routes.router, prefix="/api", tags=["telemetry"])  # NEW

@app.get("/")
def read_root():
    return {
        "message": "IOTConnect Mold Detector API",
        "version": "2.0.0",
        "endpoints": {
            "telemetry_ingestion": "/api/telemetry",
            "latest_reading": "/api/telemetry/latest",
            "history": "/api/telemetry/history",
            "websocket": "/api/ws/telemetry",
            "docs": "/docs"
        }
    }

# STARTUP EVENT - Start simulator in background
@app.on_event("startup")
async def startup_event():
    """
    Start the sensor simulator when the application starts.
    This generates dummy data every 10 seconds for testing.
    
    NOTE: Comment this out when using real ESP32 hardware.
    """
    print("Starting sensor simulator...")
    start_simulator_background(device_id=1, interval=10)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)