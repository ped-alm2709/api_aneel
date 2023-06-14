from flask import Flask, render_template, url_for, send_from_directory
from collections import defaultdict
import matplotlib.pyplot as plt
import urllib.request
import json
import csv
import os


app = Flask(__name__)

@app.route('/')
def home():
    # Definir o URL da API da ANEEL
    url = 'https://dadosabertos.aneel.gov.br/api/3/action/datastore_search?resource_id=b1bd71e7-d0ad-4214-9053-cbd58e9564a7&limit=1000'

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

        # Processar os registros e agregar os dados mensalmente
        for record in records:
            atualizacao_cadastral = record['DthAtualizaCadastralEmpreend']
            classe_consumo = record['DscClasseConsumo']
            potencia_instalada_str = record['MdaPotenciaInstaladaKW']
            potencia_instalada_str = potencia_instalada_str.replace(',', '.')  # Substituir vírgula por ponto
            potencia_instalada = float(potencia_instalada_str)
            estado = record['SigUF']

            # Extrair o mês da atualização cadastral
            mes_atualizacao = atualizacao_cadastral.split('-')[1]

            # Verificar se o mês está dentro do intervalo desejado (exemplo: janeiro a dezembro de 2023)
            if mes_atualizacao >= '01' and mes_atualizacao <= '12':
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
            empreendimentos_json.append({
                'Classe Consumo': classe_consumo,
                'Estado': estado,
                'Total de Empreendimentos': empreendimentos
            })

        with open(os.path.join(static_folder,'empreendimentos.json'), 'w', encoding='utf-8') as json_file:
            json.dump(empreendimentos_json, json_file, indent=4, ensure_ascii=False)

        # Exportar para CSV
        with open(os.path.join(static_folder, 'dados.csv'), 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Classe Consumo', 'Estado', 'Total de Empreendimentos', 'Potência Instalada (KW)'])
            for classe_estado, empreendimentos in empreendimentos_por_classe_estado.items():
                classe_consumo = classe_estado[0]
                estado = classe_estado[1]
                potencia_instalada = potencia_instalada_por_estado[estado]
                writer.writerow([classe_consumo, estado, empreendimentos, potencia_instalada])
        return render_template('index.html')

    except json.JSONDecodeError as e:
        print(f"Erro na leitura dos dados JSON: {e}")
        return 'Falha ao ler os dados da resposta.'            

@app.route('/dados')
def dados():
    try:
        # Caminho para o arquivo "empreendimentos.json" na pasta "static"
        empreendimentos_json_path = os.path.join(app.root_path,'static', 'empreendimentos.json')

        # Ler os dados do arquivo
        with open(empreendimentos_json_path, 'r', encoding='utf-8') as json_file:
            empreendimentos_data = json.load(json_file)

            # Plotar o gráfico de empreendimentos por classe
            classes = []
            totais = []
            for item in empreendimentos_data:
                classe_consumo = item['Classe Consumo']
                total_empreendimentos = item['Total de Empreendimentos']
                classes.append(classe_consumo)
                totais.append(total_empreendimentos)

            plt.bar(classes, totais)
            plt.xlabel('Classe de Consumo')
            plt.ylabel('Total de Empreendimentos')
            plt.title('Empreendimentos por Classe de Consumo')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Caminho completo para a pasta static
            static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

            # Caminho completo para o arquivo de imagem
            imagem_path = os.path.join(static_folder, 'grafico_empreendimentos.png')

            # Salvando o gráfico como imagem
            plt.savefig(imagem_path)
            return render_template('dados.html', empreendimentos_data=empreendimentos_data, imagem_path=imagem_path)
    except json.JSONDecodeError as e:
        print(f"Erro na leitura dos dados JSON: {e}")
        return 'Falha ao ler os dados da resposta.'

@app.route('/download/<path:filename>')
def download(filename):
    try:
        static_folder = os.path.join(app.root_path, 'static')
        return send_from_directory(static_folder, filename, as_attachment=True)
    except json.JSONDecodeError as e:
        print(f"Erro na leitura dos dados JSON: {e}")
        return 'Falha ao ler os dados da resposta.'
    
if __name__ == '__main__':
    app.run()