import paho.mqtt.client as mqtt
import time

# MQTT Broker settings
BROKER_ADDRESS = "localhost"  # Change this if your broker is on another host
PORT = 1883  # Default MQTT port
USERNAME = "homeassistant"
PASSWORD = "password123"


# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")


# Create an MQTT client instance
client = mqtt.Client()

# Set the authentication details if needed
client.username_pw_set(USERNAME, PASSWORD)

# Assign event callbacks
client.on_connect = on_connect

# Connect to the broker
client.connect(BROKER_ADDRESS, PORT, 60)  # 60s keepalive

# Start network loop
client.loop_start()

# Publish messages
try:
    while True:
        # Publish to different topics
        client.publish("homeassistant/switch/1/temperature", "53")
        time.sleep(1)  # Wait for 1 second
        client.publish("homeassistant/switch/1/temperature", "47")
        time.sleep(1)
        client.publish("homeassistant/test_sensor/availability", "online")
        time.sleep(1)

        # Example to stop the loop after some iterations
        if __name__ == "__main__":
            for _ in range(3):  # Run 3 times
                pass
            break

except KeyboardInterrupt:
    print("Script interrupted by user.")

finally:
    # Stop the network loop and disconnect from the broker
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT Broker.")