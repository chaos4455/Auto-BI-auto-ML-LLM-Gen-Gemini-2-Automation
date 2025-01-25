# 🚀📊 Omni-Analytics AI: Plataforma Universal de Análise de Dados com IA, BI e ML 🧠

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge&logo=python" alt="Language: Python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-red?style=for-the-badge&logo=streamlit" alt="Framework: Streamlit">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini-green?style=for-the-badge&logo=google-gemini" alt="AI: Google Gemini">
  <img src="https://img.shields.io/badge/Database-SQLite-yellow?style=for-the-badge&logo=sqlite" alt="Database: SQLite">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge" alt="License: MIT">
</p>


## 💡 Descrição do Projeto

Omni-Analytics AI é uma plataforma inovadora e **altamente versátil** que combina o poder da **Inteligência Artificial (IA)**, **Business Intelligence (BI)** e **Machine Learning (ML)** para transformar a análise de dados. Diferente de soluções específicas, Omni-Analytics AI é projetada para ser **generalista**, permitindo que você gere e analise **qualquer tipo de dataset**, para **qualquer escopo**, e com **qualquer necessidade**.

Criado por **Eláís Andrade**, um analista de IA com foco em projetos de inovação, este projeto visa **democratizar a análise de dados**, tornando-a acessível mesmo para quem não possui profundo conhecimento técnico. 🚀

## 🎯 Objetivos Principais

-   **Automatizar a análise de dados** de ponta a ponta, desde a geração do dataset até a produção de relatórios executivos.
-   Permitir que **usuários de qualquer nível técnico** realizem análises complexas.
-   **Explorar o poder da IA** na criação de datasets, consultas SQL, visualização de dados e geração de insights.
-   **Validar e testar a capacidade da IA** em gerar código de BI e ML para diversos contextos e necessidades.
-   Oferecer uma **plataforma flexível** que se adapta a diferentes tipos de dados e análises.
-  Acelerar o ciclo de **descoberta e validação de hipóteses** com dados.

## ⚙️ Como Funciona?

Omni-Analytics AI opera em um fluxo de trabalho automatizado e inteligente, que pode ser dividido em etapas:

### 1. 📝 Geração de Datasets Sintéticos com IA

-   **Input:** Descrição textual do dataset desejado pelo usuário. 📝
-   **Processamento:**
    -   A IA gera um script Python personalizado, usando bibliotecas como `faker` para simulação de dados realistas, `random` para variabilidade e `pandas` para manipulação de DataFrames. 🤖
    -   Sazonalidade e tendências são simuladas para dados mais autênticos. 📈
    -   Os dados são armazenados em um banco de dados SQLite (`banco.db`) e também em `st.session_state` para acesso rápido. 💾
-   **Output:** DataFrame em memória e persistência em SQLite, pronto para análise. ✅

### 2. 🔍 Análise de Dados com Consultas SQL Inteligentes 🧠

-   **Input:** Pergunta do usuário em linguagem natural sobre os dados. ❓
-   **Processamento:**
    -   A IA analisa a pergunta, o esquema do banco de dados e exemplos de dados. 🧐
    -   Gera consultas SQL precisas para extrair as informações solicitadas. 🗄️
    -   As consultas são retornadas em formato YAML para fácil manipulação e visualização. 📝
-   **Output:** Consultas SQL em YAML com descrições claras. ✅

### 3. ⚙️ Execução de Consultas SQL e Manipulação de Dados

-   **Input:** Consultas SQL em formato YAML. 📝
-   **Processamento:**
    -   As consultas são executadas no banco de dados SQLite. ⚙️
    -   DataFrames com os resultados são gerados a partir dos resultados das consultas. 📊
    -   A plataforma lida com erros e resultados nulos. ✅
-   **Output:** DataFrames com os resultados das consultas prontas para visualização. ✅

### 4. 📊 Visualização de Dados com IA 🎨

-   **Input:** Pergunta do usuário, resultados das consultas, esquema dos dados. ❓
-   **Processamento:**
    -   A IA gera código Python para criar **4 gráficos** distintos e relevantes usando `matplotlib`. 📈
    -  Outras bibliotecas como `seaborn`, `plotly` e `cufflinks` podem ser utilizadas para criar visualizações ainda mais ricas.
    -   A plataforma escolhe o melhor tipo de gráfico (barras, linhas, pizza, dispersão) para cada conjunto de dados. 📊
    -   Personalização de cores, legendas, títulos e tipografia profissional para visualizações de alta qualidade. 🖌️
    -   Os gráficos são salvos como imagens PNG com resolução de 1080p, e disponibilizados para download automático via base64. 🖼️
-   **Output:** Quatro imagens PNG de alta resolução com downloads automáticos. ✅

### 5. 📑 Geração de Relatórios Executivos com IA 🤖

-   **Input:** Pergunta do usuário, histórico de interações, resultados de consultas, visualizações de dados e esquema do dataset. 📝
-   **Processamento:**
    -   A IA analisa todos os resultados, gera insights e produz um relatório executivo completo em YAML com Markdown. 🤖
    -   O relatório inclui:
        -   Visão geral do contexto da análise. 🧐
        -   Análise detalhada dos resultados das consultas. 🔍
        -   Identificação de tendências, padrões e anomalias. 📈
        -   Recomendações acionáveis para tomadas de decisão. 🎯
        -   Definição do escopo, limitações e pontos positivos dos dados. 📝
        -   Considerações finais sobre melhorias e próximos passos. 💡
         - Cotação do tempo e profundidade da analise. ⏱️
    -   Apresentação com icones e emojis para facilitar a leitura e compreensão. ✨
-   **Output:** Relatório executivo em YAML com insights, recomendações e visualizações de dados. ✅

## ✨ Inovação e Diferenciais

-   **IA Generativa:** Uso intensivo de IA para geração de código, dados e análises. 🤖
-   **Generalista:** Aplicações em qualquer área de estudo, para qualquer conjunto de dados, não limitado a e-commerce ou a uma área de conhecimento. 🎯
-   **Flexibilidade:** Geração de datasets personalizados e análises adaptáveis a cada necessidade. ⚙️
-   **Acessibilidade:** Permite que usuários sem conhecimento técnico realizem análises complexas. 🔓
-   **Automação:** Redução drástica do tempo e esforço em tarefas de análise. ⚡
-   **Visualizações Ricas:** Geração de gráficos profissionais e personalizados para insights claros. 📊
-    **Profundidade Analítica**: A IA analisa e cruza os dados de maneira profunda, para extrair insights valiosos. 🧠
-   **Ciclo Completo:** Integração de todas as etapas da análise, do início ao fim. 🔄
-   **Base de Conhecimento:** A plataforma acumula e utiliza o histórico de interações para gerar analises mais profundas e relevantes. 📚

## 🚀 Aplicações e Casos de Uso

Omni-Analytics AI é incrivelmente versátil e pode ser aplicada em diversas áreas:

-   **Ciência de Dados:** Geração de datasets para testes e validação de modelos de ML e IA. 🔬
-   **Pesquisa Acadêmica:** Análise de dados para experimentos, artigos e estudos. 🎓
-   **Engenharia de Software:** Geração de dados para testes de sistemas e aplicações. 💻
-   **Business Intelligence:** Análise de dados para otimizar processos e tomada de decisões estratégicas. 📈
-   **Análise de Mercado:** Estudos de tendências e comportamento do consumidor. 🛒
-   **Finanças:** Análise de dados financeiros, investimentos e projeções. 💰
-   **Saúde:** Análise de dados para pesquisas, estudos de saúde e acompanhamento de pacientes. ⚕️
-  **Engenharia de Produto:** Validação de hipóteses de protótipos e desenvolvimento de novos produtos. 🛠️

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python. 🐍
-   **Framework:** Streamlit (para interface web interativa). 🎈
-   **IA:** Google Gemini (para geração de código e análise de dados). 🧠
-   **Bibliotecas:** Pandas, Faker, SQLite3, YAML, Matplotlib, NumPy, Base64, PIL, Seaborn, Plotly, Cufflinks e muito mais. 📚
-   **Formato de Dados:** YAML, JSON, PNG, SQL, DataFrames. 🗂️
-   **Banco de Dados:** SQLite (para armazenamento de dados). 💾

## 👩‍💻 Sobre o Desenvolvedor

**Eláís Andrade** é um analista de IA apaixonado por inovação e projetos que transformam a maneira como interagimos com os dados. Com experiência em IA, BI e ML, Eláís está sempre buscando novas formas de utilizar a tecnologia para resolver problemas complexos e gerar valor para as empresas e a sociedade. 🚀

-   **LinkedIn:** [Seu LinkedIn](https://www.linkedin.com/in/seu_perfil)
-   **GitHub:** [Seu GitHub](https://github.com/elaisandrade)

## 📜 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 📄

## 🤝 Contribuições

Contribuições são muito bem-vindas! Sinta-se à vontade para abrir issues, enviar pull requests e compartilhar suas ideias. 🙏

## 🚀 Comece a Usar Omni-Analytics AI

1.  Clone o repositório: `git clone https://github.com/elaisandrade/omni-analytics-ai.git`
2.  Instale as dependências: `pip install -r requirements.txt`
3.  Execute o aplicativo: `streamlit run app.py`

### 🎉 Explore o Poder da IA na Análise de Dados com Omni-Analytics AI! 🎉
