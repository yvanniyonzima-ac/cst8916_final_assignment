# Rideau Canal Skateway Monitoring System

## 1. Scenario Description

Skater safety depends on multiple environmental factors such as ice thickness, surface and air temperature, and snow accumulation. Manually monitoring these conditions across the length of the canal is inefficient and prone to delays. A real-time monitoring solution is required to automate data collection and enhance response times when unsafe conditions are detected. To address this need, the National Capital Commission (NCC) has commissioned the development of a real-time data streaming system capable of:

- Streaming IoT sensors to monitor ice and weather conditions along the canal.
- Processing incoming sensor data to detect unsafe conditions in real time.
- Storing results in Azure Blob Storage for future analysis and decision-making.

This designs and implement a real-time monitoring system using simulated IoT sensors, Azure IoT Hub, Azure Stream Analytics, and Azure Blob Storage.

---

## 2. System Architecture

![Canal IoT Sensors System Architecture](https://github.com/user-attachments/assets/df4be829-ecb2-4ea9-b6e3-3a3fbe335c68)

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

1. Define Input

    1. In the Stream analytics job resource on the left menu, click on Job Topology and then Inputs and then click Add Input
    2. Choose IoT Hub as the input source.
    3. Provide the following details:
        - IoT Hub Namespace: Select your IoT Hub.
        - Consumer Group: Use $Default.
        - Endpoint: Choose Messaging for messages from the IoT device to the cloud
        - Serialization Format: Choose JSON.  

3. Define Output

    1. In the Stream analytics job resource on the left menu, click on Job Topology and then Outputs and then click Add Output
    2. Choose Blob Storage as the output destination.
    3. Provide the following details:
        - Storage Account: Select the Azure Storage Account Created.
        - Container: Create or choose an existing container for storing results.
        - Path Pattern: Optionally define a folder structure (e.g., canal_sensor_output/{date}/{time}).

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

This query processes real-time telemetry data from the Rideau Canal Sensor devices connected to the Azure IoT Hub named ```rideau-canal-iot-hub```. It groups incoming data by each device (IoTHub.ConnectionDeviceId) over fixed 5-minute intervals using a tumbling window.

For each device and time window, it calculates:

- The average ice thickness (```AVG(iceThickness)```)

- The maximum snow accumulation (```MAX(snowAccumulation)```)

It also includes the event timestamp (System.Timestamp), which represents the end of the window period.

The aggregated results are written to the Azure Blob Storage container output sink named ```canal-sensor-data-container```.

### Azure Blob Storage

The processed data is stored in a container called ```canalsensordatastorage``` withing a ```JSON``` file.

#### Sample Output Data: first 10 minutes

```json
{"DeviceID":"dows_lake_sensor","AvgIceThickness":31.118854131246067,"MaxSnowAccumulation":18.592786192599007,"EventTime":"2025-04-11T19:00:00.0000000Z"}
{"DeviceID":"nac_sensor","AvgIceThickness":29.348209229173698,"MaxSnowAccumulation":19.54364425151834,"EventTime":"2025-04-11T19:00:00.0000000Z"}
{"DeviceID":"fifth_avenue_sensor","AvgIceThickness":29.149515734864163,"MaxSnowAccumulation":19.5897428031461,"EventTime":"2025-04-11T19:00:00.0000000Z"}
{"DeviceID":"dows_lake_sensor","AvgIceThickness":31.674160079077257,"MaxSnowAccumulation":19.83992648327632,"EventTime":"2025-04-11T19:05:00.0000000Z"}
{"DeviceID":"nac_sensor","AvgIceThickness":32.15587514004539,"MaxSnowAccumulation":19.88971196782257,"EventTime":"2025-04-11T19:05:00.0000000Z"}
{"DeviceID":"fifth_avenue_sensor","AvgIceThickness":31.48839883695921,"MaxSnowAccumulation":19.458139662939825,"EventTime":"2025-04-11T19:05:00.0000000Z"}
```

## 4. Usage Instructions

### Running the IoT Sensor Simulation

This guide provides step-by-step instructions for running the sensor simulation script, which launches multiple IoT sensor simulators for the Rideau Canal Skateway monitoring system.

#### Prerequisites

Before running the script, ensure you have:

1. **Python Installed**  
   - Verify Python 3 is installed by running:
     ```sh
     python3 --version
     ```
   - If Python is not installed, download it from [python.org](https://www.python.org/downloads/) or install it using your package manager.

2. **Azure IoT SDK for Python**  
   - Install the required Azure IoT SDK:
     ```sh
     pip install azure-iot-device
     ```

3. **Sensor Simulation Scripts**  
   - Ensure the following scripts exist in the same directory as the manager script ```run_sensor_simulation.py```:
     - `dows_lake_sensor.py`
     - `fifth_avenue_sensor.py`
     - `nac_sensor.py`
   - Each script is Python program that sends telemetry data for the different sensors.

---

### Steps to Run the Simulation

#### Step 1: Navigate to the Script Directory

Open a terminal or command prompt and navigate to the folder where the simulation script is located:

```sh
cd /path/to/your/script
```

#### Step 2: Run the Sensor Manager Script

Execute the script using ```python3 sensor_manager.py```. If your system uses python instead of python3, use ```python sensor_manager.py```. 

- **NOTE**: If the system uses python instead of python3, makes sure to change the ```python_version``` variable on line 12 in the ```run_sensor_simulation.py``` script to ```python```.

#### Step 3: Monitor the Output
Once the script starts, it will launch all sensor simulation scripts. You should see output similar to:

```sh
Starting dows_lake_sensor.py...
Starting fifth_avenue_sensor.py...
Starting nac_sensor.py...
All sensor simulation scripts are running. Press Ctrl+C to stop them...
```

Each sensor script will continuously generate telemetry data and send it to Azure IoT Hub.

#### Step 4: Stop the Simulation
To stop the simulation, press Ctrl+C in the terminal. This will:

Terminate all running sensor scripts and ensure a clean shutdown of the system.

Expected output when stopping:

```sh
Ctrl+C detected. Terminating all scripts...
All sensor simulation scripts have been stopped.
```
---
### Running Stream Analytics job

Once the script to simulate data is running, it will it will start streaming the data to the IoT hub every 10 seconds. In the Job Topology -> Query section of the Stream Analytics job, you can view a sample of the incoming data by clicking 'Input preview' under the query editor view.

After 5 minutes of data streaming, the query can also be tested by clicking 'Test selected query' in the top left pane of the query editor view. This will show a sample output of the aggregated data based on the query. 

If the test is successful (i.e. no errors and expected output):

1. Click the 'Save query' button in the top pane of the query editig view
2. Go back to the Overview page of the Stream Analytics job resource
3. Click on Start job to run the Query

### Accessing Stored Data

To locate and view the processed data in Azure Blob Storage:

1. Navigate to your Azure Storage account (e.g. ```canalsensordatastorage```)
2. In the left navigation blade, got to Data Storage -> Containers and locate the container you attached as the output to the Stream Analytics job (e.g. ```canal-sensor-data-container```)
3. There will be a file Blob Type file in that container with a long alphaneumerical name,
    - Path Pattern: Optionally if you defined a folder structure when setting up the output (e.g., canal_sensor_output/{date}/{time}), navigate to that folder and then the file will be in that folder.
4. Download the file in your preffered directory and then open in an editor that can view ```JSON``` data.

## 5. Results and Key Findings: Rideau Canal Skateway Monitoring

This section highlights key insights from the real-time aggregated sensor data collected between `2025-04-11T19:00:00Z` and `2025-04-11T19:50:00Z` across three key locations: Dow's Lake, NAC, and Fifth Avenue.

### Average Ice Thickness (cm)

| Time (UTC)             | Dow's Lake | NAC     | Fifth Avenue |
|------------------------|------------|---------|--------------|
| 19:00                  | 31.12      | 29.35   | 29.15        |
| 19:05                  | 31.67      | 32.16   | 31.49        |
| 19:10                  | 30.44      | 32.41   | 30.66        |
| 19:15                  | 30.71      | 31.62   | 28.30        |
| 19:35                  | 30.21      | 27.67   | 27.02        |
| 19:45                  | 30.88      | 30.45   | 30.49        |
| 19:50                  | 30.28      | 30.06   | 31.71        |

#### Observations:

- NAC reached the **highest average ice thickness** at `32.41 cm` (19:10).
- Fifth Avenue experienced a **dip to 27.02 cm** at 19:35, indicating potential softening in that area.
- Dow’s Lake maintained relatively stable ice thickness around 30–31 cm throughout.

---

### Maximum Snow Accumulation (cm)

| Time (UTC)             | Dow's Lake | NAC     | Fifth Avenue |
|------------------------|------------|---------|--------------|
| 19:00                  | 18.59      | 19.54   | 19.59        |
| 19:05                  | 19.84      | 19.89   | 19.46        |
| 19:10                  | 19.38      | 19.58   | 19.09        |
| 19:15                  | 19.75      | 19.21   | 19.77        |
| 19:35                  | 11.69      | 19.98   | 15.88        |
| 19:45                  | 18.87      | 15.47   | 19.94        |
| 19:50                  | 19.21      | 19.32   | 19.96        |

#### Observations

- **NAC hit the highest snow accumulation** of **19.98 cm** at 19:35.
- Dow's Lake dropped significantly to **11.69 cm** at 19:35, possibly due to local snow clearing or melting.
- Fifth Avenue consistently recorded high snow values near 19.5–19.9 cm.

### Conclusion

These findings show the system’s ability to:
- Detect variability in ice and snow conditions across locations.
- Support timely decisions about safety and maintenance.
- Offer valuable insights for operational planning and public updates.

## 6. Reflection

I did not face any significant challenges during the implementation. Azure IoT Hub and Stream Analytics offer a user-friendly interface that made the configuration process intuitive. Additionally, the tutorial video provided in class was straightforward and detailed, making it easy to follow along with the example IoT simulator project setup.
