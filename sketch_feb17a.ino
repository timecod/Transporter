#include <Servo.h>
Servo srv;
void setup(){
  pinMode(13, INPUT); // L
  pinMode(12, INPUT); // R
  pinMode(3, INPUT); // stop L
  pinMode(2, INPUT); // stop R
  pinMode(11, INPUT); // trapp
  srv.attach(10); // servo 
  pinMode(7, OUTPUT); // направление M2 (1 - forward) R
  pinMode(6, OUTPUT); // скорость M2
  pinMode(5, OUTPUT); // скорость M1
  pinMode(4, OUTPUT); // направление M1 (0 - forward) L
  srv.write(0);
}
int L, R, trapp, ang = 0;
void loop(){
  L = ( 2*digitalRead(13) - 1 ) * (!digitalRead(3));
  R = ( 2*digitalRead(12) - 1 ) * (!digitalRead(2));
  trapp = 2*digitalRead(11) - 1;
  analogWrite(5, abs(L)*255);
  analogWrite(6, abs(R)*255);
  digitalWrite(4, L > 0);
  digitalWrite(7, R < 0);
  ang += trapp;
  if (ang > 180) { ang = 180; }
  if (ang < 0) { ang = 0; }
  srv.write(ang);
  delay(10);
  
}
