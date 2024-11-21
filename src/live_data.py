import datetime
import random
import time
import requests
from requests.exceptions import RequestException
import urllib3
urllib3.disable_warnings()
import dotenv
import os

dotenv.load_dotenv()
token_secret = os.getenv("SPLUNK_TOKEN")

class TemperatureLogGenerator:
    def __init__(self,
                 splunk_host="localhost",
                 splunk_port=8088,
                 splunk_token="SPLUNK_TOKEN_HERE",
                 num_points=5,
                 min_temperature=60,
                 max_temperatur=95):
        self.splunk_url = f"http://{splunk_host}:{splunk_port}/services/collector"
        self.headers = {
            "Authorization": f"Splunk {splunk_token}",
            "Content-Type": "application/json"
        }
        
        self.num_points = num_points
        self.measurement_points = [f"ROTOR_M{str(i+1).zfill(2)}" for i in range(num_points)]
        self.batch_counter = 1000
        
        self.last_temperatures = {point: 70.0 for point in self.measurement_points}
        self.target_temps = {point: random.uniform(min_temperature, max_temperatur) for point in self.measurement_points}
        self.temp_momentum = {point: 0.0 for point in self.measurement_points}
        
    def get_status(self, temp):
        if temp <= 75.0:
            return "NORMAL"
        elif temp <= 85.0:
            return "WARNING"
        else:
            return "CRITICAL"

    def generate_temperature(self, point, max_change=0.5):
        last_temp = self.last_temperatures[point]
        target_temp = self.target_temps[point]
        
        damping = 0.8
        temp_diff = target_temp - last_temp
        self.temp_momentum[point] = (self.temp_momentum[point] * damping + 
                                   temp_diff * 0.1)
        
        random_change = random.uniform(-max_change, max_change) * 0.3
        change = self.temp_momentum[point] + random_change
        
        if random.random() < 0.05:
            change += random.uniform(1, 2)
            
        new_temp = round(last_temp + change, 2)
        new_temp = max(min(new_temp, 95), 60.0)
        self.last_temperatures[point] = new_temp
        return new_temp

    def send_to_splunk(self, event):
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
        print("Starting data generation... (Press Ctrl+C to stop)")
        events_sent = 0
        try:
            while True:
                current_time = datetime.datetime.now()
                for point in self.measurement_points:
                    temperature = self.generate_temperature(point)
                    log_entry = {
                        "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                        "measurement_point": point,
                        "temperature": temperature,
                        "status": self.get_status(temperature),
                        "batch_id": f"BATCH_{self.batch_counter}"
                    }
                    if self.send_to_splunk(log_entry):
                        events_sent += 1
                    if events_sent % 50 == 0:
                        print(f"Successfully sent: {events_sent} events")
                        
                if random.random() < 0.01:
                    self.batch_counter += 1
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\nProgram ended. Total events sent: {events_sent}")

if __name__ == "__main__":
   generator = TemperatureLogGenerator(
       splunk_host="localhost",
       splunk_port=8088,
       splunk_token=token_secret,
       min_temperature=60,
       max_temperatur=80
   )
   generator.generate_continuous_logs()