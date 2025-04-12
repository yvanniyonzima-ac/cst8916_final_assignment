# Rideau Canal Skateway Monitoring System

## 1. Scenario Description

Skater safety depends on multiple environmental factors such as ice thickness, surface and air temperature, and snow accumulation. Manually monitoring these conditions across the length of the canal is inefficient and prone to delays. A real-time monitoring solution is required to automate data collection and enhance response times when unsafe conditions are detected. To address this need, the National Capital Commission (NCC) has commissioned the development of a real-time data streaming system capable of:

- Streaming IoT sensors to monitor ice and weather conditions along the canal.
- Processing incoming sensor data to detect unsafe conditions in real time.
- Storing results in Azure Blob Storage for future analysis and decision-making.

This designs and implement a real-time monitoring system using simulated IoT sensors, Azure IoT Hub, Azure Stream Analytics, and Azure Blob Storage.

---

## 2. System Architecture

## 3. Implementation Details

### IoT Sensor Simulation and Transmition

There are 3 scripts that simulate an IoT sensor along the Rideau Canal Skateway
- **Downs Lake** : ```dows_lake_sensor.py```
- **Fifth Avenue**: ```fifth_avenue_sensor.py```
- **NAC**: ```nac_sensor.py```
Each scripts generates telemetry data every 10 seconds and sends it to **Azure IoT Hub** using the Azure IoT Device SDK.
The 3 scripts are lauched and managed by the ```run_sensor_simulation.py``` script.

#### Key Functionalities

**1. Telemetry Data Generation**

The `get_telemetry()` function creates a dictionary that mimics real sensor readings. Each reading includes:

- `location`: Static value representing the sensor's location (e.g., "Fifth Avenue").
- `iceThickness`: Random float between 20.0 and 40.0 cm.
- `surfaceTemperature`: Random float between -30°C and 5°C.
- `snowAccumulation`: Random float between 0.0 and 20.0 cm.
- `externalTemperature`: Random float between -30°C and 5°C.
- `timestamp`: Current UTC time formatted as an ISO 8601 string.

**Example JSON Payload**
```json
{
  "location": "Fifth Avenue",
  "iceThickness": 32.1,
  "surfaceTemperature": -4.2,
  "snowAccumulation": 6.5,
  "externalTemperature": -10.3,
  "timestamp": "2025-04-10T15:23:50Z"
}
```
**Get telemetry function example for NAC sensor**
```python
def get_telemetry():
    return {
        "location": "NAC",
        "iceThickness": random.uniform(20.0, 40.0),
        "surfaceTemperature": random.uniform(-30,5),
        "snowAccumulation": random.uniform(0.0,20.0),
        "externalTemperature": random.uniform(-30,5),
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }
```

**2. Connecting to Azure IoT Hub**

The script uses the IoTHubDeviceClient from the azure.iot.device library to establish a connection to Azure IoT Hub using a device connection string:

```python
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
#Note: CONNECTION_STRING is replaced with with the Azure IoT Hub device connection string stored in a global variable.
```

**3. Sending Telemetry Data**

Within the main loop:

- Telemetry is generated using get_telemetry().

- It is wrapped in a Message object from the Azure SDK.

- The message is sent to Azure IoT Hub using client.send_message(message).

- A confirmation is printed to the console.

```python
message = Message(str(telemetry))
client.send_message(message)
```
The loop repeats every 10 seconds to continuously stream data.

**4. Graceful Shutdown**

When Ctrl+C is pressed, or a terminate signal is received, the script catches a KeyboardInterrupt, stops the loop, and disconnects from the IoT Hub:

```python
except KeyboardInterrupt:
    print("Stopped sending messages.")
finally:
    client.disconnect()
```

#### Sensor Simulation Manager Script

This Python script is designed to **launch and manage multiple sensor simulation scripts** concurrently. It simplifies the process of starting and gracefully shutting down multiple simulated IoT sensors used in the Rideau Canal Skateway monitoring system.

**1. Define Sensor Scripts**

```python
scripts = ["dows_lake_sensor.py", "fifth_avenue_sensor.py", "nac_sensor.py"]
```

A list of Python script filenames that simulate sensors at three locations:
- Dow's Lake
- Fifth Avenue
- NAC (National Arts Centre)

**2. Start Subprocesses**
```python
proc = subprocess.Popen([python_version, script])
```
- Each script is launched in its own subprocess using the subprocess.Popen() method.
- The script uses python3 as the default interpreter. You can change this if needed.
- All subprocess references are stored in the processes list for later management.

**3. Keep Main Script Alive**
```python
while True:
    time.sleep(1)
```
The main thread stays active with a continuous loop to allow the sensor scripts to keep running in the background.
This loop runs indefinitely until interrupted by the user.

**4. Graceful Shutdown on Ctrl+C**
```python
except KeyboardInterrupt:
    ...
```
When the user presses Ctrl+C, a KeyboardInterrupt is caught.
All sensor scripts are terminated using proc.terminate() and waited on using proc.wait() to ensure they shut down cleanly.
A final message confirms that all scripts have been stopped.

**Example Output**
```shell
Starting dows_lake_sensor.py...
Starting fifth_avenue_sensor.py...
Starting nac_sensor.py...
All sensor simulation scripts are running. Press Ctrl+C to stop them...
```

### Azure IoT Hub Configuration

- Explain the configuration steps for setting up the IoT Hub, including endpoints and message routing.

#### Create an Azure IoT Hub
1. Go to the Azure Portal

2. Click “Create a resource”

3. Search for IoT Hub and click Create

4. Fill out the basic information:

    - Subscription: *Azure for Students*

    - Resource group: Create or select one (*CANAL-SENSOR-ANALYTICS*)

    - Region: *Canada Central*

    - IoT Hub Name: *rideau-canal-iot-hub*

5. Click Review + Create, then Create

In the networking tab, leave the default public access for the endpoint. This will allow us to connect to the IoT hub over the internet from any location (i.i. we will not need to set up a VNet).
This is good for testing and development environments, such as our simulation.

#### Register a Device

1. Navigate to the left menu, under “Device”, click “Devices”

2. Click Add Device

3. Fill out the information:

    - Device ID: e.g., nac_sensor

    - Leave the rest of the configuration to their default values

4. Click Save

5. Repeat steps 1-4 for Fifth Avenue and Dow's Lake sensors

6. After saving, click the device name to copy its Connection String to the appropriate python script

### Azure Stream Analytics Job

#### Create an Azure Stream Analytics job

1. Go to the Azure Portal

2. Click “Create a resource”

3. Search for Stream  Analytics job and click Create

4. Fill out the basic information:

    - Subscription: *Azure for Students*

    - Resource group: Select *CANAL-SENSOR-ANALYTICS*

    - Name: *dows-lake-sensor-stream*

    - Region: *Canada Central*

    - Hosting Environment: *Cloud*

5. Click Review + Create, then Create

#### Input and Output Destination

#### Query used for data processing.

```sql
SELECT
    IoTHub.ConnectionDeviceId AS DeviceID,
    AVG(iceThickness) AS AvgIceThickness,
    MAX(snowAccumulation) AS MaxSnowAccumulation,
    System.Timestamp AS EventTime
INTO
    [canal-sensor-data-container]
FROM
    [rideau-canal-iot-hub]
GROUP BY
    IoTHub.ConnectionDeviceId, TumblingWindow(minute, 5)
```

### Azure Blob Storage

- Explain how the processed data is organized in Blob Storage (e.g., folder structure, file naming convention).
- Specify the formats of stored data (JSON/CSV).

## 4. Usage Instructions

### Running the IoT Sensor Simulation

- Provide step-by-step instructions for running the simulation script or application.

### Configuring Azure Services

- Describe how to set up and run the IoT Hub and Stream Analytics job.

### Accessing Stored Data
- Include steps to locate and view the processed data in Azure Blob Storage.

## 5. Results

- Highlight key findings, such as:
    - Aggregated data outputs (e.g., average ice thickness).
- Include references to sample output files stored in Blob Storage.

## 6. Reflection

- Discuss any challenges faced during implementation and how they were addressed.