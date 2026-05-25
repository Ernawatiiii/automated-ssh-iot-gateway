#include <Adafruit_Sensor.h>
#include <DHT.h>

#define DHTPIN 5
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);
unsigned long seq = 0;

void setup() {
  Serial.begin(115200);
  pinMode(DHTPIN, INPUT_PULLUP);
  dht.begin();
  delay(5000);
}

void loop() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  Serial.print("esp32a,");
  if (isnan(t) || isnan(h)) {
    Serial.print("nan,nan");
  } else {
    Serial.print(t,1); Serial.print(",");
    Serial.print(h,1);
  }
  Serial.print(",");
  Serial.println(seq++);

  delay(2000);
}
