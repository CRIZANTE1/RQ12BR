import streamlit as st
import pandas as pd
from datetime import datetime
from gdrive.gdrive_upload import GoogleDriveUploader
from gdrive.config import AVALIACOES_ESCADAS_SHEET_NAME, PROJETOS_ESCADAS_SHEET_NAME
from auth.auth_utils import get_user_info

class EscadasGDriveManager:
    """Gerenciador de salvamento de avaliações e projetos no Google Drive"""
    
    def __init__(self):
        self.uploader = GoogleDriveUploader(is_matrix=False)
        self.user_info = get_user_info()
    
    def salvar_avaliacao(self, avaliacao_data, grafico_path=None, foto_path=None):
        """
        Salva uma avaliação de escada no Google Sheets e faz upload das imagens
        """
        try:
            # Upload das imagens para o Google Drive
            grafico_drive_id = None
            foto_drive_id = None
            
            if grafico_path:
                with open(grafico_path, 'rb') as f:
                    grafico_drive_id = self.uploader.upload_file(
                        f,
                        f"grafico_{avaliacao_data['id']}.png"
                    )
            
            if foto_path:
                with open(foto_path, 'rb') as f:
                    foto_drive_id = self.uploader.upload_file(
                        f,
                        f"foto_{avaliacao_data['id']}.png"
                    )
            
            # Preparar linha para a planilha
            row = [
                avaliacao_data['id'],
                avaliacao_data.get('data', datetime.now().strftime("%d/%m/%Y %H:%M")),
                avaliacao_data.get('local', 'Não informado'),
                avaliacao_data.get('tipo_escada', 'Escada com degraus'),
                avaliacao_data.get('altura_total', 0),
                avaliacao_data.get('num_degraus', 0),
                avaliacao_data.get('altura_degrau', 0),
                avaliacao_data.get('profundidade_degrau', 0),
                avaliacao_data.get('largura', 0),
                avaliacao_data.get('inclinacao', 0),
                avaliacao_data.get('formula_blondel', 0),
                avaliacao_data.get('status_conformidade', 'Pendente'),
                avaliacao_data.get('conformidade_percentual', 0),
                avaliacao_data.get('tem_plataforma', False),
                avaliacao_data.get('tem_guarda_corpo', True),
                avaliacao_data.get('observacoes', ''),
                grafico_drive_id or '',
                foto_drive_id or '',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            # Salvar na planilha
            self.uploader.append_data_to_sheet(AVALIACOES_ESCADAS_SHEET_NAME, [row])
            
            return True, grafico_drive_id, foto_drive_id
            
        except Exception as e:
            st.error(f"Erro ao salvar avaliação no Google Drive: {e}")
            return False, None, None
    
    def salvar_projeto(self, projeto_data, grafico_path=None):
        """
        Salva um projeto de escada no Google Sheets
        """
        try:
            # Upload do gráfico
            grafico_drive_id = None
            if grafico_path:
                with open(grafico_path, 'rb') as f:
                    grafico_drive_id = self.uploader.upload_file(
                        f,
                        f"projeto_{projeto_data['id']}.png"
                    )
            
            # Preparar linha para a planilha
            row = [
                projeto_data['id'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                projeto_data.get('nome_projeto', 'Projeto sem nome'),
                projeto_data.get('local', 'Não informado'),
                projeto_data.get('altura_total', 0),
                projeto_data.get('num_degraus', 0),
                projeto_data.get('altura_degrau', 0),
                projeto_data.get('profundidade_degrau', 0),
                projeto_data.get('largura', 0),
                projeto_data.get('inclinacao', 0),
                projeto_data.get('formula_blondel', 0),
                projeto_data.get('num_plataformas', 0),
                projeto_data.get('status_projeto', 'Em análise'),
                grafico_drive_id or '',
                projeto_data.get('observacoes', '')
            ]
            
            # Salvar na planilha
            self.uploader.append_data_to_sheet(PROJETOS_ESCADAS_SHEET_NAME, [row])
            
            return True, grafico_drive_id
            
        except Exception as e:
            st.error(f"Erro ao salvar projeto no Google Drive: {e}")
            return False, None
    
    def carregar_avaliacoes(self):
        """Carrega todas as avaliações do usuário"""
        try:
            data = self.uploader.get_data_from_sheet(AVALIACOES_ESCADAS_SHEET_NAME)
            if not data or len(data) < 2:
                return pd.DataFrame()
            
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar avaliações: {e}")
            return pd.DataFrame()
    
    def carregar_projetos(self):
        """Carrega todos os projetos do usuário"""
        try:
            data = self.uploader.get_data_from_sheet(PROJETOS_ESCADAS_SHEET_NAME)
            if not data or len(data) < 2:
                return pd.DataFrame()
            
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
            
        except Exception as e:
            st.error(f"Erro ao carregar projetos: {e}")
            return pd.DataFrame()
