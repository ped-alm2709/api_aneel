from flask import Flask, render_template, send_from_directory, jsonify
from collections import defaultdict
import matplotlib.pyplot as plt
import urllib.request
import requests
import random
import json
import csv
import os


app = Flask(__name__)

plt.switch_backend('Agg')

url = 'https://dadosabertos.aneel.gov.br/api/3/action/datastore_search?resource_id=b1bd71e7-d0ad-4214-9053-cbd58e9564a7'

@app.route('/')
def home():
    # Fazer a requisição para a API
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print(f"Erro na requisição: {e.code} - {e.reason}")
        return 'Falha ao fazer a requisição de dados.'

    # Ler os dados da resposta
    try:
        data = json.load(response)
        result = data['result']
        records = result['records']

        # Criar dicionários para armazenar os dados
        empreendimentos_por_classe_estado = defaultdict(int)
        potencia_instalada_por_estado = defaultdict(float)
        empreendimentos_por_mes_estado_classe = defaultdict(int)
        meses = []

        # Processar os registros e agregar os dados mensalmente
        for record in records:
            atualizacao_cadastral = record['DthAtualizaCadastralEmpreend']
            classe_consumo = record['DscClasseConsumo']
            potencia_instalada_str = record['MdaPotenciaInstaladaKW']
            potencia_instalada_str = potencia_instalada_str.replace(',', '.')  # Substituir vírgula por ponto
            potencia_instalada = float(potencia_instalada_str)
            estado = record['SigUF']
            _id = record['_id']

            # Extrair o mês da atualização cadastral
            mes_atualizacao = int(atualizacao_cadastral.split('-')[1])
            meses.append(mes_atualizacao)
            mes = mes_atualizacao

            # Verificar se o mês está dentro do intervalo desejado (exemplo: janeiro a dezembro de 2023)
            if mes_atualizacao >= 1 and mes_atualizacao <= 12:
                # Atualizar as contagens de empreendimentos por mês, estado e classe
                empreendimentos_por_mes_estado_classe[(mes_atualizacao, estado, classe_consumo)] += 1

                # Atualizar as contagens de empreendimentos por classe e estado
                empreendimentos_por_classe_estado[(classe_consumo, estado)] += 1

                # Atualizar a potência instalada por estado
                potencia_instalada_por_estado[estado] += potencia_instalada

        # Caminho para a pasta static
        static_folder = os.path.join(app.root_path, 'static')
        
        # Exportar para JSON
        empreendimentos_json = []
        for classe_estado, empreendimentos in empreendimentos_por_classe_estado.items():
            classe_consumo, estado = classe_estado
            potencia_instalada_estado = potencia_instalada_por_estado[estado]
            empreendimentos_json.append({
                '_id': _id,
                'Classe Consumo': classe_consumo,
                'Estado': estado,
                'Total de Empreendimentos': empreendimentos,
                'Potência Instalada (KW)': potencia_instalada_estado,
                'Mes': mes
            })

        with open(os.path.join(static_folder,'empreendimentos.json'), 'w', encoding='utf-8') as json_file:
            json.dump(empreendimentos_json, json_file, indent=4, ensure_ascii=False)

        # Exportar para CSV
        with open(os.path.join(static_folder, 'dados.csv'), 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['_id', 'Classe Consumo', 'Estado', 'Total de Empreendimentos', 'Potência Instalada (KW)', 'Mês'])
            for classe_estado, empreendimentos in empreendimentos_por_classe_estado.items():
                classe_consumo = classe_estado[0]
                estado = classe_estado[1]
                potencia_instalada = potencia_instalada_por_estado[estado]
                writer.writerow([_id, classe_consumo, estado, empreendimentos, potencia_instalada, mes])

        return render_template('index.html')

    except json.JSONDecodeError as e:
        print(f"Erro na leitura dos dados JSON: {e}")
        return 'Falha ao ler os dados da resposta.'

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)         

@app.route('/empreendimentos')
def consultar_empreendimentos():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            empreendimentos = dados['result']['records']
            return jsonify(empreendimentos)
        else:
            return jsonify({'message': 'Falha na solicitação'})
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})

@app.route('/potencia_instalada')
def consultar_potencia_instalada():
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica se ocorreu um erro na solicitação HTTP

        dados = response.json()
        potencia_instalada = {}

        for registro in dados['result']['records']:
            estado = registro['SigUF']
            potencia = registro['MdaPotenciaInstaladaKW'].replace(',', '.')

            if estado in potencia_instalada:
                potencia_instalada[estado] += float(potencia)
            else:
                potencia_instalada[estado] = float(potencia)

        return jsonify(potencia_instalada)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})
    
@app.route('/empreendimentos_classe')
def consultar_total_empreendimentos():
    try:
        response = requests.get(url)
        response.raise_for_status()

        dados = response.json()
        empreendimentos = {}

        for registro in dados['result']['records']:
            classe = registro['DscClasseConsumo']
            estado = registro['SigUF']

            if classe in empreendimentos:
                if estado in empreendimentos[classe]:
                    empreendimentos[classe][estado] += 1
                else:
                    empreendimentos[classe][estado] = 1
            else:
                empreendimentos[classe] = {estado: 1}

        return jsonify(empreendimentos)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})
    
@app.route('/dados_organizados')
def consultar_dados_organizados():
    try:
        response = requests.get(url)
        response.raise_for_status()

        dados = response.json()
        dados_organizados = []

        for registro in dados['result']['records']:
            dado = {
                'ID': registro['_id'],
                'DscClasseConsumo': registro['DscClasseConsumo'],
                'MdaPotenciaInstaladaKW': registro['MdaPotenciaInstaladaKW'],
                'SigUF': registro['SigUF'],
                'DatGeracaoConjuntoDados': registro['DatGeracaoConjuntoDados'],
                'DthAtualizaCadastralEmpreend': registro['DthAtualizaCadastralEmpreend'],
            }
            dados_organizados.append(dado)

        # Salvando os dados em um arquivo JSON
        json_path = os.path.join('static', 'dados_organizados.json')
        with open(json_path, 'w') as json_file:
            json.dump(dados_organizados, json_file, indent=4)

        # Salvando os dados em um arquivo CSV
        csv_path = os.path.join('static', 'dados_organizados.csv')
        with open(csv_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=dados_organizados[0].keys())
            writer.writeheader()
            writer.writerows(dados_organizados)

        return jsonify(dados_organizados)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})
    
def random_color():
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            return f'rgb({r}, {g}, {b})'

@app.route('/grafico.html')
def exibir_grafico():
    return render_template('grafico.html')

@app.route('/dados_grafico')
def obter_dados_grafico():
    try:
        response = requests.get(url)
        response.raise_for_status()

        dados = response.json()
        dados_grafico = {
            'labels': [],
            'datasets': []
        }

        estados = set()
        classes = set()

        for registro in dados['result']['records']:
            data = registro['DthAtualizaCadastralEmpreend'][:7]  # Extrai o ano e mês da data
            estado = registro['SigUF']
            classe = registro['DscClasseConsumo']

            if data not in dados_grafico['labels']:
                dados_grafico['labels'].append(data)

            if estado not in estados:
                estados.add(estado)

            if classe not in classes:
                classes.add(classe)

        for estado in estados:
            dataset = {'label': estado, 'data': [], 'backgroundColor': random_color()}
            for data in dados_grafico['labels']:
                total_empreendimentos = 0
                for registro in dados['result']['records']:
                    if registro['SigUF'] == estado and registro['DthAtualizaCadastralEmpreend'][:7] == data:
                        total_empreendimentos += 1
                dataset['data'].append(total_empreendimentos)
            dados_grafico['datasets'].append(dataset)

        return jsonify(dados_grafico)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})

@app.route('/grafico2.html')
def exibir_grafico2():
    return render_template('grafico2.html')
    
@app.route('/dados_grafico2')
def obter_dados_grafico2():
    try:
        response = requests.get(url)
        response.raise_for_status()

        dados = response.json()
        dados_grafico = {
            'labels': [],
            'datasets': []
        }

        estados = set()

        for registro in dados['result']['records']:
            data = registro['DthAtualizaCadastralEmpreend'][:7]  # Extrai o ano e mês da data
            estado = registro['SigUF']
            potencia = registro['MdaPotenciaInstaladaKW'].replace(',', '.')  # Substitui vírgula por ponto para conversão em float

            if estado not in estados:
                estados.add(estado)

        for estado in estados:
            dataset = {'label': estado, 'data': [], 'backgroundColor': random_color()}
            for registro in dados['result']['records']:
                if registro['SigUF'] == estado:
                    potencia_total = float(registro['MdaPotenciaInstaladaKW'].replace(',', '.'))
                    dataset['data'].append(potencia_total)
                    if registro['DthAtualizaCadastralEmpreend'][:7] not in dados_grafico['labels']:
                        dados_grafico['labels'].append(registro['DthAtualizaCadastralEmpreend'][:7])

            dados_grafico['datasets'].append(dataset)

        return jsonify(dados_grafico)
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Erro na solicitação: ' + str(e)})

@app.route('/grafico3.html')
def exibir_grafico3():
    return render_template('grafico3.html')
    
@app.route('/dados_grafico3')
def gerar_grafico_correlacao3():
    try:
        response = requests.get(url)
        response.raise_for_status()

        dados = response.json()
        registros = dados['result']['records']

        datasets = {}
        labels = set()

        for registro in registros:
            porte = registro['DscPorte']
            fonte = registro['DscFonteGeracao']
            potencia = registro['MdaPotenciaInstaladaKW'].replace(',', '.')

            chave = (porte, fonte)
            if chave not in datasets:
                datasets[chave] = {
                    'label': f'{porte} - {fonte}',
                    'data': [],
                    'backgroundColor': random_color()
                }

            datasets[chave]['data'].append(float(potencia))
            labels.add(f'{porte} - {fonte}')

        dados_grafico = {
            'labels': list(labels),
            'datasets': list(datasets.values())
        }

        return jsonify(dados_grafico)
    except requests.exceptions.RequestException as e:
        return f'Erro na solicitação: {str(e)}'

if __name__ == '__main__':
    app.run()
