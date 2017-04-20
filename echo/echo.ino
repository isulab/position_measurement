void setup() {
  Serial.begin(38400);
}

void loop() {
  char a;
  if (Serial.available()) {
    a = char(Serial.read());
    Serial.print(a);
  }
}
