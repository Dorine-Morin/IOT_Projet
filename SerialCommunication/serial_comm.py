import paho.mqtt.client as mqtt
import serial
import time

# Configuration MQTT
MQTT_BROKER = 'broker_address'
MQTT_PORT = 1883

# Configuration Serial
SERIAL_PORT = '/dev/ttyUSB0'  # Remplacez par le port série correct pour votre Arduino
SERIAL_BAUDRATE = 9600

# Connexion série avec l'Arduino
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
time.sleep(2)  # Attendre que la connexion série soit établie

# Callback lorsque la connexion au broker MQTT est établie
def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code de résultat: " + str(rc))
    client.subscribe("node_red_topic")
    # Ajoutez d'autres topics MQTT à surveiller ici

# Callback lorsque un message MQTT est reçu
def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        print(f"Message reçu sur le topic {msg.topic}: {message}")

        # Relayer le message à l'Arduino via la communication série
        ser.write(message.encode())

    except Exception as e:
        print(f"Erreur lors du traitement du message: {e}")

# Configuration du client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Boucle pour maintenir la connexion MQTT
client.loop_start()

try:
    while True:
        if ser.in_waiting > 0:
            arduino_message = ser.readline().decode('utf-8').strip()
            print(f"Message de l'Arduino: {arduino_message}")
            # Envoyer des messages MQTT en fonction des événements détectés par l'Arduino
            if arduino_message.startswith("RFID"):
                mqtt_message = "RFID read"
                client.publish("arduino_events", mqtt_message)
            elif arduino_message.startswith("PRESENCE"):
                mqtt_message = "Presence detected"
                client.publish("arduino_events", mqtt_message)
            elif arduino_message.startswith("POSITION"):
                mqtt_message = f"Motor position: {arduino_message[9:]}"
                client.publish("arduino_events", mqtt_message)
            else:
                mqtt_message = "Unknown event"
                client.publish("arduino_events", mqtt_message)
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Déconnexion du client MQTT")
    client.loop_stop()
    client.disconnect()
    ser.close()
