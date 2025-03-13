#!/usr/bin/env python
import json
import csv
import shutil
import os


# Diretório do JSON e nome do CSV gerado
json_file_path = "db.json"
csv_output_path = "dados.csv"

def json_to_csv(json_file, csv_file):
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
        
        if isinstance(data, list) and len(data) > 0:
            with open(csv_file, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            print(f"Conversão completa! Arquivo salvo em: {csv_file}")
        else:
            print("O JSON não possui dados válidos.")
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        os.remove(csv_file)


def get_mountpoint():
    import subprocess

    mounts = subprocess.check_output(['ls', '/media/db'], text=True)

    drives = []

    for line in mounts.split('\n'):
        line = '/media/db/' + line
        drives.append(line)

    return drives

def copy_data(device:str):
    shutil.copyfile('/home/db/Documents/toymachine_app/dados.csv', device+'/dados.csv')
