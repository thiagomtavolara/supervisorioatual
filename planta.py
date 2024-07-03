import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import csv
import sys
import time
import numpy as np
import serial
import matplotlib.pyplot as plt
import pandas as pd
from serial.tools import list_ports

# utilizado para atualização dos plotes
from IPython.display import display, clear_output
#import mtxlab
import warnings
warnings.filterwarnings('ignore')


p0inicial = 0
p1inicial = 0
p2inicial = 0
p3inicial = 0

# t0min é a temperatura que da inicio ao funcionamento do controle 70-140
t0min, t0max = "70-140".split("-")
t1min, t1max = "78-82".split("-")  # 78-82
t2min, t2max = "65-79".split("-")  # 65-79
t3min, t3max = "64-66".split("-")  # 64-66

t0_sp = (int(t0max) + int(t0min))/2
t1_sp = (int(t1max) + int(t1min))/2
t2_sp = (int(t2max) + int(t2min))/2
t3_sp = (int(t3max) + int(t3min))/2

muda_sp = True  # Se "=True" a função de mudar o set-point estará ativada, para desativar "=False"
# Quantos graus vão ser alterados do set-point inicial, para diminuir basta utilizar valor negativo (°C)
quanto = 5
# Quantas medidas devem ser feitas até eu aumentar o set-point (s/5)
patamar = 180
# Tempo para desligar o sistema após atingir T3 set-point (s)
tempoparafim = 1800

primeiravez0 = False
primeiravez1 = False
primeiravez2 = False
primeiravez3 = False
primeiravezpwm = False
novoprimeiravez = True
PWM = 100
i = 0
continuar = True
print("Start")  # Printa na tela que começou e o Jupter está funcionando

# Olha quantas leituras já foram feitas e na hora de ler a serial do Arduíno faz o código desconsiderar as que já foram lidas.
tamanhomensagemsplit = 0
# Mensagem inicial que corresponde ao que o arduino já mandou para o Jupyter.
message = ''

with open("nomes.txt", "r") as nomes:
    nomeanterior = str(nomes.read())
    nome = str(int(nomeanterior) + 1)

with open("nomes.txt", "w") as nomes:
    nomes.write(nome)

medidas = 0

dt = 5.              # tempo de amostragem em segundos
eps = 0.001          # folga para garantir que não haverá atraso
dt_eps = dt - eps     # usado dentro do loop de amostragem

#t_start = 300
Tempo_final = 14400.  # tempo final em segundos
tb3 = Tempo_final - 600
tb2 = tb3 + 250
tb1 = tb2 + 250

listatempo = np.arange(0, Tempo_final+1500, dt, dtype=float)
P0 = np.zeros_like(listatempo)
P1 = np.zeros_like(listatempo)
P2 = np.zeros_like(listatempo)
P3 = np.zeros_like(listatempo)
T0 = np.zeros_like(listatempo)
T1 = np.zeros_like(listatempo)
T2 = np.zeros_like(listatempo)
T3 = np.zeros_like(listatempo)
J1 = 100*np.ones_like(listatempo)
J2 = np.zeros_like(listatempo)
J3 = np.zeros_like(listatempo)
J4 = np.zeros_like(listatempo)

T0_sp = t0_sp*np.ones_like(listatempo)
T1_sp = t1_sp*np.ones_like(listatempo)
T2_sp = t2_sp*np.ones_like(listatempo)
T3_sp = t3_sp*np.ones_like(listatempo)

# variáveis auxiliares usadas nos controladore T0
I_int1 = 0.0  # para malha 1
D_int1 = 0.0
# variáveis auxiliares usadas nos controladore T1
I_int2 = 0.0  # para malha 1
D_int2 = 0.0
# variáveis auxiliares usadas nos controladore T2
I_int3 = 0.0  # para malha 1
D_int3 = 0.0
# variáveis auxiliares usadas nos controladore T3
I_int4 = 0.0  # para malha 1
D_int4 = 0.0

tempo = 0
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de P0 naquele tempo.
Peso0 = 'Peso0:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de P1 naquele tempo.
Peso1 = 'Peso1:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de P2 naquele tempo.
Peso2 = 'Peso2:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de P3 naquele tempo.
Peso3 = 'Peso3:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de T0 naquele tempo.
Temperatura0 = 'T0:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de T1 naquele tempo.
Temperatura1 = 'T1:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de T2 naquele tempo.
Temperatura2 = 'T2:'
# Quando aparecer isso a mensagem seguinte (após um espaço) é o valor de T3 naquele tempo.
Temperatura3 = 'T3:'

# Hora de reconhecer a porta arduíno:
print("reconhecendo porta arduino")
arduino = serial.Serial(
    port="COM4",
    baudrate=9600,
)
arduino2 = serial.Serial(
    port="COM7",
    baudrate=9600,
)
arduino3 = serial.Serial(
    port="COM8",
    baudrate=9600,
)
print("Experimento:", nome)


# Função que irá ler e informar os valores de Temperatura e Peso do sistema
def leitura():
    global t3_sp
    global Tempo_final
    global tempoparafim
    global medidas
    global primeiravez0
    global primeiravez1
    global primeiravez2
    global primeiravez3
    global novoprimeiravez
    global nome
    global listatempo
    global P0
    global P1
    global P2
    global P3
    global T0
    global T1
    global T2
    global T3
    global tb1
    global tb2
    global tb3
    global patamar

    dPeso0 = 0  # Variável que diz quando foi achada a mensagem "Peso0:"
    dPeso1 = 0  # Variável que diz quando foi achada a mensagem "Peso1:"
    dPeso2 = 0  # Variável que diz quando foi achada a mensagem "Peso2:"
    dPeso3 = 0  # Variável que diz quando foi achada a mensagem "Peso3:"
    dT0 = 0  # Variável que diz quando foi achada a mensagem "T0:"
    dT1 = 0  # Variável que diz quando foi achada a mensagem "T1:"
    dT2 = 0  # Variável que diz quando foi achada a mensagem "T2:"
    dT3 = 0  # Variável que diz quando foi achada a mensagem "T3:"
    tamanhomensagemsplit = 0
    messagepesos = ''
    message = ''
    p0 = 0
    p1 = 0
    p2 = 0
    p3 = 0
    t0 = 0
    t1 = 0
    t2 = 0
    t3 = 0
    comando = "ler\r"
    arduino.write(comando.encode())  # Escreve o comando
    arduino3.write(comando.encode())  # Escreve o comando

    while len(messagepesos.split()) < 9:
        # Lê o que o arduino mandou letra por letra.
        messagem = arduino3.readline(1).decode()
        # A cada letra a variável mensagem armazena mais alguma coisa.
        messagepesos += messagem

    while len(message.split()) < 9:
        # Lê o que o arduino mandou letra por letra.
        messagem = arduino.readline(1).decode()
        # A cada letra a variável mensagem armazena mais alguma coisa.
        message += messagem

    # message.split é a mensagem separada a cada espaço, assim se separa palavra por palavra
    if(len(messagepesos.split()) > 8):
        p0 = (float(messagepesos.split()[
              1+tamanhomensagemsplit])*1000) + p0inicial
        print(messagepesos.split()[0+tamanhomensagemsplit], "%.0f" % p0)
        P0[medidas] = float(p0)
        p1 = (float(messagepesos.split()[
              3+tamanhomensagemsplit])*1000) + p1inicial
        print(messagepesos.split()[2+tamanhomensagemsplit], "%.0f" % p1)
        P1[medidas] = float(p1)
        p2 = (float(messagepesos.split()[
              5+tamanhomensagemsplit])*1000) + p2inicial
        print(messagepesos.split()[4+tamanhomensagemsplit], "%.0f" % p2)
        P2[medidas] = float(p2)
        p3 = (float(messagepesos.split()[
              7+tamanhomensagemsplit])*1000) + p3inicial
        print(messagepesos.split()[6+tamanhomensagemsplit], "%.0f" % p3)
        P3[medidas] = float(p3)
        # mensagem em forma de matriz
        mensagemusadapesos = np.delete(messagepesos.split(), 8)

    tamanhomensagemsplit = 0
    if(len(message.split()) > 8):  # message.split é a mensagem separada a cada espaço, assim se separa palavra por palavra
        um5 = message.split()[0+tamanhomensagemsplit]+" " + \
            message.split()[1+tamanhomensagemsplit]  # T0: medição
        t0 = message.split()[1+tamanhomensagemsplit]
        print(um5)
        um6 = message.split()[2+tamanhomensagemsplit]+" " + \
            message.split()[3+tamanhomensagemsplit]  # T1: medição
        t1 = message.split()[3+tamanhomensagemsplit]
        print(um6)
        um7 = message.split()[4+tamanhomensagemsplit]+" " + \
            message.split()[5+tamanhomensagemsplit]  # T2: medição
        t2 = message.split()[5+tamanhomensagemsplit]
        print(um7)
        um8 = message.split()[6+tamanhomensagemsplit]+" " + \
            message.split()[7+tamanhomensagemsplit]  # T3: medição
        t3 = message.split()[7+tamanhomensagemsplit]
        print(um8)

        # mensagem em forma de matriz
        mensagemusada = np.delete(message.split(), 8)

        for i in mensagemusada:
            if ((dT0 == 1) and (i != Temperatura0)):
                if i != "nan":
                    T0[medidas] = float(i)
                else:
                    T0[medidas] = T0[medidas - 1]
                dT0 = 0
            if (i == Temperatura0):
                dT0 = 1

            if ((dT1 == 1) and (i != Temperatura1)):
                T1[medidas] = float(i)
                dT1 = 0
            if (i == Temperatura1):
                dT1 = 1

            if ((dT2 == 1) and (i != Temperatura2)):
                T2[medidas] = float(i)
                dT2 = 0
            if (i == Temperatura2):
                dT2 = 1

            if ((dT3 == 1) and (i != Temperatura3)):
                T3[medidas] = float(i)
                dT3 = 0
                global tempo
                tempo += 5
                # listatempo[medidas]=float(i)
                # if tempo >= t_start:
                medidas += 1

            if (i == Temperatura3):
                dT3 = 1

        if ((T0[medidas - 1] > int(t0min)) or (primeiravez0)) and (Tempo_final > tempo) and (medidas % 2 == 0):
            primeiravez0 = True
            if tb1 <= tempo:
                vazaobomba("B1", 0)
            if ((T1[medidas - 1] > int(t1min)) or (primeiravez1)) and (tb1 > tempo):
                if not primeiravez1:
                    vazaobomba("B1", 80)
                    primeiravez1 = True
                if tb2 <= tempo:
                    vazaobomba("B2", 0)
                if ((T2[medidas - 1] > t2_sp) or (primeiravez2)) and (tb2 > tempo):
                    if not primeiravez2:
                        vazaobomba("B2", 65)
                        primeiravez2 = True
                    if tb3 <= tempo:
                        vazaobomba("B3", 0)
                    if ((T3[medidas - 1] > t3_sp) or (primeiravez3)) and (tb3 > tempo):
                        if not primeiravez3:
                            vazaobomba("B3", 80)

                            if muda_sp:
                                patamar += medidas
                                T1_sp[patamar:] = t1_sp + quanto
                                T2_sp[patamar:] = t2_sp + quanto
                                T3_sp[patamar:] = t3_sp + quanto
                                novoprimeiravez = False
                            else:
                                Tempo_final = tempo + tempoparafim
                                tb3 = Tempo_final - 600
                                tb2 = tb3 + 250
                                tb1 = tb2 + 250

                            primeiravez3 = True
                        elif (not novoprimeiravez) and (T3[medidas - 1] > t3_sp) and (medidas >= patamar):
                            Tempo_final = tempo + tempoparafim
                            tb3 = Tempo_final - 600
                            tb2 = tb3 + 250
                            tb1 = tb2 + 250
                            novoprimeiravez = True

                        controlador(P0, P1, P2, P3, T0, T1, T2, T3)
                    else:
                        controlador(P0, P1, P2, P3, T0, T1, T2, (T3 * 0))
                else:
                    controlador(P0, P1, P2, P3, T0, T1, (T2 * 0), (T3 * 0))
            else:
                controlador(P0, P1, P2, P3, T0, (T1 * 0), (T2 * 0), (T3 * 0))

        elif (medidas % 2 != 0):
            J1[medidas - 1] = J1[medidas - 2]
            J2[medidas - 1] = J2[medidas - 2]
            J3[medidas - 1] = J3[medidas - 2]
            J4[medidas - 1] = J4[medidas - 2]

        '''if Tempo_final <= tempo:
            with open("acao.txt", "w") as arq:
                arq.write("parar")
            arduino.write("parar\r".encode())'''
        Vaz1 = (0.000328*(J2[medidas-1] ^ 3)-0.0357 *
                (J2[medidas-1] ^ 2)+1.78*J2[medidas-1]-21.2)/233.81
        Vaz2 = (0.0258*(J3[medidas-1] ^ 2)-0.29*J3[medidas-1]+4.81)/233.81
        Vaz3 = (0.019*(J4[medidas-1] ^ 2)+0.0408*J4[medidas-1]-13.7)/233.81
        T0[medidas-1], T1[medidas-1], T2[medidas-1], T3[medidas-1], T0_sp[medidas-1], T1_sp[medidas-1], T2_sp[medidas-1], T3_sp[medidas -
                                                                                                                                1], P0[medidas-1], P1[medidas-1], P2[medidas-1], P3[medidas-1], J1[medidas-1], Vaz1, Vaz2, Vaz3, listatempo[medidas-1]

    return (p0, p1, p2, p3, t0, t1, t2, t3)

# Função que irá alterar a vazão das valvulas


def vazaobomba(bomba, vazao):
    if vazao == 0:
        vazao = 0
    else:
        vazao = (vazao//2) + 50
    vazao = int(vazao)
    vazao = str(vazao)

    while len(vazao) < 3:
        vazao = "0" + vazao

    comando = bomba + " " + vazao + "\r"
    arduino.write(comando.encode())

    # Função que irá alterar a vazão das bombas


def vazaovalvula(bomba, vazao1, vazao2, vazao3):
    vazao1 = int(vazao1//1)
    vazao1 = str(vazao1)

    while len(vazao1) < 3:
        vazao1 = "0" + vazao1
    vazao2 = int(vazao2//1)
    vazao2 = str(vazao2)

    while len(vazao2) < 3:
        vazao2 = "0" + vazao2
    vazao3 = int(vazao3//1)
    vazao3 = str(vazao3)

    while len(vazao3) < 3:
        vazao3 = "0" + vazao3

    comando = "VX " + vazao1 + " " + vazao2 + " " + vazao3 + "\r"
    arduino2.write(comando.encode())

# Função que irá alterar condição do relé
def rele(comando):
    comando += '\r'
    arduino.write(comando.encode())
    
def PWMRELE(comando,valor):
    global PWM
    PWM=int(valor)
    if (PWM>100):
        PWM=100
    if (PWM<0):
        PWM=0

# Zero_Orded (ZOH) input signal
def ZOH(t,u):
    tt=np.vstack((t,t)).T.reshape((1,len(t)*2))[0,1:]
    uu=np.vstack((u,u)).T.reshape((1,len(u)*2))[0,0:-1]
    return ((tt,uu))

def PID_p2(SP, PV,k,I_int,D_int, dt, Method = 'Backward', Kp=10.0, Ti=50.0, Td=1.0, b=1.,c=0.0,
           N=10., U_bias = 0., Umin = -100.,Umax = 100.):
    # PID -- posicional implementation
    # Para sistemas não lineares com ação integral e   b!=1 inicializar I_int =  Kp*Yset_bias*(1-b)
    # Para sistemas não lineares com ação derivativa e c!=1 inicializar D_int =  Yset_bias*(1-c)
    # The approximation of the derivative term are stable only when abs(ad)<1.
    # The forward difference approximation requires that Td>N*dt/2, i.e., the
    # approximation becomes unstable for small values of Td. The other approximation
    # are stable for all values of Td.

    # Jorge O. Trierweiler -- GIMSCOP

    if Method == 'Backward':
        b1 = Kp*dt/Ti if Ti != 0 else 0.0
        b2 = 0.0
        ad = Td/(Td+N*dt)
        bd = Kp*Td*N/(Td+N*dt)
    elif Method == 'Forward':
        b1 = 0.0
        b2 = Kp*dt/Ti  if Ti!=0 else 0.0
        ad = 1-N*dt/Td if Td!=0 else 0.0
        bd = Kp*N
    elif Method == 'Tustin':
        b1 = Kp*dt/2/Ti if Ti!=0 else 0.0
        b2 = b1
        ad = (2*Td-N*dt)/(2*Td+N*dt)
        bd = 2*Kp*Td*N/(2*Td+N*dt)
    elif Method == 'Ramp':
        b1 = Kp*dt/2/Ti if Ti!=0 else 0.0
        b2 = b1
        ad = np.exp(-N*dt/Td) if Td !=0 else 0.0
        bd = Kp*Td*(1-ad)/dt

    # Derivative Action
    D  = ad*D_int+bd*((c*SP[k]-PV[k])-(c*SP[k-1]-PV[k-1]))

    # Integral action

    II = b1*(SP[k]-PV[k])+b2*(SP[k-1]-PV[k-1])
    #II = Kp*dt/Ti*(SP[k]-PV[k]) if Ti!=0 else 0.0
    I = I_int + II


    # calculate the PID output
    P = Kp * (b*SP[k]-PV[k])

    Uop = U_bias + P + I + D

    # implement anti-reset windup

    if Uop < Umin or Uop > Umax:
        II = 0.0      # no caso de saturação -- diminuindo o valor integrado a mais
        # clip output
        Uop = max(Umin, min(Umax, Uop))

    # return the controller output and PID terms
    return np.array([Uop,I_int+II,D])


def controlador(P0, P1, P2, P3, T0, T1, T2, T3):
    global pwmrele
    global primeiravezpwm
    global t0_sp
    global t1_sp
    global t2_sp
    global t3_sp
    global J2
    global J3
    global J4
    global i
    global medidas
    global I_int1
    global D_int1
    global I_int2
    global D_int2
    global I_int3
    global D_int3
    global I_int4
    global D_int4
    
    i = medidas - 1

    # Leitura das medições

    # Ajuste do controlador Kp=20, Ti=50
    uu0  = PID_p2(T0_sp, T0,i,I_int1,D_int1, dt , Method ='Backward',U_bias=50,Umin = 0.,Umax = 100.,
                 Kp=5,Ti=650,Td=0.,N=10) # parâmetros do controlador
    J1[i] = uu0[0]
    I_int1= uu0[1]
    D_int1= uu0[2]
    

    # Ajuste do controlador Kp=-10, Ti=60
    uu1  = PID_p2(T1_sp, T1,i,I_int2,D_int2, dt , Method ='Backward',U_bias=50,Umin = 0.,Umax = 100.,
                 Kp=-5,Ti=650,Td=0.,N=10) # parâmetros do controlador
    J2[i] = uu1[0]
    I_int2= uu1[1]
    D_int2= uu1[2]
    #print("B1:", (J2[i] // 1))

    uu2  = PID_p2(T2_sp, T2,i,I_int3,D_int3, dt , Method ='Backward',U_bias=50,Umin = 0.,Umax = 100.,
                 Kp=-5,Ti=650,Td=0.,N=10) # parâmetros do controlador
    J3[i] = uu2[0]
    I_int3= uu2[1]
    D_int3= uu2[2]
    #print("B2:", (J3[i] // 1))

    # Ajuste do controlador Kp=-10, Ti=60
    uu3  = PID_p2(T3_sp, T3,i,I_int4,D_int4, dt , Method ='Backward',U_bias=50,Umin = 0.,Umax = 100.,
                 Kp=-5,Ti=650,Td=0.,N=10) # parâmetros do controlador
    J4[i] = uu3[0]
    I_int4= uu3[1]
    D_int4= uu3[2]
    #print("B3:", (J4[i] // 1))

    #or (T1[i] > 100) <<<=================================================================================================
    if (T0[i] > 100) or (primeiravezpwm):
        PWMRELE ("PWM", J1[i])
        print("PWM:", (J1[i] // 1))
        primeiravezpwm = True
    else:
        PWMRELE ("PWM", 100)
        print("PWM: 100.0")
        J1[i]=100
        
    '''vazaobomba ("B1", J2[i])
    vazaobomba ("B2", J3[i])
    vazaobomba ("B3", J4[i])'''

    print("V1:", J2[i]//1)
    print("V2:", J3[i]//1)
    print("V3:", J4[i]//1)
    vazaovalvula ("VX", J2[i],J3[i],J4[i])
    
print('')


### global PWM
while (continuar):
    with open("acao.txt", "r") as arq:
        acao = arq.read()

    if "," in acao:
        acao, valor = acao.split(",")
        print(acao.upper(), valor, end = " ")

    else:
        print(acao.upper(), end = " ")

    print("--------------------------------", "%.2f"%(float(medidas)*5/60))

    if acao == "ler":
        dt_eps = dt - eps
        eps = 0.001          # folga para garantir que não haverá atraso

        p0, p1, p2, p3, t0, t1, t2, t3 = leitura()
        start=time.time()
        if (PWM > 5) and (tempo < Tempo_final):
            rele("liga rele")
        if PWM <= 50:
            while 1:
                if (time.time() - start > PWM/10):
                    rele("desliga rele")
                    break
            PWM2=PWM
        else:
            PWM2 = PWM - 50

        while 1:
            if (time.time() - start > dt_eps):
                break  # esperando o tempo passar para ir para próxima amostragem
        start = time.time()
        dt_eps = dt - eps
        print("LER --------------------------------", "%.2f"%(float(medidas)*5/60))
        p0, p1, p2, p3, t0, t1, t2, t3 = leitura()


        while 1:
            if (time.time() - start > PWM2/10) or (tempo > Tempo_final):
                if (PWM2 < 45) or (tempo > Tempo_final):
                    rele("desliga rele")
                break

        while 1:
            if (time.time() - start > dt_eps):
                break  # esperando o tempo passar para ir para próxima amostragem

        '''if ((int(medidas) % 60) == 0):
            tempograf = time.time()
            graficopeso = px.line(title = "Pesos vs Tempo", height = 400, width = 900)
            graficopeso.update_yaxes(title = "Peso (g)")
            graficopeso.update_xaxes(title = "Tempo (min)")
            graficopeso.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=P0[:medidas], name="P0"),secondary_y=False,)
            graficopeso.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=P1[:medidas], name="P1"),secondary_y=False,)
            graficopeso.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=P2[:medidas], name="P2"),secondary_y=False,)
            graficopeso.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=P3[:medidas], name="P3"),secondary_y=False,)
            graficopeso.show()
            graficotemperatura = px.line(title = "Temperatura vs Tempo", height = 400, width = 900)
            graficotemperatura.update_yaxes(title = "Temperatura (°C)")
            graficotemperatura.update_xaxes(title = "Tempo (min)")
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T0[:medidas], name="T0"),secondary_y=False,)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T1[:medidas], name="T1"),secondary_y=False,)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T2[:medidas], name="T2"),secondary_y=False,)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T3[:medidas], name="T3"),secondary_y=False,)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T0_sp[:medidas], name="T0_sp", line = dict(width=2, dash='dot', color ='gray')),secondary_y=False)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T1_sp[:medidas], name="T1_sp",line = dict(width=2, dash='dashdot', color ='gray')),secondary_y=False)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T2_sp[:medidas], name="T2_sp",line = dict(width=2, dash='dash', color ='gray')),secondary_y=False)
            graficotemperatura.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=T3_sp[:medidas], name="T3_sp",line = dict(width=2, dash='longdash', color ='gray')),secondary_y=False)
            graficotemperatura.show()
            graficovazoes = px.line(title = "Vazões vs Tempo", height = 400, width = 900)
            graficovazoes.update_yaxes(title = "Vazões")
            graficovazoes.update_xaxes(title = "Tempo (min)")
            graficovazoes.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=J1[:medidas], name="PWM relé"),secondary_y=False,)
            graficovazoes.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=J2[:medidas], name="V1"),secondary_y=False,)
            graficovazoes.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=J3[:medidas], name="V2"),secondary_y=False,)
            graficovazoes.add_trace(go.Scatter(x=(listatempo[:medidas])/60, y=J4[:medidas], name="V3"),secondary_y=False,)
            graficovazoes.show()
            np.savez(nome,listatempo=listatempo,P0=P0,P1=P1,P2=P2,P3=P3,T0=T0,T1=T1,T2=T2,T3=T3,PWM=J1,B1=J2,B2=J3,B3=J4,T0_sp=T0_sp,T1_sp=T1_sp,T2_sp=T2_sp,T3_sp=T3_sp)
            eps = time.time() - tempograf'''

    elif (acao == "b1") or (acao == "b2") or (acao == "b3"):
        vazaobomba(acao.upper(), int(valor))
        with open("acao.txt", "w") as arq:
            arq.write("ler")
            
    elif (acao == "v1") or (acao == "v2") or (acao == "v3"):
        vazaovalvula(acao.upper(), int(valor),int(valor),int(valor))
        with open("acao.txt", "w") as arq:
            arq.write("ler")

    elif (acao == "liga rele"):
        PWMRELE("PWM", 100)
        with open("acao.txt", "w") as arq:
            arq.write("ler")

    elif (acao == "desliga rele"):
        PWMRELE("PWM", 0)
        with open("acao.txt", "w") as arq:
            arq.write("ler")

    elif acao == "parar":
        continuar = False
        with open("acao.txt", "w") as arq:
            arq.write("ler")
        arduino.write("parar\r".encode())
    
    elif acao == "muda_sp0":
        T0_sp[medidas:] = int(valor)
        with open("acao.txt", "w") as arq:
            arq.write("ler")
            
    elif acao == "muda_sp1":
        T1_sp[medidas:] = int(valor)
        with open("acao.txt", "w") as arq:
            arq.write("ler")
            
    elif acao == "muda_sp2":
        T2_sp[medidas:] = int(valor)
        with open("acao.txt", "w") as arq:
            arq.write("ler")
            
    elif acao == "muda_sp3":
        T3_sp[medidas:] = int(valor)
        with open("acao.txt", "w") as arq:
            arq.write("ler")
            
    else:
        print("Ação Inválida")
        with open("acao.txt", "w") as arq:
            arq.write("ler")
    
    if (Tempo_final + 1790) <= tempo:
        continuar = False
            
vazaovalvula("VX", 0, 0, 0)
np.savez(nome,listatempo=listatempo,P0=P0,P1=P1,P2=P2,P3=P3,T0=T0,T1=T1,T2=T2,T3=T3,PWM=J1,B1=J2,B2=J3,B3=J4,T0_sp=T0_sp,T1_sp=T1_sp,T2_sp=T2_sp,T3_sp=T3_sp)