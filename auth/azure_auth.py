import streamlit as st
import msal
import logging
from streamlit_js_eval import streamlit_js_eval
from utils.auditoria import log_action 


logger = logging.getLogger('abrangencia_app.azure_auth')
# --- Configuração ---
CLIENT_ID = st.secrets.get("azure", {}).get("client_id")
CLIENT_SECRET = st.secrets.get("azure", {}).get("client_secret")
TENANT_ID = st.secrets.get("azure", {}).get("tenant_id")
REDIRECT_URI = st.secrets.get("azure", {}).get("redirect_uri")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read"] # Permissões básicas para ler o perfil do usuário

@st.cache_resource
def get_msal_app():
    """Inicializa e retorna a aplicação MSAL Confidential Client."""
    if not all([CLIENT_ID, CLIENT_SECRET, TENANT_ID]):
        logger.error("Credenciais do Azure não configuradas nos secrets.")
        return None
    return msal.ConfidentialClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

def get_login_button():
    """Gera a URL de login do Azure e retorna um st.link_button."""
    msal_app = get_msal_app()
    if not msal_app:
        st.error("O login com Azure não está configurado corretamente.")
        return

    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    st.link_button("Fazer Login com Microsoft Azure", auth_url, use_container_width=True)


def handle_redirect():
    """
    Processa o redirecionamento, armazena as informações do usuário, registra a ação no log
    de auditoria e, em caso de sucesso, força um redirecionamento via JavaScript.
    """
    msal_app = get_msal_app()
    if not msal_app:
        return

    auth_code = st.query_params.get("code")
    if not auth_code or st.session_state.get('login_processed', False):
        return

    try:
        result = msal_app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )

        if "error" in result:
            logger.error(f"Erro ao adquirir token: {result.get('error_description')}")
            st.error(f"Erro de autenticação: {result.get('error_description')}")
            st.session_state.login_processed = True
            return

        id_token_claims = result.get('id_token_claims', {})
        user_email = id_token_claims.get('preferred_username')
        user_name = id_token_claims.get('name')

        if not user_email:
            st.error("Erro: E-mail não encontrado no perfil do Azure.")
            st.session_state.login_processed = True
            return

        # Limpa e normaliza os dados do usuário
        user_email_cleaned = user_email.lower().strip()
        user_name_cleaned = user_name or user_email_cleaned.split('@')[0]
        
        # Salva as informações na sessão
        st.session_state.is_logged_in = True
        st.session_state.user_info_custom = {
            "email": user_email_cleaned,
            "name": user_name_cleaned
        }
        st.session_state.login_processed = True

        # --- CHAMADA DO log_action ---
        # Registra a ação de login bem-sucedido no log de auditoria.
        # Note que get_user_email() e outras funções de auth_utils agora funcionarão
        # porque acabamos de definir o session_state.
        log_action("LOGIN_SUCCESS_AZURE", f"Email: {user_email_cleaned}")
        logger.info(f"Usuário '{user_email_cleaned}' autenticado. Redirecionando...")
        # --- FIM DA CHAMADA ---
        
        st.success("Autenticação bem-sucedida! Redirecionando...")
        streamlit_js_eval(js_expressions="window.location.href = window.location.pathname;")
        st.stop()

    except Exception as e:
        logger.error(f"Erro inesperado durante handle_redirect: {e}")
        st.error("Ocorreu um erro inesperado durante a autenticação.")
        st.session_state.login_processed = True