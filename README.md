# API_ANEEL
Aplicação para consumir dados abertos da ANEEL e apresentá-los de forma didática.

## Prerrogativas direcionais
1. **Requisição e Organização dos Dados**

  * Utilizar a API da ANEEL para requisição de dados do pacote "relação de empreendimentos de geração distribuída".
  * Sugestão de linguagem de programação: Python.
  * Links de referência:
    * [Dados Abertos ANEEL](https://dadosabertos.aneel.gov.br/)
    * [Documentação da API](https://docs.ckan.org/en/2.9/api/)
  * Agregar os dados em base mensal:
  * Total de empreendimentos por classe (Residencial, comercial, etc.) e estado federativo.
  * Potência instalada de cada estado.
  * Utilização das colunas "DthAtualizaCadastralEmpreend", "DscClasseConsumo", "MdaPotenciaInstaladaKW" e "SigUF".
  * Organização dos dados em estrutura similar a um banco de dados SQL, exportando os dados em arquivos JSON e CSV.

2. **Exposição dos Dados em Forma Gráfica**

  * Selecionar 2 das opções abaixo:
    * *Opção 1*: Elaboração de um gráfico mostrando a evolução temporal do Total Mensal de Empreendimentos por Estado e por Classe de Consumo.
    * *Opção 2*: Elaboração de um gráfico mostrando a evolução temporal da Potência Instalada Total (KW) por Estado.
    * *Opção 3* (obrigatória): Selecionar variáveis de forma livre e fazer a exposição da maneira que achar mais adequada, utilizando a criatividade.
  * Sugestão de ferramentas: HTML, CSS, JavaScript, etc. Porém, outras ferramentas gráficas também podem ser utilizadas.
  * Informações a serem enviadas:
    * Códigos elaborados de Back-end e Front-end.
    * Arquivos exportados de dados.
    * Links de outras plataformas de Dashboard, caso utilizadas.
   
## Sobre o projeto
1. **Back-end**
  
  * Foi utilizado o *[Python](https://docs.python.org/3/)* como linguagem base para a criação.
    * De forma que fosse possível consumir dados da API da ANEEL e posteriormente filtrá-lo e aprensetar as informações que foram determinadas no escopo direcional, utilizei a biblioteca *[Flask](https://flask.palletsprojects.com/en/2.3.x/)* para subir um servidor local na porta *5000*.
    * Também foram utilizadas outras bibliotecas como *[Collections](https://docs.python.org/3/library/collections.html), [Matplotlib](https://matplotlib.org/), [urllib](https://docs.python.org/3/library/urllib.html), [json](https://docs.python.org/pt-br/3/library/json.html), [csv](https://docs.python.org/3/library/csv.html), [os](https://docs.python.org/3/library/os.html), [Requests](https://pypi.org/project/requests/)* e *[random](https://docs.python.org/3/library/random.html)*.

2. **Front-end**

  * Para imprimir os dados utizei um tamplate simples misturando código *[HTML](https://developer.mozilla.org/pt-BR/docs/Web/HTML), [CSS](https://developer.mozilla.org/pt-BR/docs/Web/CSS)* e a biblioteca *[Charts]([https://learn.jquery.com/using-jquery-core/document-ready/](https://www.chartjs.org/docs/latest/)*, baseada em JavaScript.
  
3. **Instruções**

  * A aplicação foi crianda em um ambiente virtual do Python. Dessa forma, primeira mente é necessário ativálo através do comando `$ venv/Scripts/Activate` (Windows) ou `$ source venv/bin/activate` (Linux ou macOS) na pasta raiz do projeto.
  * Após ativado o ambiente virtual já é possível subir o servido Flask com o comando `$ flask run` na pasta raiz do projeto. Uma mensagem será printada no prompt de comando informando o resultado do comando, assim como a URL local onde a página será renderizada (http://127.0.0.1:5000).
  * Acessando a URL informada será possível visualizar a página principal e um botão que redireciona para outro endpoint que exibirá as tabelas em páginas HTML.

