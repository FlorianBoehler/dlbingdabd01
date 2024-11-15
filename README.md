# Temperature Monitoring System for RotorWind GmbH

Real-time temperature monitoring system for wind turbine rotor manufacturing machines, sending data directly to Splunk via HTTP Event Collector (HEC).

## Prerequisites

- Python 3.8+
- Splunk Enterprise/Cloud instance
- Splunk HTTP Event Collector (HEC) token

## Splunk HEC Token Setup

1. Log in to your Splunk instance as an admin
2. Navigate to Settings > Data Inputs > HTTP Event Collector
3. Click "New Token"
4. Configure the token:
   - Name: `temperature_monitor`
   - Source type: `_json`
   - App Context: Search & Reporting
   - Default Index: main
5. Click "Review" then "Submit"
6. Save the generated token value for use in `.env`
7. Enable HEC:
   - Go to Global Settings
   - Set "All Tokens" to Enabled
   - Set HTTP Port Number to 8088
   - Click "Save"

## Setup

1. Clone the repository:
```bash
git clone https://github.com/FlorianBoehler/dlbingdabd01.git
cd dlbingdabd01
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your Splunk token:
```bash
SPLUNK_TOKEN=your_hec_token_here
```

## Configuration

Edit the following parameters in `temperature_logger.py`:
- `splunk_host`: Splunk instance hostname/IP
- `splunk_port`: HEC port (default: 8088)
- `num_machines`: Number of machines to monitor
- `locations`: List of facility locations
- `min_temperature`: Define the minimal temperature (Default:60)
- `max_temperatur`: Define the maximum temperature (Default:80)
- Temperature thresholds and ranges

## Usage

Start the real-time data generator:
```bash
python src/temperature_logger.py
```

Monitor the console for event transmission status. Use Ctrl+C to stop.

## Data Format

Real-time events include:
```json
{
  "timestamp": "2024-03-15T14:30:45.123",
  "machine": "ROTOR_M01",
  "temperature": 72.45,
  "status": "NORMAL",
  "location": "Hall_A",
  "batch_id": "BATCH_1000"
}
```

### Status Thresholds
- NORMAL: ≤75°C
- WARNING: 75-85°C
- CRITICAL: >85°C


## Splunk Dashboard

The project includes a pre-configured dashboard (`src/dashboard/temperature_dashboard.json`) with:

### Visualizations
- Real-time temperature display for each measurement point (ROTOR_M01 to ROTOR_M05)
- Temperature trend line chart for all machines
- Warning table for temperatures above 75°C

### Color Coding
- Green: Temperature ≤ 75°C
- Yellow: Temperature 75-85°C
- Red: Temperature > 85°C

### Key Metrics
```spl
# All measurement points
sourcetype=_json 
| timechart span=1min avg(temperature) by machine

# Critical values
sourcetype=_json 
| where temperature > 75
| bin _time span=30s
| table _time, machine, temperature
```

### Dashboard Installation
1. Navigate to Splunk > Dashboards
2. Click "Create New Dashboard"
3. Select "Source Editor"
4. Copy and paste the contents of `temperature_dashboard.json`
5. Save and view your dashboard

## Troubleshooting

If events aren't appearing in Splunk:
1. Verify HEC is enabled in Global Settings
2. Check the token is correctly copied to `.env`
3. Ensure port 8088 is accessible
4. Look for error messages in Splunk's internal logs