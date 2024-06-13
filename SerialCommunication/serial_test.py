import serial
import time
import paho.mqtt.client as mqtt
import requests
from datetime import datetime, timezone

# Paramètres de communication série
SERIAL_PORT = 'COM5'  # Changer en fonction du port COM de votre Arduino
BAUD_RATE = 9600

# Paramètres MQTT
MQTT_BROKER = '192.168.1.6'  # Adresse IP de votre Raspberry Pi
MQTT_PORT = 1883  # Port du broker MQTT
MQTT_TOPIC_RFID = 'iot/rfid'  # Sujet pour publier les événements
MQTT_TOPIC_PRESENCE = 'iot/presence'
MQTT_TOPIC_MOTOR = 'iot/motor'
MQTT_TOPIC_AUTHORIZED = 'iot/card/authorized'  # Sujet pour publier les résultats de l'autorisation de la carte
MQTT_TOPIC_CARDS_REQUEST = 'iot/request/cards'  # Nouveau sujet pour recevoir les demandes de position du moteur
MQTT_TOPIC_CARDS_RESPONSE = 'iot/response/cards'  # Sujet pour publier les réponses de la position du moteur
MQTT_USER = 'morin'  # Nom d'utilisateur MQTT
MQTT_PASSWORD = 'morin'  # Mot de passe MQTT

# URL de l'API FastAPI
API_URL = 'http://localhost:8000'  # Remplacer par l'adresse IP et le port de votre serveur FastAPI

# Fonction pour envoyer une commande à l'Arduino
def send_command(ser, command):
    ser.write(command.encode('utf-8'))

# Fonction pour lire les données envoyées par l'Arduino
def read_data(ser):
    return ser.readline().decode('utf-8').rstrip()

# Initialisation de la communication série
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Attendre que la communication soit établie
time.sleep(5)

# Configuration du client MQTT
client = mqtt.Client()

# Définir les informations d'identification MQTT
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# Définir les fonctions de rappel pour le client MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # S'abonner aux sujets nécessaires
    client.subscribe(MQTT_TOPIC_RFID)
    client.subscribe(MQTT_TOPIC_CARDS_REQUEST)  # S'abonner au nouveau sujet

def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"Message received on topic {msg.topic}: {payload}")

    if msg.topic == MQTT_TOPIC_CARDS_REQUEST:
        # Traiter la demande de position du moteur
        response = requests.get(f"{API_URL}/rfid_reads/")
        if response.status_code == 200:
            cards_read_data = response.json()
            print(cards_read_data)
            client.publish(MQTT_TOPIC_CARDS_RESPONSE, f"{cards_read_data}")
        else:
            print("Failed to get rfid read data")
    elif payload.startswith("RFID"): 
        parts = payload.split()
        card_number = "".join(parts[1:])  # Concatène tous les segments après "RFID"

        print(card_number)
        if card_number == '0':
            client.publish(MQTT_TOPIC_AUTHORIZED, "none")
        else:
            response = requests.get(f"{API_URL}/cards/{card_number}")
            if response.status_code == 200:
                authorized = response.json()
                if authorized:
                    print(f"Card {card_number} is authorized.")
                    client.publish(MQTT_TOPIC_AUTHORIZED, "authorized")
                else:
                    print(f"Card {card_number} is not authorized.")
                    client.publish(MQTT_TOPIC_AUTHORIZED, "not authorized")

                # Enregistrer l'événement RFID via l'API REST
                rfid_data = {
                    "card_uid": card_number,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "authorized": authorized
                }
                requests.post(f"{API_URL}/rfid_reads/", json=rfid_data)
            else:
                print(f"Card {card_number} is not authorized.")
                client.publish(MQTT_TOPIC_AUTHORIZED, "not authorized")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Connexion au broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()  # Démarrer le thread de réseau

# Période d'attente avant d'envoyer les premiers messages de détection
initial_delay = 10
print(f"Waiting for {initial_delay} seconds before starting message processing...")
time.sleep(initial_delay)
print("Starting message processing...")

try:
    # Exemples de commandes à envoyer à l'Arduino
    commands = [
        "POSITION 45\n",
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
            parts = response.split()
            if len(parts) == 2 and parts[1].replace('.', '', 1).isdigit():
                distance = float(parts[1])
                client.publish(MQTT_TOPIC_PRESENCE, f"{response}")
                
                if response.startswith("PRESENCE 1"):                  
                    # Enregistrer l'événement de présence via l'API REST
                    presence_data = {
                        "distance": distance,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    requests.post(f"{API_URL}/presence_detections/", json=presence_data)
            else:
                print("Invalid PRESENCE data received")

        elif response.startswith("Motor position"):
            parts = response.split(": ")
            if len(parts) == 2 and parts[1].isdigit():
                position = int(parts[1])
                client.publish(MQTT_TOPIC_MOTOR, f"{response}")

                # Enregistrer l'événement de position du moteur via l'API REST
                motor_position_data = {
                    "position": position,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                requests.post(f"{API_URL}/motor_position/", json=motor_position_data)
            else:
                print("Invalid Motor position data received")

        elif response.startswith("RFID"):
            client.publish(MQTT_TOPIC_RFID, f"{response}")

        time.sleep(0.1)  # Petite pause pour éviter une surcharge de la boucle

except KeyboardInterrupt:
    # Interruption par l'utilisateur (Ctrl+C)
    print("Interruption du programme.")

finally:
    # Fermer la connexion série
    ser.close()
    print("Connexion série fermée.")
    # Déconnexion du client MQTT
    client.loop_stop()
    client.disconnect()
