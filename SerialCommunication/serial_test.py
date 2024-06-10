import serial
import time
import paho.mqtt.client as mqtt

# Paramètres de communication série
SERIAL_PORT = 'COM5'  # Changer en fonction du port COM de votre Arduino
BAUD_RATE = 9600

# Paramètres MQTT
MQTT_BROKER = '192.168.0.16'  # Adresse IP de votre Raspberry Pi
MQTT_PORT = 1883  # Port du broker MQTT
MQTT_TOPIC = 'iot/project/events'  # Sujet pour publier les événements
MQTT_USER = 'morin'  # Nom d'utilisateur MQTT
MQTT_PASSWORD = 'morin'  # Mot de passe MQTT

# Fonction pour envoyer une commande à l'Arduino
def send_command(ser, command):
    ser.write(command.encode('utf-8'))

# Fonction pour lire les données envoyées par l'Arduino
def read_data(ser):
    return ser.readline().decode('utf-8').rstrip()

# Initialisation de la communication série
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Attendre que la communication soit établie
time.sleep(2)

# Configuration du client MQTT
client = mqtt.Client()

# Définir les informations d'identification MQTT
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Définir les fonctions de rappel pour le client MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

client.on_connect = on_connect
client.on_publish = on_publish

# Connexion au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    # Exemples de commandes à envoyer à l'Arduino
    commands = [
        "POSITION 45\n",
        "EVENT Test\n",
        "PRESENCE 1\n",
        "RFID allowed\n",
    ]

    # Envoyer chaque commande à l'Arduino
    for command in commands:
        send_command(ser, command)

    # Boucle infinie pour lire les données continuellement
    while True:
        response = read_data(ser)
        if response.startswith("PRESENCE"):
            client.publish(MQTT_TOPIC, f"Presence detected: {response}")
        elif response.startswith("Motor position"):
            client.publish(MQTT_TOPIC, f"Motor position changed: {response}")
        elif response.startswith("RFID"):
            client.publish(MQTT_TOPIC, f"RFID tag detected: {response}")
        elif response.startswith("EVENT Command received: EVENT"):
            client.publish(MQTT_TOPIC, f"Event detected: {response}")
        elif response.startswith("EVENT Carte"):
            client.publish(MQTT_TOPIC, f"RFID event: {response}")
        time.sleep(0.1)  # Petite pause pour éviter une surcharge de la boucle

except KeyboardInterrupt:
    # Interruption par l'utilisateur (Ctrl+C)
    print("Interruption du programme.")

finally:
    # Fermer la connexion série
    ser.close()
    print("Connexion série fermée.")
    # Déconnexion du client MQTT
    client.disconnect()
