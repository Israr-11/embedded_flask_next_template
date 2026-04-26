from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from services.telemetry_service import TelemetryService
from services.risk_engine import RiskEngine
from schemas.sensor_reading_schema import ReadingCreate, ReadingResponse

class TelemetryController:
    """
    Controller for handling telemetry-related HTTP requests.
    Coordinates between routes and telemetry service.
    """
    
    def __init__(self):
        self.telemetry_service = TelemetryService()
        self.risk_engine = RiskEngine()
    
    async def ingest_telemetry(
        self, 
        reading_data: ReadingCreate,
        db: Session
    ):
        """
        Handle POST /telemetry endpoint - Ingest sensor data from ESP32.
        
        Args:
            reading_data: Sensor reading from ESP32
            db: Database session
            
        Returns:
            Dictionary with reading data and alarm status
        """
        # INGEST READING USING SERVICE
        reading, error, trigger_alarm = self.telemetry_service.ingest_reading(
            db=db,
            device_id=reading_data.device_id,
            temperature=reading_data.temperature,
            humidity=reading_data.humidity,
            gas_reading=reading_data.gas_reading
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error
            )
        
        # GET RISK LEVEL AND COLOR
        risk_level, color = self.risk_engine.get_risk_level(reading.risk_score)
        
        # PREPARE RESPONSE
        response = {
            "message": "Telemetry data received successfully",
            "reading": reading.to_dict(),
            "risk_level": risk_level,
            "risk_color": color,
            "alarm_triggered": trigger_alarm
        }
        
        # ADD ALARM COMMAND IF RISK IS HIGH
        if trigger_alarm:
            response["mqtt_command"] = {
                "buzzer": "ALARM",
                "led": "RED",
                "message": f"CRITICAL: Mold risk at {reading.risk_score:.1f}%"
            }
        
        return response
    
    async def get_latest(
        self, 
        device_id: int,
        db: Session
    ):
        """
        Handle GET /telemetry/latest - Get most recent reading for a device.
        
        Args:
            device_id: ID of the device
            db: Database session
            
        Returns:
            Dictionary with latest reading and alert status
        """
        # GET LATEST READING
        reading = self.telemetry_service.get_latest_reading(db, device_id)
        
        if not reading:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No readings found for device {device_id}"
            )
        
        # GET RISK LEVEL
        risk_level, color = self.risk_engine.get_risk_level(reading.risk_score)
        
        # PREPARE ALERT MESSAGE IF NEEDED
        alert = None
        if reading.risk_score > 80:
            alert = f"CRITICAL: Mold risk is {risk_level}"
        elif reading.risk_score > 60:
            alert = f"WARNING: Mold risk is {risk_level}"
        
        return {
            "reading": reading.to_dict(),
            "risk_level": risk_level,
            "risk_color": color,
            "alert": alert
        }
    
    async def get_history(
        self, 
        device_id: int,
        hours: Optional[int],
        limit: int,
        db: Session
    ):
        """
        Handle GET /telemetry/history - Get historical data for charts.
        
        Args:
            device_id: ID of the device
            hours: Optional time window in hours
            limit: Maximum number of data points
            db: Database session
            
        Returns:
            Dictionary with chart-formatted data
        """
        # GET HISTORICAL DATA
        history = self.telemetry_service.get_reading_history(
            db=db,
            device_id=device_id,
            limit=limit,
            hours=hours
        )
        
        if not history['labels']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"No historical data found for device {device_id}"
            )
        
        return {
            "device_id": device_id,
            "data_points": len(history['labels']),
            "chart_data": history
        }
    
    async def get_statistics(
        self, 
        device_id: int,
        hours: int,
        db: Session
    ):
        """
        Handle GET /telemetry/statistics - Get statistical summary.
        
        Args:
            device_id: ID of the device
            hours: Time window in hours
            db: Database session
            
        Returns:
            Dictionary with statistical data
        """
        stats = self.telemetry_service.get_statistics(db, device_id, hours)
        
        return {
            "device_id": device_id,
            "statistics": stats
        }