import random
import time
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from config.database import SessionLocal
from services.telemetry_service import TelemetryService

class SensorSimulator:
    """
    Dummy data generator for testing the frontend without physical ESP32 hardware.
    Generates realistic sensor readings using a "random walk" algorithm.
    """
    
    def __init__(self, device_id: int = 1):
        """
        Initialize the simulator.
        
        Args:
            device_id: ID of the device to simulate (must exist in database)
        """
        self.device_id = device_id
        self.telemetry_service = TelemetryService()
        
        # INITIAL STATE (starting values for random walk)
        self.current_temp = 22.0      # Start at 22°C
        self.current_humidity = 65.0  # Start at 65% (moderate risk zone)
        self.current_gas = 400.0      # Start at 400 PPM
        
        # RANDOM WALK PARAMETERS
        self.temp_step = 0.5          # Max temperature change per step
        self.humidity_step = 2.0      # Max humidity change per step
        self.gas_step = 50.0          # Max gas reading change per step
        
        # BOUNDS TO KEEP VALUES REALISTIC
        self.temp_min = 18.0
        self.temp_max = 28.0
        self.humidity_min = 45.0
        self.humidity_max = 85.0
        self.gas_min = 200.0
        self.gas_max = 800.0
    
    def _random_walk(self, current: float, step_size: float, min_val: float, max_val: float) -> float:
        """
        Generate next value using random walk algorithm.
        
        Args:
            current: Current value
            step_size: Maximum change per step
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Next value in the random walk
        """
        # Random change: can go up or down
        change = random.uniform(-step_size, step_size)
        new_value = current + change
        
        # Keep within bounds
        new_value = max(min_val, min(max_val, new_value))
        
        return new_value
    
    def generate_reading(self) -> dict:
        """
        Generate one simulated sensor reading using random walk.
        
        Returns:
            Dictionary with temperature, humidity, and gas_reading
        """
        # UPDATE VALUES USING RANDOM WALK
        self.current_temp = self._random_walk(
            self.current_temp, 
            self.temp_step, 
            self.temp_min, 
            self.temp_max
        )
        
        self.current_humidity = self._random_walk(
            self.current_humidity, 
            self.humidity_step, 
            self.humidity_min, 
            self.humidity_max
        )
        
        self.current_gas = self._random_walk(
            self.current_gas, 
            self.gas_step, 
            self.gas_min, 
            self.gas_max
        )
        
        # OCCASIONALLY INJECT ANOMALIES (10% chance)
        if random.random() < 0.1:
            # Spike in one parameter to simulate real-world events
            anomaly_type = random.choice(['temp', 'humidity', 'gas'])
            if anomaly_type == 'temp':
                self.current_temp += random.uniform(1, 3)
            elif anomaly_type == 'humidity':
                self.current_humidity += random.uniform(5, 15)
            else:
                self.current_gas += random.uniform(100, 300)
        
        return {
            "temperature": round(self.current_temp, 2),
            "humidity": round(self.current_humidity, 2),
            "gas_reading": round(self.current_gas, 2)
        }
    
    async def run_simulation(self, interval_seconds: int = 10):
        """
        Run continuous simulation in the background.
        Generates and stores readings every N seconds.
        
        Args:
            interval_seconds: Time between readings (default: 10 seconds)
        """
        print(f"Simulator started for device {self.device_id}")
        print(f"Generating readings every {interval_seconds} seconds...")
        
        while True:
            try:
                # CREATE DATABASE SESSION
                db = SessionLocal()
                
                # GENERATE SIMULATED READING
                reading_data = self.generate_reading()
                
                # INGEST READING USING TELEMETRY SERVICE
                reading, error, trigger_alarm = self.telemetry_service.ingest_reading(
                    db=db,
                    device_id=self.device_id,
                    temperature=reading_data['temperature'],
                    humidity=reading_data['humidity'],
                    gas_reading=reading_data['gas_reading']
                )
                
                if error:
                    print(f"Error: {error}")
                else:
                    print(f"Reading #{reading.id} | Temp: {reading.temperature}°C | "
                          f"Humidity: {reading.humidity}% | Risk: {reading.risk_score:.1f}")
                    
                    if trigger_alarm:
                        print(f"ALARM TRIGGERED! Risk score: {reading.risk_score:.1f}")
                
                # CLOSE DATABASE SESSION
                db.close()
                
                # WAIT FOR NEXT INTERVAL
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Simulator error: {str(e)}")
                await asyncio.sleep(interval_seconds)

# HELPER FUNCTION TO START SIMULATOR AS BACKGROUND TASK
def start_simulator_background(device_id: int = 1, interval: int = 10):
    """
    Start the simulator as a background task in FastAPI.
    Call this from app.py using @app.on_event("startup")
    
    Args:
        device_id: Device ID to simulate
        interval: Seconds between readings
    """
    simulator = SensorSimulator(device_id=device_id)
    asyncio.create_task(simulator.run_simulation(interval_seconds=interval))