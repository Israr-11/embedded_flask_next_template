from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime, timedelta, timezone

from models.sensor_reading import SensorReading
from models.device import Device
from services.risk_engine import RiskEngine

class TelemetryService:
    """
    Service for handling sensor telemetry data ingestion, storage, and retrieval.
    Coordinates with RiskEngine for mold risk calculation.
    """
    
    def __init__(self):
        self.risk_engine = RiskEngine()
    
    def ingest_reading(
        self, 
        db: Session, 
        device_id: int, 
        temperature: float, 
        humidity: float, 
        gas_reading: float
    ) -> Tuple[Optional[SensorReading], Optional[str], bool]:
        """
        Ingest a new sensor reading from ESP32, calculate risk, and store in database.
        
        Args:
            db: Database session
            device_id: ID of the device sending data
            temperature: Temperature reading in Celsius
            humidity: Humidity reading in percentage
            gas_reading: Gas sensor reading (VOC level)
            
        Returns:
            Tuple containing:
            - SensorReading object (or None if error)
            - Error message (or None if success)
            - Boolean indicating if alarm should be triggered (risk > 80)
        """
        # STEP 1: Validate that the device exists
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            return None, f"Device with ID {device_id} not found", False
        
        # STEP 2: Calculate mold risk score using the risk engine
        risk_score = self.risk_engine.calculate_mold_risk(temperature, humidity, gas_reading)
        
        # STEP 3: Create new sensor reading record
        reading = SensorReading(
            device_id=device_id,
            temperature=temperature,
            humidity=humidity,
            gas_reading=gas_reading,
            risk_score=risk_score,
            timestamp=datetime.now(timezone.utc)
        )
        
        # STEP 4: Save to database
        db.add(reading)
        db.commit()
        db.refresh(reading)
        
        # STEP 5: Determine if alarm should be triggered
        trigger_alarm = risk_score > 80.0
        
        return reading, None, trigger_alarm
    
    def get_latest_reading(self, db: Session, device_id: int) -> Optional[SensorReading]:
        """
        Get the most recent sensor reading for a specific device.
        
        Args:
            db: Database session
            device_id: ID of the device
            
        Returns:
            SensorReading object or None if no readings exist
        """
        return db.query(SensorReading)\
            .filter(SensorReading.device_id == device_id)\
            .order_by(SensorReading.timestamp.desc())\
            .first()
    
    def get_reading_history(
        self, 
        db: Session, 
        device_id: int, 
        limit: int = 100,
        hours: Optional[int] = None
    ) -> Dict[str, List]:
        """
        Get historical sensor readings formatted for frontend charts (Chart.js format).
        Implements down-sampling to limit response size.
        
        Args:
            db: Database session
            device_id: ID of the device
            limit: Maximum number of data points to return (default: 100)
            hours: Optional time window in hours (e.g., last 24 hours)
            
        Returns:
            Dictionary with 'labels' (timestamps) and 'datasets' (sensor values)
        """
        # STEP 1: Build query with optional time filter
        query = db.query(SensorReading).filter(SensorReading.device_id == device_id)
        
        if hours:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            query = query.filter(SensorReading.timestamp >= cutoff_time)
        
        # STEP 2: Get readings ordered by timestamp (oldest first for chart display)
        readings = query.order_by(SensorReading.timestamp.asc()).all()
        
        # STEP 3: Down-sample if we have more readings than the limit
        if len(readings) > limit:
            # Calculate step size for uniform sampling
            step = len(readings) // limit
            readings = readings[::step][:limit]
        
        # STEP 4: Format data for Chart.js
        labels = []
        temperature_data = []
        humidity_data = []
        gas_data = []
        risk_data = []
        
        for reading in readings:
            # Format timestamp for display (e.g., "2024-04-26 14:30")
            labels.append(reading.timestamp.strftime('%Y-%m-%d %H:%M'))
            temperature_data.append(round(reading.temperature, 2))
            humidity_data.append(round(reading.humidity, 2))
            gas_data.append(round(reading.gas_reading, 2))
            risk_data.append(round(reading.risk_score, 2))
        
        # STEP 5: Return in Chart.js datasets format
        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Temperature (°C)",
                    "data": temperature_data,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.1)",
                    "yAxisID": "y-temp"
                },
                {
                    "label": "Humidity (%)",
                    "data": humidity_data,
                    "borderColor": "rgb(54, 162, 235)",
                    "backgroundColor": "rgba(54, 162, 235, 0.1)",
                    "yAxisID": "y-humidity"
                },
                {
                    "label": "Gas Reading",
                    "data": gas_data,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)",
                    "yAxisID": "y-gas"
                },
                {
                    "label": "Risk Score",
                    "data": risk_data,
                    "borderColor": "rgb(255, 159, 64)",
                    "backgroundColor": "rgba(255, 159, 64, 0.1)",
                    "yAxisID": "y-risk",
                    "borderWidth": 3
                }
            ]
        }
    
    def get_statistics(self, db: Session, device_id: int, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate statistical summary for a device over a time period.
        
        Args:
            db: Database session
            device_id: ID of the device
            hours: Time window in hours (default: 24)
            
        Returns:
            Dictionary with min, max, avg values for each sensor
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        readings = db.query(SensorReading)\
            .filter(SensorReading.device_id == device_id)\
            .filter(SensorReading.timestamp >= cutoff_time)\
            .all()
        
        if not readings:
            return {
                "count": 0,
                "message": "No data available for this period"
            }
        
        # Calculate statistics
        temps = [r.temperature for r in readings]
        humidities = [r.humidity for r in readings]
        gases = [r.gas_reading for r in readings]
        risks = [r.risk_score for r in readings]
        
        return {
            "count": len(readings),
            "period_hours": hours,
            "temperature": {
                "min": round(min(temps), 2),
                "max": round(max(temps), 2),
                "avg": round(sum(temps) / len(temps), 2)
            },
            "humidity": {
                "min": round(min(humidities), 2),
                "max": round(max(humidities), 2),
                "avg": round(sum(humidities) / len(humidities), 2)
            },
            "gas_reading": {
                "min": round(min(gases), 2),
                "max": round(max(gases), 2),
                "avg": round(sum(gases) / len(gases), 2)
            },
            "risk_score": {
                "min": round(min(risks), 2),
                "max": round(max(risks), 2),
                "avg": round(sum(risks) / len(risks), 2),
                "current": round(risks[-1], 2)
            }
        }