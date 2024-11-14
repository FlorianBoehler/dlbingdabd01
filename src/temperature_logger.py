import datetime
import random
import time
import json
from pathlib import Path

class TemperatureLogGenerator:
    def __init__(self, num_machines=5, locations=["Hall_A", "Hall_B", "Hall_C"]):
        self.num_machines = num_machines
        self.locations = locations
        self.machines = [f"ROTOR_M{str(i+1).zfill(2)}" for i in range(num_machines)]
        self.batch_counter = 1000
        
    def get_status(self, temp):
        """Determine machine status based on temperature"""
        if temp <= 75.0:
            return "NORMAL"
        elif temp <= 85.0:
            return "WARNING"
        else:
            return "CRITICAL"
    
    def generate_temperature(self, base_temp=70.0, variation=15.0):
        """Generate a realistic temperature value with some random variation"""
        # Adding some randomness and occasional spikes
        temp = base_temp + random.gauss(0, variation/3)
        
        # Occasionally generate temperature spikes
        if random.random() < 0.05:  # 5% chance of a spike
            temp += random.uniform(10, 20)
            
        return round(temp, 2)
    
    def generate_log_entry(self, timestamp=None):
        """Generate a single log entry"""
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        machine = random.choice(self.machines)
        temperature = self.generate_temperature()
        status = self.get_status(temperature)
        location = random.choice(self.locations)
        
        return {
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
            "machine": machine,
            "temperature": temperature,
            "status": status,
            "location": location,
            "batch_id": f"BATCH_{self.batch_counter}"
        }
    
    def generate_logs(self, duration_seconds=60, interval_ms=1000):
        """Generate logs for a specified duration with given interval"""
        output_dir = Path("logs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"temperature_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        start_time = time.time()
        records_written = 0
        
        with open(output_file, "w") as f:
            while time.time() - start_time < duration_seconds:
                timestamp = datetime.datetime.now()
                
                # Generate log entry for each machine
                for machine in self.machines:
                    log_entry = self.generate_log_entry(timestamp)
                    f.write(json.dumps(log_entry) + "\n")
                    records_written += 1
                
                # Update batch counter occasionally
                if random.random() < 0.01:  # 1% chance to change batch
                    self.batch_counter += 1
                
                # Wait for next interval
                time.sleep(interval_ms / 1000)
        
        return records_written, output_file

# Usage example
if __name__ == "__main__":
    # Initialize generator with 5 machines
    generator = TemperatureLogGenerator(num_machines=5)
    
    # Generate logs for 5 minutes with readings every second
    records, logfile = generator.generate_logs(duration_seconds=300, interval_ms=1000)
    
    print(f"Generated {records} log entries in {logfile}")