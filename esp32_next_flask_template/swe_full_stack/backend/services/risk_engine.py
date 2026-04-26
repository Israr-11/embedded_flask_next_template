import math
from typing import Tuple

class RiskEngine:
    """
    Mold Risk Calculation Engine based on Environmental Engineering principles.
    Uses weighted factors for temperature, humidity, and air quality (gas readings).
    
    Risk Scoring Logic:
    - Humidity is the PRIMARY factor (weight: 50%)
    - Temperature is SECONDARY factor (weight: 30%)
    - Gas reading (VOC) is TERTIARY factor (weight: 20%)
    
    Mold thrives in:
    - High humidity (>60%)
    - Moderate temps (20-30°C / 68-86°F)
    - Poor ventilation (high VOC levels)
    """
    
    # RISK THRESHOLDS
    HUMIDITY_CRITICAL = 70.0  # Above this, mold risk is very high
    HUMIDITY_WARNING = 60.0   # Above this, mold risk starts increasing
    TEMP_OPTIMAL_MIN = 20.0   # Mold growth optimal range start
    TEMP_OPTIMAL_MAX = 30.0   # Mold growth optimal range end
    GAS_WARNING = 500.0       # Arbitrary threshold for poor air quality
    
    # WEIGHTS (must sum to 1.0)
    WEIGHT_HUMIDITY = 0.50
    WEIGHT_TEMPERATURE = 0.30
    WEIGHT_GAS = 0.20
    
    @staticmethod
    def calculate_mold_risk(temperature: float, humidity: float, gas_reading: float) -> float:
        """
        Calculate mold risk score on a scale of 0-100.
        
        Args:
            temperature (float): Temperature in Celsius
            humidity (float): Relative humidity (0-100%)
            gas_reading (float): Gas sensor reading (VOC/MQ sensor value)
            
        Returns:
            float: Risk score between 0 (no risk) and 100 (extreme risk)
        """
        # STEP 1: Calculate humidity risk component (0-50 points)
        humidity_risk = RiskEngine._calculate_humidity_risk(humidity)
        
        # STEP 2: Calculate temperature risk component (0-30 points)
        temperature_risk = RiskEngine._calculate_temperature_risk(temperature)
        
        # STEP 3: Calculate gas risk component (0-20 points)
        gas_risk = RiskEngine._calculate_gas_risk(gas_reading)
        
        # STEP 4: Sum all components
        total_risk = humidity_risk + temperature_risk + gas_risk
        
        # STEP 5: Ensure score is within bounds [0, 100]
        return max(0.0, min(100.0, total_risk))
    
    @staticmethod
    def _calculate_humidity_risk(humidity: float) -> float:
        """
        Humidity risk calculation (exponential growth above 60%).
        
        Logic:
        - Below 40%: Minimal risk (0-5 points)
        - 40-60%: Low risk (5-15 points)
        - 60-70%: Moderate risk (15-35 points)
        - Above 70%: High risk (35-50 points)
        """
        if humidity < 40:
            # Very dry conditions - minimal mold risk
            return (humidity / 40) * 5
        elif humidity < RiskEngine.HUMIDITY_WARNING:
            # Comfortable range - low risk
            normalized = (humidity - 40) / 20
            return 5 + (normalized * 10)
        elif humidity < RiskEngine.HUMIDITY_CRITICAL:
            # Warning zone - risk increases rapidly
            normalized = (humidity - RiskEngine.HUMIDITY_WARNING) / 10
            return 15 + (normalized * 20)
        else:
            # Critical zone - exponential risk growth
            normalized = (humidity - RiskEngine.HUMIDITY_CRITICAL) / 30
            exponential_factor = math.exp(normalized * 2) - 1  # Exponential curve
            return 35 + min(15, exponential_factor * 10)
    
    @staticmethod
    def _calculate_temperature_risk(temperature: float) -> float:
        """
        Temperature risk calculation (peak risk at 20-30°C).
        
        Logic:
        - Below 15°C: Low risk (0-5 points)
        - 15-20°C: Moderate risk (5-20 points)
        - 20-30°C: OPTIMAL MOLD RANGE - High risk (20-30 points)
        - Above 30°C: Decreasing risk (10-20 points)
        """
        if temperature < 15:
            # Too cold for rapid mold growth
            return max(0, (temperature / 15) * 5)
        elif temperature < RiskEngine.TEMP_OPTIMAL_MIN:
            # Approaching optimal range
            normalized = (temperature - 15) / 5
            return 5 + (normalized * 15)
        elif temperature <= RiskEngine.TEMP_OPTIMAL_MAX:
            # OPTIMAL MOLD GROWTH RANGE - Maximum temperature risk
            normalized = (temperature - RiskEngine.TEMP_OPTIMAL_MIN) / 10
            return 20 + (normalized * 10)
        elif temperature < 35:
            # Above optimal range - risk decreases
            normalized = (temperature - RiskEngine.TEMP_OPTIMAL_MAX) / 5
            return 30 - (normalized * 10)
        else:
            # Too hot for most mold species
            return max(10, 30 - ((temperature - 35) * 2))
    
    @staticmethod
    def _calculate_gas_risk(gas_reading: float) -> float:
        """
        Gas reading risk calculation (higher VOC = poor ventilation).
        
        Logic:
        - Below 300: Good air quality (0-5 points)
        - 300-500: Moderate air quality (5-10 points)
        - Above 500: Poor air quality (10-20 points)
        """
        if gas_reading < 300:
            # Good ventilation
            return (gas_reading / 300) * 5
        elif gas_reading < RiskEngine.GAS_WARNING:
            # Moderate air quality
            normalized = (gas_reading - 300) / 200
            return 5 + (normalized * 5)
        else:
            # Poor ventilation - increases mold risk
            normalized = (gas_reading - RiskEngine.GAS_WARNING) / 1000
            return 10 + min(10, normalized * 10)
    
    @staticmethod
    def get_risk_level(risk_score: float) -> Tuple[str, str]:
        """
        Convert numeric risk score to categorical risk level with color coding.
        
        Returns:
            Tuple[str, str]: (risk_level, color_code)
        """
        if risk_score < 30:
            return ("LOW", "green")
        elif risk_score < 50:
            return ("MODERATE", "yellow")
        elif risk_score < 70:
            return ("HIGH", "orange")
        elif risk_score < 85:
            return ("VERY HIGH", "red")
        else:
            return ("CRITICAL", "darkred")