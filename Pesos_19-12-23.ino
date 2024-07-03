/*
 * Planta de Destilação Multivasos
 * Baseado na Planta de Unidade e Temperatura de  Angelo Collovini
 -----------------COM8-------------------------
 */
/*BIBLIOTECAS*/
#include "max6675.h" //biblioteca para termopar
#include "HX711.h"  //biblioteca para células de carga
#include <string.h>
/*VARIÁVEIS GLOBAIS*/
char Buffer[64];  //Buffer para armazenar a entrada serial
String cmd;       //Variável de comando recebido
float var=100;        //Valor recebido

/*CONSTANTES*/
const char sp = ' ';     //comando espaço
const char nl = '\n';    //quebra de linha

/*CELULAS DE CARGA*/
//Valor de calibragem das células de carga
#define P0CAL -403365.5189
#define P1CAL -389426.4114
#define P2CAL -378367.7773
#define P3CAL 398155.4728

//Valor de tara das células de carga
#define P0TAR 3
#define P1TAR 3
#define P2TAR 3
#define P3TAR 3
// Pinos
//Pinos da célula 0
#define P0DT A3 
#define P0SCK A7 
//Pinos da célula 1
#define P1DT A2
#define P1SCK A6
//Pinos da célula 2
#define P2DT A1
#define P2SCK A5
//Pinos da célula 3
#define P3DT A8 //A0
#define P3SCK A12 //A4

//Declara todas células
HX711 P0;
HX711 P1;
HX711 P2;
HX711 P3;

float P00, P01, P02, P03;
String c;

void rotina(void){
  c = Serial.readStringUntil('\r');
  int i;
  
  if (c=="ler")
  {
    P00 = P0.get_units(P0TAR),3;
    P01 = P1.get_units(P1TAR),3;
    P02 = P2.get_units(P2TAR),3;
    P03 = P3.get_units(P3TAR),3;

    Serial.println("Peso0: ");
    Serial.println(P00,3);
    Serial.println("Peso1: ");
    Serial.println(P01,3);
    Serial.println("Peso2: ");
    Serial.println(P02,3);
    Serial.println("Peso3: ");
    Serial.println(P03,3);
    Serial.println("s");
    c="f";
  }
  delay(50);
}
void setup() {
  Serial.begin(9600);

  //Setup das células de carga
  P0.begin(P0DT, P0SCK);
  P1.begin(P1DT, P1SCK);
  P2.begin(P2DT, P2SCK);
  P3.begin(P3DT, P3SCK);
  delay(3000);
  P0.set_scale(P0CAL);
  P1.set_scale(P1CAL);
  P2.set_scale(P2CAL);
  P3.set_scale(P3CAL);
  delay(3000);
  P0.tare(P0TAR);
  P1.tare(P1TAR);
  P2.tare(P2TAR);
  P3.tare(P3TAR);
  delay(3000);
}
 
void loop() {
  rotina();
}