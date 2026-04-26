from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from config.database import Base

class SensorReading(Base):
    """
    SQLAlchemy model for storing sensor telemetry data from ESP32 devices.
    Each reading contains temperature, humidity, gas levels, and a calculated mold risk score.
    """
    __tablename__ = 'sensor_readings'
    
    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)
    
    # FOREIGN KEY - Links to the Device table
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # SENSOR DATA FIELDS
    temperature = Column(Float, nullable=False, comment="Temperature in Celsius")
    humidity = Column(Float, nullable=False, comment="Relative humidity percentage")
    gas_reading = Column(Float, nullable=False, comment="Gas sensor reading (VOC/MQ level)")
    
    # CALCULATED RISK SCORE (0-100)
    risk_score = Column(Float, nullable=False, comment="Mold risk score calculated by risk engine")
    
    # TIMESTAMP WITH TIMEZONE AWARENESS
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # RELATIONSHIP - Links back to Device model
    device = relationship("Device", backref="sensor_readings")
    
    def __repr__(self):
        return f'<SensorReading {self.id} | Device {self.device_id} | Risk {self.risk_score:.2f}>'
        
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': round(self.temperature, 2),
            'humidity': round(self.humidity, 2),
            'gas_reading': round(self.gas_reading, 2),
            'risk_score': round(self.risk_score, 2),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }