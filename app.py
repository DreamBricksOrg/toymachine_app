from flask import Flask, render_template, request, redirect, send_file
from raspberry_handler import start_game, start_timer_thread, stop_timer_thread, update_status
from data_handler import json_to_csv, get_mountpoint, copy_data
from datetime import datetime
import json, csv
import platform
import os
import requests

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
    now = datetime.now()
    weekday = now.strftime('%A')
    date = now.strftime('%d/%m/%Y')
    time = now.strftime('%H:%M:%S')
    iso_datetime = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    return weekday, date, time, iso_datetime

def database_sync():
    try:
        r = requests.get('https://dbutils.ddns.net/datalog/getdatabyproject?project=ciclic_vending_machine')
        if r.status_code == 200:
            response_data = r.json()
            
            if 'data' in response_data and len(response_data['data']) > 0:

                additional_data = response_data['data'][-1].get('additional')
                print("Additional data:", additional_data)
                
                # Read all lines from CSV file
                with open(encrypted_path, "r", encoding="utf-8") as f:
                    lines = list(csv.reader(f, delimiter=' '))
                    if lines:
                        for line in lines:
                            if additional_data == lines[-1]:
                                print("Data already synced")
                                return additional_data, None
                            else:
                                print("Data not synced")
                                print("Not synced data:", line[0])
                                date_and_time = get_current_datetime()
                                obj_to_sync = {
                                    "status" : "jogou",
                                    "project" : "67d358c732f32712b51c5aeb",
                                    "additional" : str(line[0]),
                                    "timePlayed" : str(date_and_time[3])  # Get the ISO formatted datetime
                                }
                                print("Object to sync:", obj_to_sync)
                                try:
                                    x = requests.post('https://dbutils.ddns.net/datalog/upload', json=obj_to_sync)
                                    print("Data synced:", x.text)
                                except requests.exceptions.RequestException as e:
                                    print("Error fetching data:", e)
                                
                    else:
                        print("CSV file is empty")
                        return additional_data, None
                        
            else:
                print("No data found in response")
                return None, None
                
    except FileNotFoundError:
        print(f"File not found: {encrypted_path}")
        return None, None
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None, None
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return None, None

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
    sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        return False

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
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
    try:
        with open(database_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = None

    if data:
        json_to_csv(database_path, csv_path)


    
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
            data.append({'Nome': name, 'Email': email, 'Telefone': cellphone, 'CPF': cpf, 'Protecoes': protections, 'Hora': play_datetime[2], 'Data': play_datetime[1]})
            with open(database_path, "w", encoding="utf-8") as arquivo:
                json.dump(data, arquivo, ensure_ascii=False, indent=4)
            message=None
            form_data = None
            start_game()
            return redirect('/maquinaliberada')
        else:
            message = "Por favor, insira um número de CPF válido."
            error = "CPF"

    return render_template('register.html', message=message, form_data=form_data, form_error=error)

@app.route('/maquinaliberada')
def gamestarted():

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
        #print("Alias", alias)
        #print(alias[-1])
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

    #print("Current datetime: ", now)
    #print("Datetime update command: ", datetime_command)

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
def encripter():
    if request.method == 'POST':
        print("Request received")
        if 'file' not in request.files:
            print("No file in request")
            return render_template('encripter.html', message="Nenhum arquivo foi enviado.")
            
        file = request.files['file']
        print("File received:", file.filename)
        
        if file.filename == '':
            return render_template('encripter.html', message="Nenhum arquivo foi selecionado.")
        
        if file:
            # Save encrypted file
            save_path = os.path.join(app.root_path, 'dados_encrypted.csv')
            file.save(save_path)
            print("File saved to:", save_path)
            return render_template('encripter.html', message="Arquivo encriptado com sucesso!")
    else:
        return send_file('dados_encrypted.csv', mimetype='text/csv')
    
    return render_template('encripter.html')

@app.route('/dados.csv')
def get_csv():
    return send_file('dados.csv', mimetype='text/csv')

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')



database_sync()

if __name__ == "__main__":
    app.run(debug=True, port="5000", host="0.0.0.0")
