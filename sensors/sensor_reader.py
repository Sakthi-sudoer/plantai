import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
from statistics import mean

class SensorReader:
    def __init__(self):
        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Pin configurations
        self.MOISTURE_PIN = 17  # GPIO pin for soil moisture sensor
        self.LDR_PIN = 18      # GPIO pin for LDR sensor
        self.DHT_PIN = 4       # GPIO pin for DHT11 sensor
        
        # Initialize DHT11
        self.dht = adafruit_dht.DHT11(board.D4)  # Using GPIO4
        
        # Setup for moisture sensor (analog)
        GPIO.setup(self.MOISTURE_PIN, GPIO.IN)
        
        # Setup for LDR (using RC circuit)
        GPIO.setup(self.LDR_PIN, GPIO.IN)
        
    def read_moisture(self, num_samples=5):
        """
        Read soil moisture sensor with multiple samples to improve accuracy
        Returns percentage (0-100), where 0 is dry and 100 is very wet
        """
        try:
            readings = []
            for _ in range(num_samples):
                # Read digital value
                reading = GPIO.input(self.MOISTURE_PIN)
                readings.append(reading)
                time.sleep(0.1)
            
            # Convert to percentage (inverted as sensor reads LOW when wet)
            moisture = (1 - mean(readings)) * 100
            return round(moisture, 1)
        except Exception as e:
            print(f"Error reading moisture: {e}")
            return None

    def read_light(self, num_samples=5):
        """
        Read LDR sensor using RC circuit method
        Returns percentage (0-100), where 0 is dark and 100 is bright
        """
        try:
            readings = []
            for _ in range(num_samples):
                # Discharge capacitor
                GPIO.setup(self.LDR_PIN, GPIO.OUT)
                GPIO.output(self.LDR_PIN, GPIO.LOW)
                time.sleep(0.1)
                
                # Count time to charge
                GPIO.setup(self.LDR_PIN, GPIO.IN)
                count = 0
                while GPIO.input(self.LDR_PIN) == GPIO.LOW and count < 1000:
                    count += 1
                
                # Convert count to percentage (inverted)
                reading = ((1000 - count) / 1000) * 100
                readings.append(reading)
                
            return round(mean(readings), 1)
        except Exception as e:
            print(f"Error reading light: {e}")
            return None

    def read_temperature_humidity(self, retries=3):
        """
        Read temperature and humidity from DHT11
        Returns tuple (temperature, humidity) or (None, None) on failure
        """
        for _ in range(retries):
            try:
                temperature = self.dht.temperature
                humidity = self.dht.humidity
                return round(temperature, 1), round(humidity, 1)
            except Exception as e:
                print(f"Error reading DHT11: {e}")
                time.sleep(2)  # DHT11 needs 2 seconds between readings
        return None, None

    def read_all_sensors(self):
        """
        Read all sensors and return their values
        """
        moisture = self.read_moisture()
        light = self.read_light()
        temperature, humidity = self.read_temperature_humidity()
        
        return {
            'moisture': moisture,
            'light': light,
            'temperature': temperature,
            'humidity': humidity
        }

    def cleanup(self):
        """
        Clean up GPIO pins
        """
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    sensor = SensorReader()
    try:
        while True:
            readings = sensor.read_all_sensors()
            print(f"""
Sensor Readings:
---------------
Moisture: {readings['moisture']}%
Light: {readings['light']}%
Temperature: {readings['temperature']}°C
Humidity: {readings['humidity']}%
            """)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping sensor readings...")
    finally:
        sensor.cleanup()
