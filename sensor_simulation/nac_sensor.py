import time
import random
from datetime import datetime, timezone
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=rideau-canal-iot-hub.azure-devices.net;DeviceId=nac_sensor;SharedAccessKey=k5NI7RRPMncg7w/TfM3xLwxPNad0GZ0XWHwKstTKA3s="

def get_telemetry():
    return {
        "location": "NAC",
        "iceThickness": random.uniform(20.0, 40.0),
        "surfaceTemperature": random.uniform(-30,5),
        "snowAccumulation": random.uniform(0.0,20.0),
        "externalTemperature": random.uniform(-30,5),
        "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }

def main():
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    # Used for testing purposes
    # while True:
    #     telemetry = get_telemetry()
    #     print(f"Telemetry data: {telemetry}")
    #     time.sleep(2)
    

    print("Sending telemetry to IoT Hub...")
    try:
        while True:
            telemetry = get_telemetry()
            message = Message(str(telemetry))
            client.send_message(message)
            print(f"Sent message: {message}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped sending messages.")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()