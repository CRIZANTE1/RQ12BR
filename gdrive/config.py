import os
import json
import streamlit as st

def get_matrix_sheets_id():
    """Busca o ID da Planilha Matriz a partir dos segredos do Streamlit."""
    try:
        return st.secrets["google_drive"]["matrix_sheets_id"]
    except (KeyError, AttributeError):
        st.error("Erro Crítico: O ID da Planilha Matriz (`matrix_sheets_id`) não foi encontrado em secrets.toml.")
        st.stop()

def get_central_drive_folder_id():
    """Busca o ID da Pasta Central do Drive a partir dos segredos do Streamlit."""
    try:
        return st.secrets["google_drive"]["central_drive_folder_id"]
    except (KeyError, AttributeError):
        st.error("Erro Crítico: O ID da Pasta Central (`central_drive_folder_id`) não foi encontrado em secrets.toml.")
        st.stop()

USERS_SHEET_NAME = "usuarios"
AUDIT_LOG_SHEET_NAME = "log_auditoria"
ACCESS_REQUESTS_SHEET_NAME = "solicitacoes_acesso"

LOCATIONS_SHEET_NAME = "locais"
EXTINGUISHER_SHEET_NAME = "extintores"
HOSE_SHEET_NAME = "mangueiras"
SHELTER_SHEET_NAME = "abrigos"
INSPECTIONS_SHELTER_SHEET_NAME = "inspecoes_abrigos"
SCBA_SHEET_NAME = "conjuntos_autonomos"
SCBA_VISUAL_INSPECTIONS_SHEET_NAME = "inspecoes_scba"
EYEWASH_INVENTORY_SHEET_NAME = "chuveiros_lava_olhos"
EYEWASH_INSPECTIONS_SHEET_NAME = "inspecoes_chuveiros_lava_olhos"
MULTIGAS_INVENTORY_SHEET_NAME = "multigas_inventario"
MULTIGAS_INSPECTIONS_SHEET_NAME = "inspecoes_multigas"
LOG_MULTIGAS_SHEET_NAME = "log_multigas"
FOAM_CHAMBER_INVENTORY_SHEET_NAME = "camaras_espuma_inventario"
FOAM_CHAMBER_INSPECTIONS_SHEET_NAME = "inspecoes_camaras_espuma"
LOG_ACTIONS = "log_acoes"
LOG_SHELTER_SHEET_NAME = "log_abrigos"
LOG_SCBA_SHEET_NAME = "log_scba"
LOG_EYEWASH_SHEET_NAME = "log_acoes_chuveiros"
LOG_FOAM_CHAMBER_SHEET_NAME = "log_acoes_camaras_espuma"
HOSE_DISPOSAL_LOG_SHEET_NAME = "log_baixas_mangueiras"
EXTINGUISHER_SHIPMENT_LOG_SHEET_NAME = "log_remessas_extintores"
TH_SHIPMENT_LOG_SHEET_NAME = "log_remessas_th"
ALARM_INVENTORY_SHEET_NAME = "alarmes_inventario"
ALARM_INSPECTIONS_SHEET_NAME = "alarmes_inspecoes"
LOG_ALARM_SHEET_NAME = "log_alarmes"
SUPPORT_REQUESTS_SHEET_NAME = "solicitacoes_suporte"
EXTINGUISHER_DISPOSAL_LOG_SHEET_NAME = "log_baixas_extintores"

# Abas específicas do app de escadas
AVALIACOES_ESCADAS_SHEET_NAME = "avaliacoes_escadas"
PROJETOS_ESCADAS_SHEET_NAME = "projetos_escadas"



def get_credentials_dict():
    """
    Carrega as credenciais do serviço do Google.
    - Em produção (Streamlit Cloud), usa st.secrets.
    - Para desenvolvimento local, busca um arquivo 'credentials.json' na raiz do projeto.
    """
    if st.runtime.exists():
        try:
            return st.secrets["connections"]["gsheets"]
        except (KeyError, AttributeError):
            st.error("Erro: As credenciais do Google não foram encontradas em st.secrets. Configure [connections.gsheets] no seu secrets.toml.")
            st.stop()
    else:
        local_creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
        try:
            with open(local_creds_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error(f"Erro: Arquivo 'credentials.json' não encontrado. Crie este arquivo com suas credenciais de conta de serviço para desenvolvimento local.")
            st.stop()
        except json.JSONDecodeError:
            st.error(f"Erro: O arquivo 'credentials.json' está mal formatado.")
            st.stop()