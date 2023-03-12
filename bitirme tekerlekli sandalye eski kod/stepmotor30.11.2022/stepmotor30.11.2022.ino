#define dir 3
#define pul 4

int value;
int degree_last;
int degree=0;
int degree2=267;
int k;
int state;
int difference;
void setup() {
  k=0;
  degree=0;
  degree_last=267;
  state=267;
  Serial.begin(9600);
  Serial.println("Pot değer okuma");
  pinMode(dir,OUTPUT);
  pinMode(pul,OUTPUT);
  digitalWrite(dir,HIGH);
}

void loop() {

  value=analogRead(A0);
  Serial.println(value);
  degree=map(value, 0,1023,0,534);
  if(degree<282 && degree>252){
     if(267>state){
      right(267-state);
      state=267;
      }
      if(267<state){
      left(state-267);
      state=267;
      }
      if(267==state){
      digitalWrite(pul,LOW);
      }
    
  }
  else if(degree>degree_last+15 || degree<degree_last-15){
    if(degree>state){
    right(degree-state);
    state=degree;
    }
    if(degree<state){
    left(state-degree);
    state=degree;
    }
    if(degree==state){
    digitalWrite(pul,LOW);
    }
    degree_last=degree;
    }
}

int right(int x){
  k=0;
  digitalWrite(dir,HIGH);
  while(k!=x){
    digitalWrite(pul,HIGH);
    delayMicroseconds(100);
    digitalWrite(pul,LOW);
    delayMicroseconds(100);
    k+=1;
  }
  return k;
}

int left(int x){
  k=0;
  digitalWrite(dir,LOW);
  while(k!=x){
    digitalWrite(pul,HIGH);
    delayMicroseconds(100);
    digitalWrite(pul,LOW);
    delayMicroseconds(100);
    k+=1;
  }
  return k;
}