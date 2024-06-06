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
    myservo.write(0);  // Tourner à 0 degrés pour la carte RFID
    delay(1000);  // Attendre que le moteur atteigne la position

    if (readRFID()) {
      Serial.print("RFID ");
      printDec(nuidPICC, 4);
      Serial.println();
    }
    delay(2000);
    myservo.write(90);  // Retourner à la position initiale
    delay(1000);       // Attendre que le moteur revienne à 0 degrés
    Serial.println("PRESENCE 0");
  }

  // Lire les commandes série
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    handleCommand(command);
  }
}

void handleCommand(String command) {
  if (command.startsWith("POSITION")) {
    int position = command.substring(9).toInt();
    myservo.write(position);
  } else if (command.startsWith("EVENT")) {
    Serial.println("EVENT Command received: " + command);
  } else if (command.startsWith("PRESENCE")) {
    Serial.println("PRESENCE Command received: " + command);
  } else if (command.startsWith("RFID")) {
    if (command.substring(5) == "allowed") {
      digitalWrite(ledVerte, HIGH);
      digitalWrite(ledRouge, LOW);
      Serial.println("EVENT Carte allowed");
    } else {
      digitalWrite(ledVerte, LOW);
      digitalWrite(ledRouge, HIGH);
      Serial.println("EVENT Carte not allowed");
    }
  } else {
    Serial.println("Unknown command: " + command);
  }
}

void resetCard() {
  for (int i = 0; i < 4; i++) {
    nuidPICC[i] = 0;
  }
  digitalWrite(ledVerte, LOW);
  digitalWrite(ledRouge, LOW);
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
  Serial.print("RFID tag in dec: ");
  printDec(rfid.uid.uidByte, rfid.uid.size);
  Serial.println();
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
