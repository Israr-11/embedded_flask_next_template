from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import asyncio

from config.database import get_db
from controllers.telemetry_controller import TelemetryController
from schemas.sensor_reading_schema import ReadingCreate, ReadingResponse

router = APIRouter()
telemetry_controller = TelemetryController()

# ======================
# WEBSOCKET CONNECTION MANAGER
# ======================
class ConnectionManager:
    """
    Manages WebSocket connections for real-time telemetry broadcasting.
    Allows multiple frontend clients to receive live sensor updates.
    """
    def __init__(self):
        # List of active WebSocket connections
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Dictionary to send (will be converted to JSON)
        """
        # Remove dead connections
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)
        
        # Clean up dead connections
        for dead in dead_connections:
            self.active_connections.remove(dead)

# GLOBAL CONNECTION MANAGER INSTANCE
manager = ConnectionManager()


# ======================
# HTTP ENDPOINTS
# ======================

@router.post("/telemetry", response_model=dict)
async def ingest_telemetry(
    reading_data: ReadingCreate, 
    db: Session = Depends(get_db)
):
    """
    **ESP32 Telemetry Ingestion Endpoint**
    
    This endpoint receives sensor data from ESP32 devices, calculates mold risk,
    and stores the reading in the database.
    
    **Request Body:**
    ```json
    {
        "device_id": 1,
        "temperature": 24.5,
        "humidity": 68.2,
        "gas_reading": 520.0
    }
    ```
    
    **Response:**
    - Returns calculated risk score and alarm status
    - If risk > 80, includes MQTT command to trigger buzzer
    - Broadcasts reading to all connected WebSocket clients
    """
    # INGEST DATA
    response = await telemetry_controller.ingest_telemetry(reading_data, db)
    
    # BROADCAST TO WEBSOCKET CLIENTS
    await manager.broadcast({
        "type": "new_reading",
        "data": response['reading'],
        "risk_level": response['risk_level'],
        "alarm_triggered": response['alarm_triggered']
    })
    
    return response


@router.get("/telemetry/latest", response_model=dict)
async def get_latest_reading(
    device_id: int = Query(..., description="ID of the device", gt=0),
    db: Session = Depends(get_db)
):
    """
    **Get Latest Sensor Reading**
    
    Returns the most recent sensor reading for a specific device.
    Useful for dashboard displays and current status checks.
    
    **Query Parameters:**
    - `device_id`: ID of the device (required)
    
    **Example:**
    ```
    GET /telemetry/latest?device_id=1
    ```
    """
    return await telemetry_controller.get_latest(device_id, db)


@router.get("/telemetry/history", response_model=dict)
async def get_reading_history(
    device_id: int = Query(..., description="ID of the device", gt=0),
    hours: Optional[int] = Query(None, description="Time window in hours (e.g., 24 for last day)", gt=0),
    limit: int = Query(100, description="Maximum number of data points", gt=0, le=500),
    db: Session = Depends(get_db)
):
    """
    **Get Historical Sensor Data for Charts**
    
    Returns time-series data formatted for Chart.js or other charting libraries.
    Includes down-sampling to limit response size.
    
    **Query Parameters:**
    - `device_id`: ID of the device (required)
    - `hours`: Optional time window (e.g., 24 for last 24 hours)
    - `limit`: Maximum data points to return (default: 100, max: 500)
    
    **Response Format:**
    ```json
    {
        "chart_data": {
            "labels": ["2024-04-26 10:00", "2024-04-26 10:10", ...],
            "datasets": [
                {"label": "Temperature", "data": [22.5, 22.8, ...]},
                {"label": "Humidity", "data": [65.2, 66.1, ...]},
                ...
            ]
        }
    }
    ```
    """
    return await telemetry_controller.get_history(device_id, hours, limit, db)


@router.get("/telemetry/statistics", response_model=dict)
async def get_statistics(
    device_id: int = Query(..., description="ID of the device", gt=0),
    hours: int = Query(24, description="Time window in hours", gt=0, le=720),
    db: Session = Depends(get_db)
):
    """
    **Get Statistical Summary**
    
    Returns min, max, and average values for all sensor readings over a time period.
    
    **Query Parameters:**
    - `device_id`: ID of the device (required)
    - `hours`: Time window in hours (default: 24, max: 720)
    """
    return await telemetry_controller.get_statistics(device_id, hours, db)


# ======================
# WEBSOCKET ENDPOINT
# ======================

@router.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """
    **Real-Time Telemetry WebSocket**
    
    Establishes a WebSocket connection for receiving live sensor updates.
    Frontend clients can connect to this endpoint to get real-time data.
    
    **Usage in Frontend (JavaScript):**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/ws/telemetry');
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('New reading:', data);
        // Update your UI here
    };
    ```
    
    **Message Format:**
    ```json
    {
        "type": "new_reading",
        "data": {
            "temperature": 24.5,
            "humidity": 68.2,
            "risk_score": 72.5
        },
        "risk_level": "HIGH",
        "alarm_triggered": false
    }
    ```
    """
    await manager.connect(websocket)
    
    try:
        # KEEP CONNECTION ALIVE
        while True:
            # Wait for messages from client (ping/pong for keep-alive)
            data = await websocket.receive_text()
            
            # Echo back to confirm connection
            await websocket.send_json({
                "type": "pong",
                "message": "Connection active"
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)