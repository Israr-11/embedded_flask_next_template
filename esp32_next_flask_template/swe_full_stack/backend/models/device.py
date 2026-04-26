from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

from config.database import Base

class Device(Base):
    """
    SQLAlchemy model for ESP32 mold detector devices.
    Represents physical ESP32 hardware units that send sensor data.
    """
    __tablename__ = 'devices'
    
    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)
    
    # DEVICE IDENTIFICATION
    device_uid = Column(String(255), unique=True, nullable=False, comment="Unique hardware identifier (MAC address or custom ID)")
    name = Column(String(255), nullable=False, comment="Friendly name (e.g., 'Living Room Sensor')")
    location = Column(String(255), nullable=True, comment="Physical location of the device")
    
    # DEVICE STATUS
    is_active = Column(Boolean, default=True, comment="Whether device is currently active")
    
    # METADATA
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=True, comment="Last time device sent data")
    
    def __repr__(self):
        return f'<Device {self.name} ({self.device_uid})>'
        
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'device_uid': self.device_uid,
            'name': self.name,
            'location': self.location,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }