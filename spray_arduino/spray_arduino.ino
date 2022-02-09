void setup() {
  Serial.begin(115200);
  
  for(int i=2; i<=13; i++){
    pinMode(i, OUTPUT);
  }
}

void loop() {
  while(Serial.available() > 0){
     String data = Serial.readStringUntil('\n');
     if(data.startsWith("ON")){
      data.remove(0,2);
      digitalWrite(data.toInt(), HIGH);
     }
     if(data.startsWith("OFF")){
      data.remove(0,3);
      digitalWrite(data.toInt(), LOW);
     }
  }
}
