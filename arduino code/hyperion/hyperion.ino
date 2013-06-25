#include <AccelStepper.h>

byte motor;
int motorSteps;
int numBytes = 0;
boolean doneReading = false;
boolean reading = false;
AccelStepper stepper1(1, 2, 3);
AccelStepper stepper2(4, 5, 6);
AccelStepper stepper3(7, 8, 9);
void setup() {
  Serial.begin(9600);
  stepper1.setMaxSpeed(300);
  stepper1.setAcceleration(100);
  stepper2.setMaxSpeed(300);
  stepper2.setAcceleration(100);
  stepper3.setMaxSpeed(300);
  stepper3.setAcceleration(100);
  pinMode(13,OUTPUT);
}
 
 void loop() {
   if(doneReading == true){
     AccelStepper currentStepper;
     if(motor == 0x01){
       currentStepper = stepper1;
     }else if(motor == 0x02){
       currentStepper = stepper2;
     }else if(motor == 0x03){
       currentStepper = stepper3;
     }
     currentStepper.move(motorSteps);
     while(currentStepper.distanceToGo() != 0){
        currentStepper.run();
     }
     Serial.write(0x44);
     doneReading = false;
   }
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    byte inChar = (byte)Serial.read(); 
   
    if(inChar == 0xF0){                        //First input char
      numBytes = 0;
      doneReading = false;
      reading = true;
    }else if(inChar == 0x0F && reading == false){      //Last input char
       doneReading = true;
       reading = false;
       digitalWrite(13,HIGH);
    }else if(reading == false && inChar == 0x42){      //Handshake
      Serial.write(0x41);
    }else if(reading == true && numBytes == 0){        //First byte for motor selection
       motor = inChar; 
       numBytes++;
    }else if(reading == true){                         //Read motor steps
       char buffer[] = {' ',' ',' ',' ',' ',' ',' '}; //Buffer upto 7 chars
       Serial.readBytesUntil('\n', buffer, 7);       //Read upto 7 chars
       motorSteps = atoi(buffer);              //Convert to int
       reading = false;                        //no more input (except delimiting character)
    }
  }
}

