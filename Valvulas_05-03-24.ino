//-----------------COM7-------------------------

#include <AccelStepper.h>

AccelStepper stepper1(AccelStepper::FULL4WIRE, 29, 33, 31, 35);
AccelStepper stepper2(AccelStepper::FULL4WIRE, 37, 41, 39, 43);
AccelStepper stepper3(AccelStepper::FULL4WIRE, 45, 49, 47, 51);

int POSICAO_V1 = 0;
int POSICAO_V2 = 0;
int POSICAO_V3 = 0;

void setup() {
  Serial.begin(9600);
  stepper1.setMaxSpeed(400.0);
  stepper1.setAcceleration(400.0);
  stepper1.setCurrentPosition(0); // Define a nova posição inicial
  stepper2.setMaxSpeed(400.0);
  stepper2.setAcceleration(400.0);
  stepper2.setCurrentPosition(0);
  stepper3.setMaxSpeed(400.0);
  stepper3.setAcceleration(400.0);
  stepper3.setCurrentPosition(0);

  delay(3000);
}

void loop() {
  if (Serial.available()) {
    String comando = Serial.readStringUntil('\r');
    if (comando[0] == 'V' && comando[1] == 'X' && comando[2] == ' ') {

      int novaPosicaoV1 = ((comando[3]-48) * 100) + ((comando[4]-48) * 10) + (comando[5]-48);
      int novaPosicaoV2 = (comando[7]-48) * 100 + (comando[8]-48) * 10 + (comando[9]-48);
      int novaPosicaoV3 = (comando[11]-48) * 100 + (comando[12]-48) * 10 + (comando[13]-48);
      //Serial.println(novaPosicaoV1);

      POSICAO_V1 = ((novaPosicaoV1*30/100) * 145);
      
      if (novaPosicaoV2 == 0) {
        POSICAO_V2 = (novaPosicaoV2*174);
      }
      else {
        POSICAO_V2 = ((10 + (novaPosicaoV2*45/100)) * 174);
      }
      
      POSICAO_V3 = ((novaPosicaoV3*25/100) * 177.5);
      //Serial.println(POSICAO_V1);
      //Serial.println(POSICAO_V2);
      //Serial.println(POSICAO_V3);
      stepper1.moveTo(POSICAO_V1);
      stepper2.moveTo(POSICAO_V2);
      stepper3.moveTo(POSICAO_V3);
    }
    else if (comando == "parar") {
      stepper1.stop();
      stepper2.stop();
      stepper3.stop();
      stepper1.moveTo(0);
      stepper2.moveTo(0);
      stepper3.moveTo(0);
    }
  }

  stepper1.run();
  stepper2.run();
  stepper3.run();
}
