from flask import Flask, render_template, request, redirect, send_file, url_for

from dbcrypt import db_encrypt_string
from raspberry_handler import start_game, start_timer_thread, stop_timer_thread, update_status
from data_handler import json_to_csv, get_mountpoint, copy_data
from datetime import datetime
import json, csv
import platform
import os
import requests

from rsa_public_key import get_rsa_public_key

app = Flask(__name__)
system = platform.system()

if system == 'Windows':
    database_path = "db.json"
    csv_path = "dados.csv"
    encrypted_path = "dados_encrypted.csv"
    config_path = "config.json"
    print("System identified: ", system)
elif system == 'Linux':
    database_path = "/home/db/Documents/toymachine_app/db.json"
    csv_path = "/home/db/Documents/toymachine_app/dados.csv"
    encrypted_path = "/home/db/Documents/toymachine_app/dados_encrypted.csv"
    config_path = "/home/db/Documents/toymachine_app/config.json"
    print("System identified: ", system)


def get_current_datetime():
    time_played = datetime.now()
    formatted_time_played = time_played.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted_time_played


def database_sync():
    try:
        # Obter todos os objetos do servidor
        response = requests.get('https://dbutils.ddns.net/datalog/getdatabyproject?project=ciclic_vending_machine')
        response.raise_for_status()
        server_data = response.json().get("data", [])

        # Extrair todos os valores de "additional" do servidor
        print("Dados do servidor:", server_data)
        if not server_data:
            print("Nenhum dado encontrado no servidor.")
            server_additional_value = None
            sync_data = True
        else:
            server_additional_value = server_data[-1].get("additional")
            sync_data = False
        print("Ultimo valor no servidor:", server_additional_value)
    except requests.exceptions.RequestException as e:
        print("Erro ao obter dados do servidor:", e)
        return

    # Ler o arquivo criptografado
    try:
        with open(encrypted_path, "r", encoding="utf-8") as f:
            lines = list(csv.reader(f, delimiter=' '))
    except FileNotFoundError:
        print("Arquivo criptografado não encontrado.")
        return

    if not lines:
        print("Arquivo criptografado está vazio.")
        return

    if lines[-1][0] == server_additional_value:
        print("Último valor já sincronizado.")
        return

    # print("\n")

    # Iterar pelas linhas e sincronizar os objetos que não estão no servidor
    for line in lines:
        print("\n")
        print("Dado deve ser sincronizado: ", sync_data)
        if not line:
            continue
        additional_value = line[0]
        """if additional_value in server_additional_value:
            print(f"Valor '{additional_value}' já sincronizado. Pulando...")
            continue"""

        # Criar o objeto para sincronizar
        time_played = datetime.now()
        formatted_time_played = time_played.strftime("%Y-%m-%dT%H:%M:%SZ")
        status = "JOGOU"
        project = "67d358c732f32712b51c5aeb"

        obj_to_sync = {
            'status': status,
            'project': project,
            'additional': additional_value,
            'timePlayed': formatted_time_played
        }
        print("Objeto a ser sincronizado:", obj_to_sync)

        # Fazer o POST do objeto
        try:
            post_response = requests.post('https://dbutils.ddns.net/datalog/upload', data=obj_to_sync)
            post_response.raise_for_status()
            print("Dados sincronizados com sucesso:", post_response.text)
        except requests.exceptions.RequestException as e:
            print("Erro ao sincronizar dados:", e)

        if additional_value == server_additional_value:
            print("Último valor sincronizado encontrado.")
            sync_data = True


def phone_validator(cellphone: str) -> bool:
    streak = 0

    numbers = [int(digit) for digit in cellphone if digit.isdigit()]

    if len(numbers) < 10 or len(set(numbers)) == 1:
        return False

    print("Streak testada: ", streak)

    if streak >= 10:
        return False
    else:
        return True


def cpf_validator(cpf: str) -> bool:
    """ Efetua a validação do CPF, tanto formatação quando dígito verificadores.

    Parâmetros:
        cpf (str): CPF a ser validado

    Retorno:
        bool:
            - Falso, quando o CPF não possuir o formato 999.999.999-99;
            - Falso, quando o CPF não possuir 11 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    >>> validate('529.982.247-25')
    True
    >>> validate('52998224725')
    False
    >>> validate('111.111.111-11')
    False
    """

    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    if cpf == "010.010.010-10":
        return True

    # Verifica se o CPF possui 11 números ou se todos são iguais:
    if len(numbers) != 11 or len(set(numbers)) == 1:
        return False

    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a * b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        return False

    return True


def existent_cpf(cpf: str) -> bool:
    print("Verificando CPF...")
    if cpf == "010.010.010-10":
        return False

    try:
        with open(database_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    for dado in data:
        print("\nVerificando:  ")
        print(dado)
        if dado.get("CPF") == cpf:
            print("CPF já existente:", dado)
            return True
        else:
            print("Nenhum CPF igual foi encontrado.")

    return False


@app.route('/', methods=['GET'])  # Call to Action
def index():
    database_sync()
    return render_template('index.html', data=csv_path)


@app.route('/conheca', methods=['GET'])
def about():
    return render_template('about.html')


@app.route('/protecoes', methods=['GET'])
def products():
    return render_template('products.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def register():
    message = None
    error = None
    form_data = {}

    if request.method == 'POST':

        try:
            with open(database_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        name = request.form['user']
        email = request.form['email']
        cellphone = request.form['cellphone']
        cpf = request.form['cpf']
        protections = request.form.getlist('protections')
        play_datetime = get_current_datetime()

        form_data = {
            'user': name,
            'email': email,
            'cellphone': cellphone,
            'cpf': cpf,
            'protections': protections
        }

        print("CPF informado: ", cpf)

        if name == 'CiclicAdmin' and email == 'admin@admin':
            return redirect('/admin')

        if not name:
            message = "Por favor, insira seu nome."
            error = "Nome"
        elif not email:
            message = "Por favor, insira seu e-mail."
            error = "Email"
        elif not request.form.getlist('protections'):
            message = "Por favor, selecione qual a proteção mais adequada para você!"
            error = "Protecoes"
        elif cpf_validator(cpf) == True and existent_cpf(cpf) == True:
            message = "O CPF informado já está cadastrado."
            error = "CPF"
        elif phone_validator(cellphone) == False:
            message = "Por favor, insira um número de celular válido."
            error = "Celular"
        elif cpf_validator(cpf) == True and existent_cpf(cpf) == False and phone_validator(cellphone) == True:
            data.append({'Nome': name, 'Email': email, 'Telefone': cellphone, 'CPF': cpf, 'Protecoes': protections,
                         'Hora': play_datetime[2], 'Data': play_datetime[1]})
            with open(database_path, "w", encoding="utf-8") as arquivo:
                json.dump(data, arquivo, ensure_ascii=False, indent=4)
            message = None
            form_data = None
            try:
                with open(database_path, "r") as file:
                    data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                data = None

            if data:
                json_to_csv(database_path, csv_path)
            return redirect('/maquinaliberada')
        else:
            message = "Por favor, insira um número de CPF válido."
            error = "CPF"

    return render_template('register.html', message=message, form_data=form_data, form_error=error)


@app.route('/maquinaliberada')
def gamestarted():
    start_game()
    encrypt_and_send_last_line()
    moved = start_timer_thread()
    print('Resultado:  ', moved)

    return render_template('gamestarted.html')


@app.route('/timer')
def timer():
    playtime = 45
    pressed = stop_timer_thread()
    print('Resultado: ', pressed)

    return render_template('timer.html', playtime=playtime)


@app.route('/file.json')
def get_json():
    return send_file('config.json', mimetype='application/json')


@app.route('/obrigado')
def thanks():
    update_status(0, 0)
    update_status(1, 0)
    # database_sync()
    return render_template('thanks.html'), {"Refresh": "7, url=/"}


@app.route('/foradeservico')
def oos():
    return render_template('oos.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    system = platform.system()

    if system == 'Windows':
        devices = "home/db/Documents/toymachine_app/db.json"
    elif system == 'Linux':
        devices = get_mountpoint()

    aliases = []

    devices = "home/db/Documents/toymachine_app/db.json"
    for device in devices:
        alias = device.rsplit('/', 1)
        # print("Alias", alias)
        # print(alias[-1])
        if alias[-1]:
            aliases.append(alias[-1])

    if not aliases:
        alias = None
    elif aliases:
        alias = aliases[0]

    print(aliases)

    # Carrega o conteúdo do arquivo JSON
    with open(config_path, "r") as file:
        data = json.load(file)
        print('json file loaded.')

    print("------ Inactivity time: ", data["inactivity_time"])

    current_inactivity = int(data["inactivity_time"]) / 1000

    now = get_current_datetime()
    date_formmater = now[1].split('/')
    datetime_command = date_formmater[-1] + "/" + date_formmater[1] + "/" + date_formmater[0] + " " + now[2]

    # print("Current datetime: ", now)
    # print("Datetime update command: ", datetime_command)

    if request.method == 'POST':

        print("Botão pressionado: ", request.form["submit_button"])

        if request.form["submit_button"] == 'start':

            try:
                with open(database_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
            except (FileNotFoundError, json.JSONDecodeError):
                data = []

            data.append({'Nome': "Admin", 'Email': "admin", 'Telefone': "None", 'CPF': "None", 'Protecoes': "None"})
            with open(database_path, "w", encoding="utf-8") as arquivo:
                json.dump(data, arquivo, ensure_ascii=False, indent=4)
            start_game()
            return redirect('/maquinaliberada')

        elif request.form["submit_button"] == "copy":

            json_to_csv(database_path, csv_path)
            print("Pendrive montado em: ", devices)
            print("request para montar em: ", devices[0])
            copy_data(devices[0])

        elif request.form["submit_button"] == "delete":

            os.remove(database_path)
            print("Arquivo deletado: ", database_path)

        elif request.form["submit_button"] == "set":

            inactivity_timer = request.form['inactivity']

            # Atualiza o valor da chave "status"
            data["inactivity_time"] = int(inactivity_timer) * 1000

            # Salva o arquivo JSON com o novo valor
            with open(config_path, "w") as file:
                json.dump(data, file, indent=4)
                file.flush()

            return redirect('/admin')

        elif request.form["submit_button"] == "setdatetime":

            print("Definir hora")
            print("Request de atualizar data: ", request.form['dateupdater'])

            if system == 'Windows':
                print("System identified: ", system)
            elif system == 'Linux':
                print("System identified: ", system)
                now = request.form['timeupdater']
                print("Hora atual: ", now)
                date_updater = request.form['dateupdater']
                print("Data formatada: ", date_updater)
                datetime_command = "date +%Y%m%d -s" + date_updater
                print("Comando de atualização de data e hora: ", datetime_command)
                os.system(datetime_command)
                datetime_command = "date +%T -s " + now + ":00"
                os.system(datetime_command)
                #subprocess.call(['timedatectl', 'set-ntp', 'false'], shell=True) # Disable network time
                #subprocess.call(['date', '+%Y%m%d', '-s', '2025-02-19'], shell=True) #Sets system time

            return redirect('/admin')


    return render_template('admin.html', devices=alias, inactivity_timer=current_inactivity, current_datetime=now)


@app.route('/start')
def start():
    return redirect('/timer')


@app.route('/dados')
def data():
    return render_template('dados.html')


@app.route('/cryptography', methods=['GET', 'POST'])
def cryptography():
    if request.method == 'POST':
        print("Request received on cryptohgraphy!")
        print("Request form: ", request.files)
    return render_template('download.html')


@app.route('/encrypter', methods=['GET', 'POST'])
def encrypter():
    """
    Recebe uma linha criptografada e a adiciona ao arquivo dados_encrypted.csv.
    """
    if request.method == 'POST':
        # Verificar se o campo 'line' está presente na requisição
        print("* * Request received on encrypter!")
        encrypted_line = request.form.get('line')
        if not encrypted_line:
            print("- Nada recebido!")
            return "<html><body><h1>Erro: Nenhuma linha criptografada enviada!</h1></body></html>", 400

        try:
            # Adicionar a linha criptografada ao final do arquivo dados_encrypted.csv
            with open(encrypted_path, "a", encoding="utf-8") as file:
                file.write(encrypted_line + "\n")
            print("Linha criptografada adicionada ao arquivo:", encrypted_line)
            return "<html><body><h1>Linha adicionada com sucesso ao arquivo dados_encrypted.csv!</h1></body></html>", 200
        except Exception as e:
            print("Erro ao salvar a linha criptografada:", e)
            return "<html><body><h1>Erro ao salvar a linha criptografada!</h1></body></html>", 500
    elif request.method == 'GET':
        #print("Request received on encrypter!")
        return send_file('dados_encrypted.csv', mimetype='text/csv')


@app.route('/dados.csv')
def get_csv():
    print("* *  Request received on dados.csv!")
    return send_file('dados.csv', mimetype='text/csv')


@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')


def encrypt_and_send_last_line():
    # Obtém a última linha do CSV
    line = fetch_last_line_from_csv()
    if not line:
        print('Nenhuma linha válida encontrada no CSV.')
        return

    # Encripta a linha usando a chave pública RSA
    rsa_public_key = get_rsa_public_key()
    data_encrypted = db_encrypt_string(line, rsa_public_key)

    # Cria o payload para o POST
    payload = {
        'line': data_encrypted
    }

    print('Linha encriptada:', data_encrypted)

    try:

        url_encrypt = url_for('encrypter', _external=True)
        # Faz o POST no endpoint /encrypter
        response = requests.post(url_encrypt, data=payload)

        if response.ok:
            print('Linha encriptada enviada com sucesso:', data_encrypted)
        else:
            print('Erro ao enviar a linha encriptada:', response.status_code, response.text)
    except Exception as e:
        print('Erro na requisição de salvamento:', e)


def fetch_last_line_from_csv():
    try:
        url = url_for('get_csv', _external=True)
        response = requests.get(url, headers={'Cache-Control': 'no-cache'})

        if not response.ok:
            print('Erro ao buscar o arquivo CSV:', response.status_code)
            return None

        # Obtém o conteúdo do CSV como texto
        csv_text = response.text

        # Divide o conteúdo em linhas e obtém a última linha não vazia
        lines = [line for line in csv_text.split('\n') if line.strip() != '']
        if not lines:
            print('O arquivo CSV está vazio.')
            return None

        last_line = lines[-1]
        print('Última linha do CSV:', last_line)
        return last_line

    except Exception as e:
        print('Erro ao buscar a última linha do CSV:', e)
        return None


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
