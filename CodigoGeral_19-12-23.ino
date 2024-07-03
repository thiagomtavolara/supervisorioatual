/*
 * Planta de Destilação Multivasos
 * Baseado na Planta de Unidade e Temperatura de  Angelo Collovini
 -----------------COM4-------------------------
 */
/*BIBLIOTECAS*/
#include "max6675.h" //biblioteca para termopar
#include "HX711.h"  //biblioteca para células de carga
#include <string.h>
/*VARIÁVEIS GLOBAIS*/
char Buffer[64];  //Buffer para armazenar a entrada serial
String cmd;       //Variável de comando recebido
float var=100;        //Valor recebido
int iwrite1 = 100;   //Valor recebido a ser alterado
int iwrite2 = 100;
int iwrite3 = 100;
int PWM_RELE = 100;//Valor do pwm do rele
int rele = 1;     //Auxiliar para ver o status do módulo relé

/*CONSTANTES*/
const char sp = ' ';     //comando espaço
const char nl = '\n';    //quebra de linha
// Pinos
/*TERMOPARES*/
//Pinos do termopar 0
#define T0SO 35  //11
#define T0CS 37 //12
#define T0CLK 39 //26
//Pinos do termopar 1
#define T1SO 49 //10
#define T1CS 51 //9
#define T1CLK 53 //8
//Pinos do termopar 2
#define T2SO 34 //7
#define T2CS 36 //6
#define T2CLK 38 //5
//Pinos do termopar 3
#define T3SO 48 //4
#define T3CS 50 //3
#define T3CLK 52 //2

//Inicia todos termopares
MAX6675 T0(T0CLK, T0CS, T0SO);
MAX6675 T1(T1CLK, T1CS, T1SO);
MAX6675 T2(T2CLK, T2CS, T2SO);
MAX6675 T3(T3CLK, T3CS, T3SO);

// Pinos
/*BOMBAS*/
//Pinos da bomba 1
#define B1IN1 45  //52
#define B1IN2 44
//Pinos da bomba 2
#define B2IN1 3 //50
#define B2IN2 2 //46
//Pinos da bomba 3
#define B3IN1 12 //48
#define B3IN2 13

/*RELÉ*/
#define PINRELE 26 //27 //28   //Pino do módulo relé

String c;

void rotina(void){
  c = Serial.readStringUntil('\r');
  
  int i;
   if(c[0]=='P')
  {
    if(c[1]=='W')
    {
      if(c[2]=='M')
      {
        PWM_RELE=(c[3]-48)*100+(c[4]-48)*10+(c[5]-48);
      }
    }
  }
  
  if (c=="ler")
  {
    //Realiza as leituras
    float T00 = T0.readCelsius();
    float T01 = T1.readCelsius();
    float T02 = T2.readCelsius();
    float T03 = T3.readCelsius();

    Serial.println("T0: ");
    Serial.println(T00);
    Serial.println("T1: ");
    Serial.println(T01);
    Serial.println("T2: ");
    Serial.println(T02);
    Serial.println("T3: ");
    Serial.println(T03);
    Serial.println("s");
    c="f";
  }
  
  if(c=="liga rele")
  {
    digitalWrite(PINRELE, HIGH);
    rele = 1;
  }
  if(c=="desliga rele")
  {
    digitalWrite(PINRELE, LOW);
    rele = 0;
  }
  if(c[0]=='B')
  {
    if(c[1]=='1')
    {
      if(c[2]==' ')
      {
        iwrite1=(c[3]-48)*100+(c[4]-48)*10+(c[5]-48);

        digitalWrite(B1IN1, LOW);        //Liga a bomba d'água
        digitalWrite(B1IN2, HIGH);
        analogWrite(B1IN2, iwrite1);
      }
    }
  }
    if(c[0]=='B')
  {
    if(c[1]=='2')
    {
      if(c[2]==' ')
      {
        iwrite2=(c[3]-48)*100+(c[4]-48)*10+(c[5]-48);
        //Serial.println("A vazao eh");
        //Serial.println((int)iwrite1);
       // Serial.println(B2vaz);
        digitalWrite(B2IN1, LOW);        //Liga a bomba d'água
        digitalWrite(B2IN2, HIGH);
        analogWrite(B2IN2, iwrite2);
      }
    }
  }
    if(c[0]=='B')
  {
    if(c[1]=='3')
    {
      if(c[2]==' ')
      {
        iwrite3=(c[3]-48)*100+(c[4]-48)*10+(c[5]-48);
        //Serial.println("A vazao eh");
        //Serial.println((int)iwrite1);
        //Serial.println(B3vaz);
        digitalWrite(B3IN1, LOW);        //Liga a bomba d'água
        digitalWrite(B3IN2, HIGH);
        analogWrite(B3IN2, iwrite3);
      }
    }
  }
  
  if (c == "parar") {
    digitalWrite(PINRELE, LOW);
    iwrite1 = 0;
    digitalWrite(B1IN1, LOW);        //Desliga a bomba d'água
    digitalWrite(B1IN2, HIGH);
    analogWrite(B1IN2, iwrite1);
    
    iwrite2 = 0;
    digitalWrite(B2IN1, LOW);        //Desliga a bomba d'água
    digitalWrite(B2IN2, HIGH);
    analogWrite(B2IN2, iwrite2);

    iwrite3 = 0;
    digitalWrite(B3IN1, LOW);        //Desliga a bomba d'água
    digitalWrite(B3IN2, HIGH);
    analogWrite(B3IN2, iwrite3);
    }
  delay(50);
  
  }
void setup() {
  Serial.begin(9600);
  
  //Setup do relé
  pinMode(PINRELE, OUTPUT);
  digitalWrite(PINRELE, HIGH); //Módulo relé inicia ligado 
  rele=1;
  // ISSO É FEITO PARA CORRIGIR UM PROBLEMA DE TARA NO INÍCIO
  
  //Setup das bombas
  pinMode(B1IN1,OUTPUT);
  pinMode(B1IN2,OUTPUT);
  pinMode(B2IN1,OUTPUT);
  pinMode(B2IN2,OUTPUT);
  pinMode(B3IN1,OUTPUT);
  pinMode(B3IN2,OUTPUT);

  delay(3000);
  iwrite1=158.1;
  iwrite2=160.65;
  iwrite3=165.75;
  
  digitalWrite(PINRELE, LOW); //Módulo relé inicia desligado
  delay(3000);
  rele=0;

}
 
void loop() {
  rotina();
}