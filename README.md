# Temperature Monitoring System for RotorWind GmbH

This project generates simulated temperature sensor data for wind turbine rotor manufacturing machines. The data is formatted for analysis in Splunk.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/FlorianBoehler/dlbingdabd01.git
cd dlbingdabd01
```

2. Create and activate virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the temperature logger:
```bash
python src/temperature_logger.py
```

This will generate log files in the `logs` directory that can be imported into Splunk.

## Data Format

The generated logs contain the following fields:
- timestamp: ISO 8601 format with millisecond precision
- machine: Unique machine identifier (ROTOR_Mxx)
- temperature: Temperature in Celsius with 2 decimal places
- status: NORMAL (≤75°C), WARNING (75-85°C), or CRITICAL (>85°C)
- location: Machine location in the facility
- batch_id: Current production batch identifier
