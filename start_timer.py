try:
    import RPi.GPIO as GPIO
    print("RPi.GPIO foi importado com sucesso!")
except ImportError:
    GPIO = None
import time
import json

TIMER_STARTER_UP = 29
TIMER_STARTER_DOWN = 31
TIMER_STARTER_LEFT = 33
TIMER_STARTER_RIGHT = 35
file_path = 'timer_status.json'

if GPIO:
    GPIO.setmode(GPIO.BOARD)



def start_timer() -> bool: 

    if GPIO:
        GPIO.setup(TIMER_STARTER_UP, GPIO.IN)
        GPIO.setup(TIMER_STARTER_DOWN, GPIO.IN)
        GPIO.setup(TIMER_STARTER_LEFT, GPIO.IN)         
        GPIO.setup(TIMER_STARTER_RIGHT, GPIO.IN)
    else:

        print("Chegou")

        while True:
            if input("Aperte qualquer botao"):
                return True


    while True and GPIO:
        if GPIO.input(TIMER_STARTER_UP) == GPIO.LOW:
            print('Botao pra cima')
            update_status(1)
        elif GPIO.input(TIMER_STARTER_DOWN) == GPIO.LOW:
            print('Botao pra baixo')
            update_status(1)
        elif GPIO.input(TIMER_STARTER_LEFT) == GPIO.LOW:
            print('Botao pra esquerda')
            update_status(1)
        elif GPIO.input(TIMER_STARTER_RIGHT) == GPIO.LOW:
            print('Botao pra direita')
            update_status(1)
        else:
            update_status(0)

        time.sleep(0.2)


def update_status(new_status):
    """
    Atualiza o valor da chave 'status' em um arquivo JSON.

    Args:
        file_path (str): Caminho para o arquivo JSON.
        new_status (int): Novo valor para a chave 'status' (deve ser 0 ou 1).

    Raises:
        ValueError: Se o novo valor não for 0 ou 1.
        FileNotFoundError: Se o arquivo JSON não existir.
    """
    if new_status not in (0, 1):
        raise ValueError("O valor de 'status' deve ser 0 ou 1.")

    try:
        # Lê o conteúdo do arquivo JSON
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Atualiza o valor da chave 'status'
        data['status'] = new_status

        # Escreve o conteúdo atualizado de volta no arquivo
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"Chave 'status' atualizada para {new_status}.")
    except FileNotFoundError:
        raise FileNotFoundError(f"O arquivo '{file_path}' não foi encontrado.")
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON. Verifique se ele está correto.")

# threading.Thread(target=start_timer, daemon=True).start()
teste = start_timer()