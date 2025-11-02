import paho.mqtt.client as mqtt

# MQTT Broker credentials
BROKER = "n171f1d9.ala.eu-central-1.emqxsl.com"
PORT = 8883
USERNAME = "aryanvish2006"
PASSWORD = "aryanvishvishalyadav"

# Topic for broadcast command
TOPIC = "control/broadcast"

# Command you want to send
COMMAND = "desktop"

# Create and configure MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()  # Using TLS because your broker uses port 8883

# Connect and send command
client.connect(BROKER, PORT, 60)
client.publish(TOPIC, COMMAND, qos=1)
client.disconnect()

print(f"Sent command '{COMMAND}' to topic '{TOPIC}'")
