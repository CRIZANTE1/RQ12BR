import streamlit as st
from datetime import datetime
import pytz

def log_action(action, details=""):
    """
    Registra uma ação no log de auditoria do sistema
    
    Args:
        action (str): Tipo de ação realizada (ex: "LOGIN_SUCCESS", "AVALIACAO_CRIADA")
        details (str): Detalhes adicionais sobre a ação
    """
    try:
        # Importar aqui para evitar circular imports
        from gdrive.gdrive_upload import GoogleDriveUploader
        from gdrive.config import AUDIT_LOG_SHEET_NAME
        from auth.auth_utils import get_user_email
        
        # Obter informações do usuário
        user_email = get_user_email() or "sistema@anonimo"
        
        # Timezone de São Paulo
        sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
        timestamp = datetime.now(sao_paulo_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        # Criar linha de log
        log_row = [
            timestamp,
            user_email,
            action,
            details
        ]
        
        # Salvar na planilha matriz
        try:
            matrix_uploader = GoogleDriveUploader(is_matrix=True)
            matrix_uploader.append_data_to_sheet(AUDIT_LOG_SHEET_NAME, [log_row])
        except Exception as e:
            # Se falhar ao salvar no Google Sheets, registra no console mas não interrompe
            print(f"⚠️ Aviso: Não foi possível salvar log de auditoria: {e}")
        
    except Exception as e:
        # Falha silenciosa - não deve interromper o fluxo do aplicativo
        print(f"⚠️ Erro ao registrar ação de auditoria: {e}")


def log_avaliacao_escada(avaliacao_id, local, conformidade_percentual):
    """
    Registra especificamente uma avaliação de escada
    
    Args:
        avaliacao_id (str): ID único da avaliação
        local (str): Local da instalação
        conformidade_percentual (float): Percentual de conformidade
    """
    details = f"ID: {avaliacao_id}, Local: {local}, Conformidade: {conformidade_percentual:.1f}%"
    log_action("AVALIACAO_ESCADA_CRIADA", details)


def log_projeto_escada(projeto_id, local, num_degraus):
    """
    Registra especificamente um projeto de escada
    
    Args:
        projeto_id (str): ID único do projeto
        local (str): Local da instalação
        num_degraus (int): Número de degraus do projeto
    """
    details = f"ID: {projeto_id}, Local: {local}, Degraus: {num_degraus}"
    log_action("PROJETO_ESCADA_CRIADO", details)


def log_erro(erro_tipo, erro_mensagem):
    """
    Registra um erro no sistema
    
    Args:
        erro_tipo (str): Tipo de erro
        erro_mensagem (str): Mensagem de erro
    """
    details = f"Tipo: {erro_tipo}, Mensagem: {erro_mensagem}"
    log_action("ERRO_SISTEMA", details)