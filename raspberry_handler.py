try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None
import time
import json
import os
import platform
from threading import Thread

MACHINE_COMMAND = 11
COMMAND_DURATION = 2

TIMER_STARTER_UP = 29
TIMER_STARTER_DOWN = 31
TIMER_STARTER_LEFT = 33
TIMER_STARTER_RIGHT = 35

TIMER_STOPPER = 13

if GPIO:
    print("Configurando GPIO...")
    GPIO.setmode(GPIO.BOARD)

def update_status(mode:int, new_status):
    # Caminho para o arquivo JSON
    system = platform.system()

    if system == 'Windows':
        json_file = "timer_status.json"
        print("System identified: ", system)
    elif system == 'Linux':
        json_file = "/home/db/Documents/toymachine_app/timer_status.json"
        print("System identified: ", system)
    
    # Verifica se o arquivo JSON já existe
    if os.path.exists(json_file):
        # Carrega o conteúdo do arquivo JSON
        print('json file loaded.')
        with open(json_file, "r") as file:
            data = json.load(file)
    else:
        # Cria um novo JSON com a chave "status" definida como 0
        data = {"status": 0}
    
    # Atualiza o valor da chave "status"

    if mode == 0:
        data["status"] = new_status
        data["stop"] = 0
        print(f"Status atualizado para {new_status} no arquivo JSON.")
    elif mode == 1:
        data["status"] = 0
        data["stop"] = new_status
        print(f"Stop atualizado para {new_status} no arquivo JSON.")
    
    # Salva o arquivo JSON com o novo valor
    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)
        file.flush()
        os.fsync(file.fileno())  # Garante que os dados foram escritos no disco
        print('Data:')
        print(data)

def start_game():
    print("-------- JOGO COMECA --------")
    if GPIO:
        GPIO.setup(MACHINE_COMMAND, GPIO.OUT)
        time.sleep(COMMAND_DURATION)
        GPIO.setup(MACHINE_COMMAND, GPIO.IN)

def start_timer(): 
    print("Inicializando a funcao de deteccao...")
    if GPIO:
        print("Configurando pinos do GPIO...")
        GPIO.setup(TIMER_STARTER_UP, GPIO.IN)
        GPIO.setup(TIMER_STARTER_DOWN, GPIO.IN)
        GPIO.setup(TIMER_STARTER_LEFT, GPIO.IN)         
        GPIO.setup(TIMER_STARTER_RIGHT, GPIO.IN)

        while True:
            print("Aguardando alteracoes no GPIO...")
            if GPIO.input(TIMER_STARTER_UP) == GPIO.LOW:
                print('Botao pra cima')
                update_status(0, 1)  # Atualiza o status no JSON para 1
                return True
            elif GPIO.input(TIMER_STARTER_DOWN) == GPIO.LOW:
                print('Botao pra baixo')
                update_status(0, 1)
                return True
            elif GPIO.input(TIMER_STARTER_LEFT) == GPIO.LOW:
                print('Botao pra esquerda')
                update_status(0, 1)
                return True
            elif GPIO.input(TIMER_STARTER_RIGHT) == GPIO.LOW:
                print('Botao pra direita')
                update_status(0, 1)
                return True

            time.sleep(0.2)
    else:
        update_status(0, 0)
        return False
    
def start_timer_thread():
    print("Iniciando Thread...")
    result = [False]  # Usamos uma lista para armazenar o resultado (mutável)
    
    def thread_target():
        result[0] = start_timer()  # Armazena o resultado da função start_timer
    
    thr = Thread(target=thread_target)
    print("Thread iniciada: ", thr)
    thr.daemon = True
    thr.start()
    return result  # Retorna a lista para que o valor possa ser verificado posteriormente


def stop_timer(): 
    print("Inicializando a funcao...")
    if GPIO:
        print("Configurando GPIO...")
        GPIO.setup(TIMER_STOPPER, GPIO.IN)

        while True:
            print("Aguardando alteracoes no GPIO...")
            if GPIO.input(TIMER_STOPPER) == GPIO.LOW:
                print('Botao pressionado')
                update_status(1, 1)  # Atualiza o status no JSON para 1
                return True
            time.sleep(0.2)
    else:
        update_status(0)
        return False
    
def stop_timer_thread():
    print("Iniciando Thread...")
    result = [False]  # Usamos uma lista para armazenar o resultado (mutável)
    
    def thread_target():
        result[0] = stop_timer()  # Armazena o resultado da função start_timer
    
    thr = Thread(target=thread_target)
    print("Thread iniciada: ", thr)
    thr.daemon = True
    thr.start()
    return result  # Retorna a lista para que o valor possa ser verificado posteriormente
