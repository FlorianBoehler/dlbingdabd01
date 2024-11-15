import datetime
import random
import time
import requests
from requests.exceptions import RequestException
import urllib3
urllib3.disable_warnings()
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()

# Get Splunk token from environment variables
token_secret = os.getenv("SPLUNK_TOKEN")

class TemperatureLogGenerator:
    """
    Generates and sends simulated temperature logs for multiple machines to Splunk.
    Simulates realistic temperature fluctuations with momentum and randomization.
    """
    
    def __init__(self,
                 splunk_host="localhost",
                 splunk_port=8088,
                 splunk_token="SPLUNK_TOKEN_HERE",
                 num_machines=5,
                 min_temperature=60,
                 max_temperatur=80,
                 locations=["Hall_A", "Hall_B", "Hall_C"]):
        # Configure Splunk connection
        self.splunk_url = f"http://{splunk_host}:{splunk_port}/services/collector"
        self.headers = {
            "Authorization": f"Splunk {splunk_token}",
            "Content-Type": "application/json"
        }
        
        # Initialize machine configurations
        self.num_machines = num_machines
        self.locations = locations
        self.machines = [f"ROTOR_M{str(i+1).zfill(2)}" for i in range(num_machines)]
        self.batch_counter = 1000
        
        # Initialize temperature tracking for each machine
        self.last_temperatures = {machine: 70.0 for machine in self.machines}
        self.target_temps = {machine: random.uniform(min_temperature, max_temperatur) for machine in self.machines}
        self.temp_momentum = {machine: 0.0 for machine in self.machines}
        
    def get_status(self, temp):
        """Determine machine status based on temperature thresholds."""
        if temp <= 75.0:
            return "NORMAL"
        elif temp <= 85.0:
            return "WARNING"
        else:
            return "CRITICAL"

    def generate_temperature(self, machine, max_change=0.5):
        """
        Generate next temperature value using physics-inspired simulation.
        Includes momentum, damping, and random fluctuations.
        """
        last_temp = self.last_temperatures[machine]
        target_temp = self.target_temps[machine]
        
        # Apply damping to reduce oscillations
        damping = 0.8
        
        # Calculate temperature change using momentum
        temp_diff = target_temp - last_temp
        self.temp_momentum[machine] = (self.temp_momentum[machine] * damping + 
                                     temp_diff * 0.1)
        
        # Add random variations
        random_change = random.uniform(-max_change, max_change) * 0.3
        change = self.temp_momentum[machine] + random_change
        
        # 5% chance of temperature spike
        if random.random() < 0.05:
            change += random.uniform(1, 2)
            
        # Apply changes and enforce temperature bounds
        new_temp = round(last_temp + change, 2)
        new_temp = max(min(new_temp, 95.0), 65.0)
        self.last_temperatures[machine] = new_temp
        return new_temp

    def send_to_splunk(self, event):
        """Send event data to Splunk HEC endpoint."""
        data = {
            "event": event,
            "sourcetype": "_json",
            "index": "main"
        }
        try:
            response = requests.post(
                self.splunk_url,
                headers=self.headers,
                json=data,
                verify=False
            )
            if response.status_code != 200:
                print(f"Error sending data: Status {response.status_code}")
                print(f"Response: {response.text}")
            return response.status_code == 200
        except RequestException as e:
            print(f"Connection error: {e}")
            return False

    def generate_continuous_logs(self):
        """
        Main loop for generating and sending temperature logs.
        Runs until interrupted with Ctrl+C.
        """
        print("Starting data generation... (Press Ctrl+C to stop)")
        events_sent = 0
        try:
            while True:
                current_time = datetime.datetime.now()
                for machine in self.machines:
                    # Generate and send log entry for each machine
                    temperature = self.generate_temperature(machine)
                    log_entry = {
                        "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                        "machine": machine,
                        "temperature": temperature,
                        "status": self.get_status(temperature),
                        "location": random.choice(self.locations),
                        "batch_id": f"BATCH_{self.batch_counter}"
                    }
                    if self.send_to_splunk(log_entry):
                        events_sent += 1
                    if events_sent % 50 == 0:
                        print(f"Successfully sent: {events_sent} events")
                        
                # 1% chance to increment batch counter
                if random.random() < 0.01:
                    self.batch_counter += 1
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nProgram ended. Total events sent: {events_sent}")

# Example usage
if __name__ == "__main__":
   generator = TemperatureLogGenerator(
       splunk_host="localhost",
       splunk_port=8088,
       splunk_token=token_secret,
       min_temperature=60,
       max_temperatur=80
   )
   generator.generate_continuous_logs()
