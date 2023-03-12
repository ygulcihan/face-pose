int pot=0;
int val=0;
void setup() {
  pinMode(3,OUTPUT);
  pinMode(A0,INPUT);
}

void loop() {
  pot=analogRead(A0);
  val=map(pot,0,1023,1,160);
  analogWrite(3,val);
}
