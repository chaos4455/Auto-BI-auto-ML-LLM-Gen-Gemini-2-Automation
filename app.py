import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
from faker import Faker
import sqlite3
import yaml
import re
from datetime import date, timedelta
import matplotlib.pyplot as plt
import io
import os
from base64 import b64encode
import shutil
import tempfile
from PIL import Image
import random
import numpy as np

# Configurações de chave secreta e API do Google Gemini
API_KEY = 'CHAVE-GOOGLE-GEMINI-API'  # Substitua pela sua chave API
genai.configure(api_key=API_KEY)

# Configuração do modelo de IA
CONFIGURACAO_GERACAO = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40,
    "response_mime_type": "text/plain",
}
NOME_MODELO = "gemini-2.0-flash-exp"
MODELO = genai.GenerativeModel(
    model_name=NOME_MODELO,
    generation_config=CONFIGURACAO_GERACAO,
)

def enviar_mensagem_para_modelo(mensagem):
    """Envia uma mensagem para o modelo de IA e retorna a resposta."""
    try:
        resposta = MODELO.start_chat(history=[]).send_message(mensagem)
        return resposta.text
    except Exception as e:
        st.error(f"❌ Erro ao comunicar com a IA: {e}")
        return None

def quebrar_texto(texto, tamanho_maximo=8000):
    """Quebra o texto em partes menores para evitar exceder o limite."""
    partes = []
    for i in range(0, len(texto), tamanho_maximo):
        partes.append(texto[i:i + tamanho_maximo])
    return partes

def extract_yaml_from_markdown(markdown_text):
    """Extrai snippets YAML de um texto Markdown."""
    yaml_pattern = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)
    yaml_matches = yaml_pattern.findall(markdown_text)
    return yaml_matches

def generate_dataset_code(user_input):
    prompt = f"""
    Você é um especialista em geração de datasets fictícios e criação de código Python. O usuário fornecerá uma descrição de um dataset que ele precisa. 
    Sua tarefa é gerar um código Python completo que utilize as bibliotecas `faker`, `random`, `pandas` e `sqlite3` para criar um dataset com as características especificadas pelo usuário. O código gerado deve criar um DataFrame com os dados, salvar em um banco de dados sqlite na raiz do projeto com o nome banco.db, e também salvar todo o DataFrame em st.session_state.
    
    **Instruções:**
    
    1.  **Entenda a necessidade do usuário:** Analise a descrição do dataset que o usuário quer criar.
    2.  **Use a biblioteca Faker:** Utilize a biblioteca `faker` para gerar dados fictícios realistas, como nomes, endereços, datas, empresas, etc.
    3.  **Use a biblioteca Random:** Utilize a biblioteca `random` para gerar dados com aleatoriedade, como números inteiros e flutuantes, com limites e distribuição.
    4.  **Use a biblioteca Pandas:** Utilize a biblioteca `pandas` para criar DataFrames, manipular e salvar os dados.
    5.  **Use a biblioteca sqlite3:** Utilize a biblioteca `sqlite3` para criar uma base de dados e salvar os dados na raiz do projeto com nome banco.db.
    6.  **Simule dados realistas:** Simule sazonalidade e tendências.
    7.  **Saída:** O código deve criar um DataFrame, salvar ele no st.session_state com nome df, salvar em um banco de dados sqlite na raiz do projeto com nome banco.db, salvar todo o DataFrame com os dados da base em st.session_state com o nome df_all_data e retornar o texto do código gerado para o streamlit.
    8. **Comentarios:** Não gere nenhum tipo de comentario, nada, gere só o código python
    
    O usuário pediu: {user_input}
    """
    response = enviar_mensagem_para_modelo(prompt)
    return response


def execute_dataset_code(dataset_code):
    """Executa o código Python para criar o dataset."""
    dataset_code = re.sub(r'```python\n', '', dataset_code)
    dataset_code = re.sub(r'\n```', '', dataset_code)

    try:
        exec(dataset_code, globals())
        st.session_state['data_generated'] = True
        st.success("✅ Dataset criado com sucesso!")
    except Exception as e:
        st.error(f"❌ Erro ao executar o código Python para criar o dataset: {e}")


def get_db_schema():
    """Obtém o esquema do banco de dados."""
    if 'df_all_data' not in st.session_state:
        return "Schema não disponível: Execute a criação do dataset primeiro."
    
    df_all_data = st.session_state['df_all_data']
    
    if df_all_data.empty:
        return "Schema não disponível: DataFrame de dados está vazio."

    schema = "Tabela: historico_estoque\n"
    schema += "Colunas:\n"
    for col in df_all_data.columns:
        schema += f"- {col} (TEXT)\n"
    
    return schema

def get_sample_data():
    """Obtém amostra de dados do DataFrame."""
    if 'df_all_data' not in st.session_state:
        return "Nenhum dado disponível: Execute a criação do dataset primeiro."

    df_all_data = st.session_state['df_all_data']

    if df_all_data.empty:
        return "Nenhum dado disponível: DataFrame de dados está vazio."
    
    sample_data = df_all_data.head(2).to_dict(orient='records')
    return sample_data


def process_user_input(user_input, db_schema, sample_data):
    """Processa a entrada do usuário e gera querys SQL, usando o esquema e exemplo de dados."""
  
    sample_data_str = json.dumps(sample_data, indent=2, default=str, ensure_ascii=False)
    prompt = f"""
    Você é um assistente de análise de dados especializado em SQL.
    
    O usuário fornecerá uma pergunta sobre os dados, e você deverá gerar um ou mais comandos SQL para responder à pergunta.
    
    Aqui está o esquema da tabela do banco de dados:
    
    ```text
    {db_schema}
    ```
    
    Aqui estão exemplos de 2 linhas de dados da tabela (em formato JSON):
    
    ```json
    {sample_data_str}
    ```
    
    
    O usuário fará perguntas sobre esses dados.
    
    Você deve responder em formato YAML e, caso preciso, gerar multiplas querys SQL, com a seguinte estrutura:
    
    ```yaml
      query_1:
        description: "descrição da query 1"
        sql: "comando sql 1"
      query_2:
        description: "descrição da query 2"
        sql: "comando sql 2"
    ```
    
    A descrição deve ser detalhada, e o comando SQL deve ser completo, e você deve usar apenas os nomes de colunas e tabelas fornecidas no esquema.
    
    O usuario perguntou: {user_input}
    """
    response = enviar_mensagem_para_modelo(prompt)
    return response

def execute_queries(conn, yaml_response, df_all_data):
    """Executa as consultas SQL extraídas do YAML e retorna os resultados."""
    queries_yaml = extract_yaml_from_markdown(yaml_response)
    if not queries_yaml:
        return None
    
    query_results = {}
    if df_all_data is not None:
         
         with sqlite3.connect(':memory:') as conn_mem:
              df_all_data.to_sql('historico_estoque', conn_mem, if_exists='replace', index=False)
              for yaml_str in queries_yaml:
                 try:
                     queries = yaml.safe_load(yaml_str)
                     if isinstance(queries,dict):
                        for key, query_data in queries.items():
                           sql_query = query_data.get('sql')
                           description = query_data.get('description')
                           if sql_query:
                                 try:
                                   df_result = pd.read_sql_query(sql_query, conn_mem)
                                   query_results[key] = {
                                        'description': description,
                                        'sql': sql_query,
                                        'result': df_result
                                       }
                                 except Exception as e:
                                      query_results[key] = {
                                            'description': description,
                                            'sql': sql_query,
                                             'result': f"Erro ao executar query em df: {e}"
                                         }
                           else:
                               query_results[key] = {
                                    'description': description,
                                     'sql': 'Erro: SQL não encontrado',
                                      'result': None
                                    }
                 except Exception as e:
                    query_results[f'Erro ao executar query '] = {
                        'description': 'Erro ao executar query',
                        'sql': None,
                        'result': f"Erro: {e}"
                    }
    else:
      query_results[f'Erro ao executar query '] = {
            'description': 'Erro ao executar query',
            'sql': None,
            'result': "DataFrame não carregado"
      }
            
    return query_results
    
def generate_plots(user_input, previous_responses, query_results, db_schema, sample_data):
    """Gera um código Python que cria gráficos com base nos dados processados e histórico."""
    
    formatted_results = ""
    for key, value in query_results.items():
            if isinstance(value, dict):
                formatted_results += f"\n\n**Query: {key}**\n\n"
                formatted_results += f"**Descrição:** {value.get('description')}\n\n"
                formatted_results += f"**SQL:** \n\n```sql\n{value.get('sql')}\n```\n\n"
                
                result = value.get('result')
                if isinstance(result, pd.DataFrame):
                  formatted_results += f"**Resultados:**\n\n"
                  formatted_results += result.to_markdown(index=False)
                elif isinstance(result,str):
                  formatted_results += f"**Resultado:**\n\n{result}\n\n"
                else:
                    formatted_results += f"**Sem resultados**\n\n"
            else:
                formatted_results += f"\n\n**Erro**: {key}\n\n"
                formatted_results += f"**Erro**: {value}\n\n"
    sample_data_str = json.dumps(sample_data, indent=2, default=str, ensure_ascii=False)

    prompt = f"""
    📊 **Geração de Gráficos para Análise de E-commerce: Planejamento Detalhado e Execução Precisa** 📈

    Você é um especialista em visualização de dados com foco em e-commerce e gestão de estoque. Antes de gerar o código, dedique tempo para analisar profundamente os dados, o contexto e a pergunta do usuário. Sua tarefa é gerar um snippet de código Python que utilize a biblioteca `matplotlib.pyplot` para gerar quatro gráficos distintos, formatados como imagens PNG de alta resolução (1080p) e que sejam salvos na raiz do projeto.

    **Contexto da Análise**

    O usuário solicitou informações sobre o histórico de vendas e compras, fazendo a seguinte pergunta:

    > 💬 **Pergunta do Usuário:** {user_input}

    **Dados Processados**

    Com base na pergunta do usuário, as seguintes querys SQL foram executadas e seus resultados foram obtidos:
    
    ```text
    {formatted_results}
    ```
    
   **Estrutura do Banco de Dados e Exemplos:**
   
    ```text
    {db_schema}
    ```
    
    ```json
    {sample_data_str}
    ```
    
    **Planejamento:**

    1. **Entendimento Profundo dos Dados:** Analise cuidadosamente a estrutura da tabela do banco de dados (que pode variar a cada execução), os exemplos de dados fornecidos, e o contexto da pergunta do usuário. Determine quais insights são mais relevantes e como eles podem ser visualizados de maneira eficaz.
    2. **Definição do que exibir:** Com base nos dados, no contexto, e na pergunta do usuario, liste explicitamente o que vai ser mostrado em cada gráfico. Seja proativo e criativo, utilize o maximo dos dados, aprofunde, mostre dados que podem ter valor. 
    3.  **Cotação:** Antes de gerar o código Python, faça uma cotação do tempo que seria gasto para criar os 4 graficos planejados, liste todo o planejamento dos graficos e os dados que ele usa.
  
     **Banco de Dados:**
    *   Um arquivo `banco.db` foi criado na raiz do projeto com todos os dados de vendas e compras. O py gerado pela ia deve usar esse banco para gerar os gráficos,
    *  **Estrutura do Banco de Dados:** Garanta que o código use a mesma estrutura do banco, lendo a estrutura do banco de dados `banco.db` na raiz do projeto  e não usando uma estrutura predefinida.


sempre que necessario, use as libs que estoa no seu ambiente, que sao essas : 

Todas as libs a seguir estão instaladas no seu ambiente, use elas, como quiser, 
Libs instaladas que podem ser importadas:

streamlit
google-generativeai
pandas
faker
pyyaml
tabulate
matplotlib
dash

# --- Data Science & Analysis ---
numpy
scipy
scikit-learn  # Machine Learning Algorithms
statsmodels # Statistical Modeling, Time Series (ARIMA, SARIMA, etc.)
prophet     # Time Series Forecasting
seaborn     # Advanced Statistical Visualization
plotly      # Interactive Plotting
cufflinks   # Plotly + Pandas Integration
openpyxl    # Excel file handling
sqlalchemy  # Database interaction
requests    # HTTP requests for data fetching
beautifulsoup4 # Web Scraping
nltk        # Natural Language Processing (text analysis)
spacy       # Advanced NLP

# --- Machine Learning & Deep Learning ---
tensorflow  # Deep Learning Framework
keras       # Neural Network API (runs on TensorFlow)
torch       # PyTorch - Another major DL framework
torchvision # PyTorch Vision Library
transformers # Hugging Face Transformers - NLP Models
accelerate # Hugging Face - Distributed Training
datasets   # Hugging Face - Datasets Library
xgboost     # Gradient Boosting (ML)
lightgbm    # Gradient Boosting (ML)
catboost    # Gradient Boosting (ML)

Todas as libs acima estão no seu ambiente e devem e poder ser usadas conforme sua necessidade-


    **Instruções Obrigatórias para o Código Python:**
     -  Leia a estrutura do banco de dados `banco.db` para identificar o nome da tabela (pode variar a cada execução) e os nomes das colunas. Use essa estrutura para gerar os gráficos.
    gere 4 png de 1080p  - cada png tem 4 graficos, os graficos tem o mesmo padrão de cor, branco tons azuis e roxos - bem profisisonal, entenda bem os dados, gere os graficos 100 % alinhado aos dados
    mostre coisa relevantes, defina o que sao os dados, quais os melhores insights a mostrar, que graficos ira gerar, dia gere os graficos, faça tudo iso em contexot antes mesmo de gerar o py, 
    os graficos devem ser pfoissionais e ao estado da arte, ser ricos,a vançados, estilizados, consistentes, devem ser classificados, estruturados, escolha os melhores tipos de graficos para os dados
    seja criativo, use variedade de graficos  - crie ao estado da arte do mais avançado em bi e graficos 
    seja consistente, mostre detalhes valiosos, foque tanto no que o usuario pediu, como seja criado e crie coisa que nao foram pedidas mas que sao de valor 
    nunca gere comentarios, nada, gere unicamente o py, sem comentarios fora alem do py, ou seja, a resposta é o py, nao tem texto no md fora do snippet py - 
    * Utilize **MAJORIRATIAMENTE, MAS NÃO EXCLUSIVAMENTE** `matplotlib.pyplot` para gerar os gráficos, use sempre que necessário qualquer outra libs, das libs do seu ambiente.  Você deve evitar QUALQUER tipo de saída web, incluindo frameworks como `dash` -  **NUNCA** use `dash` para gerar qualquer tipo de output web.
    * Os gráficos devem ser salvos **EXCLUSIVAMENTE** como arquivos PNG na raiz do projeto, com resolução de 1080p (1920x1080 pixels).
        *   Nomeie os arquivos como `grafico_1.png`, `grafico_2.png`, `grafico_3.png`, e `grafico_4.png`.
        *  NUNCA, em hipótese alguma, gere código que tente abrir qualquer tipo de servidor web ou algo parecido, como essa linha de comando e outras semelhantes " Dash is running on http://127.0.0.1:8050/\n * Serving Flask app 'app'\n * Debug mode: off\nWARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.\n * Running on http://127.0.0.1:8050\nPress CTRL+C to quit"
    *   O py deve fazer a leitura dos dados do banco de dados `banco.db` na raiz do projeto para criar os graficos, usando a estrutura do banco conhecida, e não outro dataframe ou algo parecido.
    *   Gere quatro gráficos diferentes (um por PNG), cada um representando um indicador importante para a gestão do estoque.
         * Use cores consistentes e profissionais para os gráficos, e legendas.
         * Use uma tipografia limpa e profissional.
         * Utilize tudo o que estiver ao seu alcance para que os graficos sejam criativos, profissionais e de alta qualidade.
        *   Em um dos gráficos gere uma representação do que foi pedido pelo usuario em sua pergunta.
        *    **Download Automatico:** Depois de gerar os graficos em png, gere um código para que esses arquivos sejam baixados automaticamente pelo navegador do usuário, sem a necessidade de clicar em botões, usando base64.
    *   **Comentários:** Inclua comentários no código Python para explicar cada passo.
    *   **Captura da Imagem:** Não faça exibição da imagem em tela, apenas garanta que os 4 png sejam gerados corretamente.
    
    **Formato da Resposta:**
    Gere o código Python completo como um bloco de código Markdown com a seguinte estrutura:
    
    ```python
    # seu código python aqui
    ```
    """
    
    plot_code = enviar_mensagem_para_modelo(prompt)
    return plot_code

def execute_plot_code(plot_code, png_placeholder):
    """Executa o código Python com os gráficos e captura as imagens."""
    plot_code = re.sub(r'```python\n', '', plot_code)
    plot_code = re.sub(r'\n```', '', plot_code)
    
    try:
        exec(plot_code, globals())
        # Listar arquivos png gerados na pasta
        png_files = [f for f in os.listdir('.') if f.endswith('.png')]
        
        # Exibir as imagens e botao para dowload
        with png_placeholder.container():
            st.success("✅ Gráficos gerados com sucesso!")
            for png_file in png_files:
              with open(png_file, "rb") as f:
                  img_bytes = f.read()
              st.image(img_bytes, caption=f"Gráfico: {png_file}")
              b64_encoded_image = b64encode(img_bytes).decode()
              st.markdown(
                f'<a href="data:image/png;base64,{b64_encoded_image}" download="{png_file}">Baixar {png_file}</a>',
                unsafe_allow_html=True
                )
    except Exception as e:
        st.error(f"❌ Erro ao executar o código Python: {e}")

def generate_report_with_images(user_input, previous_responses, query_results, png_files, db_schema, sample_data):
    """Gera o relatório com texto, imagens e históricos."""

    formatted_results = ""
    for key, value in query_results.items():
            if isinstance(value, dict):
                formatted_results += f"\n\n**Query: {key}**\n\n"
                formatted_results += f"**Descrição:** {value.get('description')}\n\n"
                formatted_results += f"**SQL:** \n\n```sql\n{value.get('sql')}\n```\n\n"
                
                result = value.get('result')
                if isinstance(result, pd.DataFrame):
                  formatted_results += f"**Resultados:**\n\n"
                  formatted_results += result.to_markdown(index=False)
                elif isinstance(result,str):
                  formatted_results += f"**Resultado:**\n\n{result}\n\n"
                else:
                    formatted_results += f"**Sem resultados**\n\n"
            else:
                formatted_results += f"\n\n**Erro**: {key}\n\n"
                formatted_results += f"**Erro**: {value}\n\n"
    
    sample_data_str = json.dumps(sample_data, indent=2, default=str, ensure_ascii=False)
    
    
    image_tags = ""
    for idx, png_file in enumerate(png_files):
      with open(png_file, "rb") as f:
          img_bytes = f.read()
          b64_encoded_image = b64encode(img_bytes).decode()
          image_tags += f"<img src='data:image/png;base64,{b64_encoded_image}' width='300' alt='Gráfico {idx+1}'>"
     
    image_tags_layout = f"""
       <div style="display: flex; flex-wrap: wrap; justify-content:center;">
        {image_tags}
    </div>
    """

    prompt = f"""
    📊 **Relatório Executivo com Análise de Dados de E-commerce e Gráficos** 📈

    Você é um especialista em análise de dados com vasta experiência em e-commerce, gestão de estoque e visualização de dados. Sua tarefa é gerar um relatório executivo completo, abordando os dados de histórico de vendas e compras e os gráficos gerados. Sua persona é de um analista de dados sênior, didático, profundo, com visão de negócio e olhar apurado sobre os dados, abordando o contexto comercial, técnico, logístico, com foco no impacto gerencial e o que for necessário para gerar um resultado de alta qualidade.

    **Contexto da Análise**

    O usuário solicitou informações sobre o histórico de vendas e compras, fazendo a seguinte pergunta:

    > 💬 **Pergunta do Usuário:** {user_input}

    **Dados Processados**

    Com base na pergunta do usuário, as seguintes querys SQL foram executadas e seus resultados foram obtidos:
    
    ```text
    {formatted_results}
    ```
    
    **Estrutura do Banco de Dados e Exemplos:**
   
    ```text
    {db_schema}
    ```
    
    ```json
    {sample_data_str}
    ```
    
    **Gráficos Gerados:**

    Os seguintes gráficos foram gerados e salvos na raiz do projeto:
   
    {image_tags_layout}
   
   
     **Lista de Imagens:**
     - Grafico_1.png
     - Grafico_2.png
     - Grafico_3.png
     - Grafico_4.png
    
    **Instruções para o Relatório:**

    1.  **Visão Geral:** Apresente uma visão geral do contexto da análise. Qual é o propósito da análise do histórico de vendas e compras?
    2.  **Análise Detalhada:** Apresente uma análise detalhada de cada consulta e seus resultados. 
        *   Utilize uma linguagem clara, objetiva e rica em detalhes.
        *   Explique o impacto comercial e logístico dos resultados.
        *  Use números, porcentagens e estatísticas para quantificar os insights.
        *    Use icones, emojis, negrito, italico e todos recursos do markdown para enriquecer o texto.
    3.  **Insights e Tendências:** Analise os gráficos gerados e identifique padrões, tendências, valores discrepantes ou anomalias nos dados.
        *   Quais produtos são mais vendidos ou comprados?
        *   Quais são os períodos de maior e menor movimento?
        *  Quais são os principais fornecedores e clientes?
    
    4.  **Recomendações Acionáveis:** Ofereça recomendações claras e acionáveis para otimizar o estoque.
        *   Como melhorar o planejamento de compras?
        *   Como reduzir o estoque parado e os custos de armazenamento?
        *   Quais ações devem ser tomadas para resolver os problemas identificados?
        *   Quais produtos devem ser priorizados para compra?
        *   Quais produtos devem ser oferecidos em promoções?
    5.  **Escopo:** Defina qual o escopo desses dados, quais as limitações e os pontos positivos.
    6.  **Considerações Finais:** Apresente uma visão geral sobre o que pode ser aprimorado nas próximas análises.
    7. **Cotação:** Faça uma cotação da análise, de acordo com seu tempo e nível de profundidade.

    **Formato da Resposta:**
    Gere o relatório executivo em formato YAML, com a seguinte estrutura:
    ```yaml
        relatorio_executivo:
            titulo: "Título do Relatório Executivo"
            texto: "Texto detalhado do Relatório Executivo"
    ```
    """
    report_response = enviar_mensagem_para_modelo(prompt)
    return report_response

def main():
    st.set_page_config(page_title="Análise de Estoque E-commerce", page_icon="🛒")
    st.title("Análise de Histórico de Vendas e Compras 🛒")
    
    # Area de texto para descrição do dataset
    st.markdown("### Descreva o dataset que deseja criar:")
    dataset_description = st.text_area("Ex: Crie um dataset com dados de clientes, compras, produtos, e empresas")
    
    if st.button("Criar Dataset"):
        if not dataset_description:
            st.error("⚠️ Por favor, descreva o dataset.")
            return
    
        with st.spinner("Gerando código Python para dataset..."):
          dataset_code = generate_dataset_code(dataset_description)
          if dataset_code:
              st.markdown("### Código Python Gerado:")
              st.markdown(dataset_code)
          else:
             st.error("❌ Falha ao gerar código python para o dataset.")
             return
          
        with st.spinner("Executando código Python para criar dataset..."):
            execute_dataset_code(dataset_code)

    
    
    if 'data_generated' not in st.session_state:
        st.warning("⚠️ Por favor, crie um dataset primeiro.")
        return
      
    
    if 'df_all_data' not in st.session_state:
       try:
          with sqlite3.connect('banco.db') as conn_saved_db:
            cursor = conn_saved_db.cursor()
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                table_name = tables[0][2]
                cursor.execute(f"SELECT * FROM {table_name}")
                all_data = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                df_all_data = pd.DataFrame(all_data, columns=columns)
                st.session_state['df_all_data'] = df_all_data
            else:
                st.error("Nenhuma tabela encontrada no banco de dados.")
                return
       except Exception as e:
            st.error(f"❌ Erro ao carregar os dados do banco: {e}")
            return
    else:
        df_all_data = st.session_state['df_all_data']
        

    
    db_schema = get_db_schema()
    sample_data = get_sample_data()
    
    st.markdown("### Exemplo dos dados no banco:")
    st.markdown(f"**Schema:**\n\n```text\n{db_schema}\n```")
    st.markdown(f"**Exemplo de dados:**\n\n```json\n{json.dumps(sample_data, indent=2, default=str, ensure_ascii=False)}\n```")
    
    st.markdown("### Faça sua pergunta sobre os dados:")
    user_input = st.text_input("Digite sua pergunta aqui:")
    
    png_placeholder = st.empty()

    if st.button("🔍 Análise e Geração de Relatórios"):
        if not user_input:
            st.error("⚠️ Por favor, digite sua pergunta.")
            return
        
        spinner_placeholder = st.empty()
        with spinner_placeholder.container():
            with st.spinner("Processando pergunta e gerando querys SQL..."):
              
                previous_responses = ""
                
                yaml_response = process_user_input(user_input, db_schema, sample_data)
                
                if yaml_response:
                  st.markdown("### Resposta da IA para a geração das querys:")
                  st.markdown(yaml_response)
                  previous_responses = yaml_response
                else:
                   st.error("❌ Falha ao obter resposta da IA para gerar a querys.")
                   return

        
        with spinner_placeholder.container():
            with st.spinner("Executando querys SQL..."):
                with sqlite3.connect('banco.db') as conn:
                    query_results = execute_queries(conn,yaml_response,df_all_data)
                
                if query_results:
                      st.markdown("### Resultados das Querys:")
                      for key, value in query_results.items():
                        if isinstance(value, dict):
                          st.markdown(f"#### Query: {key}")
                          st.markdown(f"**Descrição:** {value.get('description')}")
                          st.markdown(f"**SQL:** ```sql\n{value.get('sql')}\n```")
                          result = value.get('result')
                          if isinstance(result, pd.DataFrame):
                            st.dataframe(result)
                          elif isinstance(result,str):
                             st.markdown(f"**Resultado:** {result}")
                          else:
                             st.markdown("**Sem resultados**")
                        else:
                            st.error(f"❌ Erro na Query: {key} - {value}")
                else:
                    st.error("❌ Falha ao executar querys.")
                    return

        with spinner_placeholder.container():
             with st.spinner("Gerando código Python para os gráficos..."):
                 plot_code = generate_plots(user_input, previous_responses,query_results, db_schema, sample_data)
                 if plot_code:
                    st.markdown("### Código Python para Geração de Gráficos:")
                    st.markdown(plot_code)
                 else:
                    st.error("❌ Falha ao gerar o código Python para os gráficos.")
                    return
        with spinner_placeholder.container():
             with st.spinner("Executando código Python e exibindo gráficos..."):
                execute_plot_code(plot_code, png_placeholder)
        with spinner_placeholder.container():
           png_files = [f for f in os.listdir('.') if f.endswith('.png')]
           with st.spinner("Gerando relatório executivo com imagens..."):
                report_response = generate_report_with_images(user_input, previous_responses, query_results, png_files, db_schema, sample_data)
                if report_response:
                    st.markdown("### Relatório Executivo com Imagens:")
                    st.markdown(report_response)
                else:
                    st.error("❌ Falha ao gerar relatório com as imagens.")
                    return

        #Manter tudo na tela apos o relatório
        st.markdown("### Exemplo dos dados no banco:")
        st.markdown(f"**Schema:**\n\n```text\n{db_schema}\n```")
        st.markdown(f"**Exemplo de dados:**\n\n```json\n{json.dumps(sample_data, indent=2, default=str, ensure_ascii=False)}\n```")
        st.markdown("### Faça sua pergunta sobre os dados:")
        st.text_input("Digite sua pergunta aqui:", key='new_input')

if __name__ == "__main__":
    main()
