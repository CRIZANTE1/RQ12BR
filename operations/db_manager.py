# operations/db_manager.py
import streamlit as st
import sqlalchemy
from supabase import create_client, Client, ClientOptions
import io
import json
import ssl
import httpx

# --- INÍCIO DA CORREÇÃO: Bypass de verificação SSL ---
# Adicione estas linhas para contornar o erro [SSL: CERTIFICATE_VERIFY_FAILED]
# comum em ambientes corporativos com proxies.
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context
# --- FIM DA CORREÇÃO ---


# --- INICIALIZAÇÃO DAS CONEXÕES (COM CACHE) ---
# Usamos st.cache_resource para criar as conexões apenas uma vez.
@st.cache_resource
def init_connections():
    """Inicializa e retorna as conexões com o Supabase (DB e Storage)."""
    try:
        # Removido st.info e st.success para uma inicialização mais limpa
        # Conexão com o Banco de Dados PostgreSQL via SQLAlchemy
        db_conn_str = st.secrets["supabase"]["db_connection_string"]
        engine = sqlalchemy.create_engine(db_conn_str)

        # Cliente do Supabase para o Storage (upload de arquivos)
        url: str = st.secrets["supabase"]["url"]
        key: str = st.secrets["supabase"]["key"]
        # CORREÇÃO: Adiciona `httpx_client` com verificação SSL desativada
        httpx_client = httpx.Client(verify=False)
        supabase: Client = create_client(url, key, options=ClientOptions(httpx_client=httpx_client))
        
        return engine, supabase
    except Exception as e:
        st.error(f"Erro fatal ao conectar com o Supabase: {e}")
        st.error("Verifique seu arquivo .streamlit/secrets.toml e as configurações de rede.")
        st.stop()

# Chama a função para obter as conexões. O cache garante que o código acima só rode uma vez.
engine, supabase = init_connections()
BUCKET_NAME = "imagens-escadas"


# --- FUNÇÕES DE BANCO DE DADOS (POSTGRESQL) ---

def carregar_avaliacoes():
    """Carrega todas as avaliações do banco de dados, ordenadas pela mais recente."""
    with engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM avaliacoes ORDER BY created_at DESC;"))
        # Converte o resultado para uma lista de dicionários para ser fácil de usar
        avaliacoes = [dict(row._mapping) for row in result]
        return avaliacoes

def salvar_avaliacao(avaliacao_dict):
    """Salva uma nova avaliação no banco de dados."""
    query = sqlalchemy.text("""
        INSERT INTO avaliacoes (local, data, altura_total, tipo, medidas, valores, status_itens, recomendacoes, grafico_url, foto_url)
        VALUES (:local, :data, :altura_total, :tipo, :medidas, :valores, :status_itens, :recomendacoes, :grafico_url, :foto_url)
    """)
    with engine.connect() as connection:
        with connection.begin() as transaction: # Usar transação para garantir atomicidade
            connection.execute(query, {
                "local": avaliacao_dict.get('local'),
                "data": avaliacao_dict.get('data'),
                "altura_total": avaliacao_dict.get('altura_total'),
                "tipo": avaliacao_dict.get('tipo', 'Avaliação'),
                # As colunas JSONB esperam uma string JSON, então convertemos as listas
                "medidas": json.dumps(avaliacao_dict.get('medidas', [])),
                "valores": json.dumps(avaliacao_dict.get('valores', [])),
                "status_itens": json.dumps(avaliacao_dict.get('status_itens', [])),
                "recomendacoes": json.dumps(avaliacao_dict.get('recomendacoes', [])),
                "grafico_url": avaliacao_dict.get('grafico_url'),
                "foto_url": avaliacao_dict.get('foto_url')
            })

def excluir_avaliacao(avaliacao_id):
    """Exclui uma avaliação e seus arquivos associados do Storage."""
    with engine.connect() as connection:
        with connection.begin() as transaction: # Usar transação
            # Primeiro, busca os URLs dos arquivos no DB
            select_query = sqlalchemy.text("SELECT grafico_url, foto_url FROM avaliacoes WHERE id = :id")
            result = connection.execute(select_query, {"id": str(avaliacao_id)}).first()
            
            if result:
                # CORREÇÃO: Acessar por nome para maior robustez
                grafico_url = result.grafico_url
                foto_url = result.foto_url
                # Exclui os arquivos do Storage usando os URLs
                if grafico_url:
                    excluir_arquivo_pela_url(grafico_url)
                if foto_url:
                    excluir_arquivo_pela_url(foto_url)

            # Agora, exclui o registro do banco de dados
            delete_query = sqlalchemy.text("DELETE FROM avaliacoes WHERE id = :id")
            connection.execute(delete_query, {"id": str(avaliacao_id)})


# --- FUNÇÕES DE ARMAZENAMENTO (STORAGE) ---

def salvar_arquivo(file_content_bytes, file_name, content_type='image/png'):
    """Salva um arquivo (em bytes) no Supabase Storage e retorna a URL pública."""
    try:
        # A API usa from_() para evitar conflito com a palavra-chave 'from' do Python
        supabase.storage.from_(BUCKET_NAME).upload(
            path=file_name,
            file=file_content_bytes,
            file_options={"content-type": content_type, "upsert": "true"} # upsert=true evita erro se o arquivo já existir
        )
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
        return public_url
    except Exception as e:
        st.error(f"Erro ao salvar arquivo no Storage: {e}")
        return None

def excluir_arquivo_pela_url(file_url):
    """Exclui um arquivo do Supabase Storage a partir de sua URL pública."""
    if not file_url or BUCKET_NAME not in file_url:
        return
    try:
        # Extrai o nome do arquivo da URL
        file_name = file_url.split(f'{BUCKET_NAME}/')[-1]
        supabase.storage.from_(BUCKET_NAME).remove([file_name])
    except Exception as e:
        st.warning(f"Não foi possível excluir o arquivo {file_name}. Pode já ter sido removido. Erro: {e}")

def fig_to_bytes(fig):
    """Converte uma figura Matplotlib em um objeto de bytes no formato PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()