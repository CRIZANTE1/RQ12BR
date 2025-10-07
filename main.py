import streamlit as st
from operations.front import front
from auth.login_page import show_login_page, show_user_header, show_logout_button
from auth.auth_utils import is_user_logged_in, setup_sidebar

def main():
    # Verificar se o usuário está logado
    if not is_user_logged_in():
        show_login_page()
        return
    
    # Configurar sidebar com informações do usuário
    show_user_header()
    
    # Verificar acesso e configurar ambiente
    if not setup_sidebar():
        st.error("Você não tem permissão para acessar este sistema.")
        st.stop()
    
    # Adicionar botão de logout
    show_logout_button()
    
    # Chamar a função front() do front.py
    front()

if __name__ == "__main__":
    main()