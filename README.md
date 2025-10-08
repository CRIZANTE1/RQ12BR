# RQ12BR - Avaliador de Escadas NR-12

Este projeto é uma ferramenta desenvolvida em Python e Streamlit para auxiliar na avaliação de conformidade de escadas industriais, com base nos requisitos da Norma Regulamentadora Nº 12 (NR-12) do Brasil.

## Funcionalidades

- **Calculadora de Escadas:**
  - **Avaliar Escada Existente:** Permite inserir as dimensões de uma escada existente para verificar sua conformidade com a NR-12.
  - **Calcular Nova Escada:** Ajuda a projetar uma nova escada que atenda aos padrões da norma.
- **Referências Visuais:** Apresenta imagens e diagramas que ilustram os requisitos da NR-12 para escadas.
- **Histórico de Avaliações:**
  - Salva os resultados das avaliações em um banco de dados Supabase.
  - Armazena um gráfico da escada avaliada e uma foto enviada pelo usuário.
  - Permite visualizar e excluir avaliações anteriores.

## Tecnologias Utilizadas

- **Frontend:** Streamlit
- **Backend:** Python
- **Banco de Dados:** Supabase (PostgreSQL)
- **Armazenamento de Arquivos:** Supabase Storage

## Instalação e Configuração

1. **Clone o repositório:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <NOME_DO_DIRETORIO>
   ```

2. **Instale as dependências:**
   Certifique-se de ter o Python 3.8+ instalado. Em seguida, instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as credenciais do Supabase:**
   Crie um arquivo chamado `secrets.toml` na pasta `.streamlit` e adicione suas credenciais do Supabase, conforme o exemplo abaixo:

   ```toml
   # .streamlit/secrets.toml
   [supabase]
   url = "SUA_URL_SUPABASE"
   key = "SUA_CHAVE_SUPABASE"
   db_connection_string = "SEU_STRING_DE_CONEXAO_POSTGRESQL"
   ```

## Como Executar

Para iniciar a aplicação, execute o seguinte comando na raiz do projeto:

```bash
python -m streamlit run main.py
```

A aplicação será aberta em seu navegador.

## Estrutura de Arquivos

```
.
├── main.py                   # Ponto de entrada da aplicação
├── requirements.txt          # Dependências do projeto
├── .streamlit/
│   └── secrets.toml          # Arquivo de segredos (credenciais)
├── data/
│   └── historico.json        # (Opcional) Arquivo de histórico local
├── images/                   # Imagens utilizadas na interface
└── operations/
    ├── avaliador_escada.py     # Lógica para avaliar escadas existentes
    ├── calculadora_escada.py   # Classe principal com as regras da NR-12
    ├── calculadora_nova_escada.py # Lógica para calcular novas escadas
    ├── db_manager.py           # Gerenciador de conexão com o Supabase
    ├── front.py                # Estrutura principal da interface
    ├── historico_avaliacoes.py # Lógica para exibir o histórico
    └── referencias_visuais.py  # Lógica para exibir as referências
```
