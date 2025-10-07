import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth.auth_utils import is_superuser, get_users_data
from gdrive.gdrive_upload import GoogleDriveUploader
from gdrive.config import AVALIACOES_ESCADAS_SHEET_NAME, PROJETOS_ESCADAS_SHEET_NAME

if not is_superuser():
    st.error("🚫 Acesso negado. Esta página é restrita a administradores.")
    st.stop()

st.title("🪜 Administração - Sistema de Escadas NR-12")

tab_stats, tab_avaliacoes, tab_projetos = st.tabs([
    "📊 Estatísticas", "📋 Avaliações", "🏗️ Projetos"
])

matrix_uploader = GoogleDriveUploader(is_matrix=True)
users_df = get_users_data()

with tab_stats:
    st.header("Estatísticas Gerais do Sistema")
    
    # Carregar dados de todos os usuários
    total_avaliacoes = 0
    total_projetos = 0
    
    active_users = users_df[users_df['status'] == 'ativo']
    
    for _, user in active_users.iterrows():
        try:
            user_uploader = GoogleDriveUploader(is_matrix=False)
            user_uploader.spreadsheet_id = user['spreadsheet_id']
            
            avaliacoes = user_uploader.get_data_from_sheet(AVALIACOES_ESCADAS_SHEET_NAME)
            projetos = user_uploader.get_data_from_sheet(PROJETOS_ESCADAS_SHEET_NAME)
            
            total_avaliacoes += len(avaliacoes) - 1 if avaliacoes and len(avaliacoes) > 1 else 0
            total_projetos += len(projetos) - 1 if projetos and len(projetos) > 1 else 0
        except:
            continue
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuários Ativos", len(active_users))
    col2.metric("Total de Avaliações", total_avaliacoes)
    col3.metric("Total de Projetos", total_projetos)
    col4.metric("Média Avaliações/Usuário", f"{total_avaliacoes/len(active_users):.1f}" if len(active_users) > 0 else "0")

with tab_avaliacoes:
    st.header("Todas as Avaliações Realizadas")
    
    selected_user = st.selectbox(
        "Filtrar por usuário:",
        ["Todos"] + active_users['email'].tolist()
    )
    
    # Implementar visualização de avaliações

with tab_projetos:
    st.header("Todos os Projetos Criados")
    
    # Implementar visualização de projetos
