int redPin = 9;
int greenPin = 10;
int bluePin = 11;

void setup()
{
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void setColor(String& color) {
  long number = strtol( &color[0], NULL, 16);

  long r = number >> 16;
  long g = number >> 8 & 0xFF;
  long b = number & 0xFF;

  // ---------------------------------
  // PNP transistors controls the values
  // 0v (base pin) => 5v (emitter pin); 
  // 5v (base pin) => 0v (emitter pin);
  // so i need to patch the values (or to use NPN transistors)

  r = 255 - r;
  g = 255 - g;
  b = 255 - b;
  // ---------------------------------

  analogWrite(redPin, r);
  analogWrite(greenPin, g);
  analogWrite(bluePin, b);
}

void loop()
{
  if (Serial.available()) {
    delay(100);
    while (Serial.available() > 0) {
      String color = Serial.readString();
      setColor(color);
    }
  }
}
