import streamlit as st
import json
import os
from streamlit_lottie import st_lottie
from .auth_utils import is_oidc_available, is_user_logged_in, get_user_display_name

@st.cache_data
def load_lottie_file(filepath: str):
    """Carrega um arquivo Lottie JSON do caminho especificado."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Arquivo de animação não encontrado em: {filepath}")
        return None
    except json.JSONDecodeError:
        st.error(f"Erro ao ler o arquivo de animação. Verifique se é um JSON válido.")
        return None

def show_login_page():
    """
    Mostra uma página de login com animação Lottie, focada apenas no login com Google.
    """
    # Truque para acionar o st.login() sem que o botão desapareça
    if 'google_login_triggered' not in st.session_state:
        st.session_state.google_login_triggered = False

    if st.session_state.get('google_login_triggered', False):
        st.session_state.google_login_triggered = False # Reseta o gatilho
        st.login()

    # Layout da página em duas colunas
    login_col, lottie_col = st.columns([1, 1.5])

    with login_col:
        st.title("Sistema de Gestão de Inspeções De Segurança e Emergência")
        st.markdown("---")
        st.subheader("Por favor, faça login para continuar")
        st.write("") # Espaçamento

        # Botão para login com Google
        if is_oidc_available():
            if st.button("Entrar com Google", use_container_width=True, type="primary"):
                st.session_state.google_login_triggered = True
                st.rerun() # O rerun é necessário para que a lógica no topo da função seja acionada
        else:
            st.warning("O login com Google não está configurado.")
            st.error("Entre em contato com o administrador do sistema.")

    with lottie_col:
        # Encontra o caminho do arquivo Lottie de forma robusta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        lottie_filepath = os.path.join(current_dir, '..', 'lotties', 'login_animation.json')
        
        lottie_animation = load_lottie_file(lottie_filepath)
        
        if lottie_animation:
            st_lottie(
                lottie_animation,
                speed=1,
                loop=True,
                quality="high",
                height=500, # Ajuste a altura conforme necessário
                width=None, # Deixa a largura se ajustar
                key="login_lottie"
            )

    return False # Indica que o login ainda não foi concluído.

def show_user_header():
    """Mostra o nome do usuário logado na sidebar."""
    st.sidebar.info(f"Usuário: **{get_user_display_name()}**")

def show_logout_button():
    """Mostra o botão de logout na sidebar."""
    if st.sidebar.button("Sair do Sistema (Logout)"):
        # Limpa o gatilho de login para evitar loops
        if 'google_login_triggered' in st.session_state:
            del st.session_state['google_login_triggered']
        
        # Chama a função de logout do Streamlit
        try:
            st.logout()
        except:
            st.rerun()