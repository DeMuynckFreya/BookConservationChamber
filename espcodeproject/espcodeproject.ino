int ldr = 4;
int servo = 22;
const int PWMFreq = 50;
const int PWMChannel = 0;
const int PWMResolution = 8;
int dutyCycle = 0;
void setup() {
  Serial.begin(9600, SERIAL_8N1,16,17);
  ledcSetup(PWMChannel, PWMFreq, PWMResolution);
  ledcAttachPin(servo, PWMChannel);
  ledcWrite(PWMChannel, dutyCycle);

}

void loop() {

  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    if (line == "LDR") {
      int value = analogRead(ldr);
      float convertedValue = convertldr(value);
      Serial.println(convertedValue);
    }
    if (line == "close") {
      dutyCycle = 16;
      ledcWrite(PWMChannel, dutyCycle);
      Serial.println("lock is closed");
    }
    if (line == "open") {
      dutyCycle = 5;
      ledcWrite(PWMChannel, dutyCycle);
      Serial.println("lock is open");
    }
  }
}

float convertldr(int value){
  return (value/4095.0)*100;
}
