#include <Servo.h>
#include <SPI.h>
#include <MFRC522.h>

// Pins pour les leds
const int ledRouge = 9;
const int ledVerte = 8;

// Pins pour le capteur de distance HC-SR04
const int trigPin = 6;
const int echoPin = 7;

// Servo
Servo myservo;
const int servoPin = 3;

// Pins pour le RC522
#define SS_PIN 10
#define RST_PIN 5
MFRC522 rfid(SS_PIN, RST_PIN);
byte nuidPICC[4];

enum State {
  WAITING_FOR_PRESENCE,
  MOVING_SERVO,
  WAITING_FOR_RFID,
  RFID_READ,
  WAITING_AFTER_RFID,
};

State currentState = WAITING_FOR_PRESENCE;
bool cardRead = false;  // Variable pour suivre si la carte a été lue avec succès
unsigned long previousMillis = 0;  // Variable pour suivre le temps écoulé

void setup() {
  Serial.begin(9600);

  // Initialisation des leds
  pinMode(ledRouge, OUTPUT);
  pinMode(ledVerte, OUTPUT);
  digitalWrite(ledRouge, LOW);
  digitalWrite(ledVerte, LOW);

  // Initialisation du capteur de distance
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Initialisation du servomoteur
  myservo.attach(servoPin);
  myservo.write(90);  // Position initiale à 0

  // Initialisation du RC522
  SPI.begin();      // Initialiser le bus SPI
  rfid.PCD_Init();  // Initialiser le lecteur RFID
}

void loop() {
  switch (currentState) {
    case WAITING_FOR_PRESENCE:
      detectPresence();
      break;
    case MOVING_SERVO:
      moveServo();
      break;
    case WAITING_FOR_RFID:
      waitForRFID();
      break;
    case RFID_READ:
      handleRFID();
      break;
    case WAITING_AFTER_RFID:
      waitAfterRFID();
      break;
  }

  // Lire les commandes série
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    handleCommand(command);
  }
}

void detectPresence() {
  // Mesurer la distance avec le HC-SR04
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  if (distance < 10) {
    Serial.println("PRESENCE 1");
    currentState = MOVING_SERVO;
  }
}

void moveServo() {
  myservo.write(0);  // Tourner à 0 degrés pour la carte RFID
  Serial.println("Motor position: 90"); // Nouveau message pour mouvement moteur
  delay(1000);  // Attendre que le moteur atteigne la position
  currentState = WAITING_FOR_RFID;
}

void waitForRFID() {
  if (readRFID()) {
    Serial.print("RFID ");
    printDec(nuidPICC, 4);
    Serial.println();
    currentState = RFID_READ;
    cardRead = true;  // La carte a été lue avec succès
  }
}

void handleRFID() {
  // Traitement de la carte RFID lue
  // Votre code pour gérer la lecture de la carte RFID va ici

  // Après avoir traité la carte RFID, attendre un moment puis revenir à l'état initial
  currentState = WAITING_AFTER_RFID;
  previousMillis = millis();  // Stocker le temps actuel
}

void waitAfterRFID() {
  // Attendre 3 secondes après la lecture de la carte RFID
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= 3000) {
    myservo.write(90);  // Retourner à la position initiale
    Serial.println("Motor position: 0"); // Nouveau message pour mouvement moteur
    delay(1000);       // Attendre que le moteur revienne à 0 degrés
    currentState = WAITING_FOR_PRESENCE;  // Revenir à l'état initial
    cardRead = false;  // Réinitialiser la variable cardRead
    Serial.println("PRESENCE 0");
  }
}

void handleCommand(String command) {
  // Votre code pour gérer les commandes série va ici
}

bool readRFID() {
  // Vérifier la présence d'une nouvelle carte
  if (!rfid.PICC_IsNewCardPresent()) return false;
  // Vérifier si la carte a été lue correctement
  if (!rfid.PICC_ReadCardSerial()) return false;
  // Stocker le NUID de la carte lue
  for (byte i = 0; i < 4; i++) {
    nuidPICC[i] = rfid.uid.uidByte[i];
  }
  // Arrêter la communication avec la carte
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  return true;
}

void printDec(byte* buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }
}
