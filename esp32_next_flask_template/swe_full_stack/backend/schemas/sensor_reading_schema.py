from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ReadingBase(BaseModel):
    """Base schema with common sensor reading fields"""
    temperature: float = Field(..., ge=-40, le=85, description="Temperature in Celsius (-40 to 85°C)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity percentage (0-100%)")
    gas_reading: float = Field(..., ge=0, description="Gas sensor reading (PPM or analog value)")

class ReadingCreate(ReadingBase):
    """
    Schema for incoming sensor data from ESP32.
    This is what the hardware sends via POST /telemetry
    """
    device_id: int = Field(..., gt=0, description="ID of the device sending the data")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """Ensure temperature is within realistic bounds"""
        if v < -40 or v > 85:
            raise ValueError('Temperature must be between -40°C and 85°C')
        return round(v, 2)
    
    @validator('humidity')
    def validate_humidity(cls, v):
        """Ensure humidity is within valid percentage range"""
        if v < 0 or v > 100:
            raise ValueError('Humidity must be between 0% and 100%')
        return round(v, 2)

class ReadingResponse(ReadingBase):
    """
    Schema for sending sensor data to the frontend.
    Includes calculated risk score and timestamp.
    """
    id: int
    device_id: int
    risk_score: float = Field(..., ge=0, le=100, description="Calculated mold risk score (0-100)")
    timestamp: datetime
    
    class Config:
        orm_mode = True

class ReadingHistoryResponse(BaseModel):
    """
    Schema for time-series chart data.
    Follows Chart.js format with labels and datasets.
    """
    labels: list = Field(..., description="Array of timestamp strings for X-axis")
    datasets: list = Field(..., description="Array of dataset objects containing sensor values")
    
class LatestReadingResponse(BaseModel):
    """Schema for the most recent sensor reading"""
    reading: ReadingResponse
    alert: Optional[str] = Field(None, description="Alert message if risk score is high")