int estado=0;

void setup() {
  Serial.begin(9600);
  pinMode(3, INPUT_PULLUP);
}

void loop() {
  estado = digitalRead(3);

  if (estado == HIGH) {
    Serial.println("S");
    delay(1000);
  }
}