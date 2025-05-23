import time
import random
from datetime import datetime, timezone
from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=rideau-canal-iot-hub.azure-devices.net;DeviceId=fifth_avenue_sensor;SharedAccessKey=Z6ElpP6GICop/NWh5SdSRyYo8J/MNasKw89QeUaYMDY="

def get_telemetry():
    return {
        "location": "Fifth Avenue",
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
    

    print("Sending Fifth Avenue telemetry to IoT Hub...")
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