import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
import tempfile
from gdrive.config import get_credentials_dict, get_matrix_sheets_id

class GoogleDriveUploader:
    """
    Classe central para interagir com as APIs do Google Drive e Google Sheets.
    Opera em dois modos:
    - 'matrix' (is_matrix=True): Para ações na planilha central de gerenciamento.
    - 'user' (is_matrix=False): Para ações na planilha do usuário logado.
    """
    def __init__(self, is_matrix=False):
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.credentials = None
        self.drive_service = None
        self.sheets_service = None
        self.initialize_services()
        
        if is_matrix:
            # Modo Matriz: Usa o ID da planilha central, lido dos segredos.
            # Não há um folder_id associado, pois as ações são apenas na planilha.
            self.spreadsheet_id = get_matrix_sheets_id()
            self.folder_id = None
        else:
            # Modo Usuário: Pega os IDs do ambiente do usuário, carregados na sessão durante o login.
            self.spreadsheet_id = st.session_state.get('current_spreadsheet_id')
            self.folder_id = st.session_state.get('current_folder_id')

    def initialize_services(self):
        """Inicializa os serviços da API do Google usando as credenciais."""
        try:
            credentials_dict = get_credentials_dict()
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_dict,
                scopes=self.SCOPES
            )
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        except Exception as e:
            st.error(f"Erro fatal ao inicializar serviços do Google. Verifique suas credenciais. Detalhes: {e}")
            raise

    def get_data_from_sheet(self, sheet_name):
        """Busca todos os dados de uma aba específica da planilha selecionada."""
        if not self.spreadsheet_id:
            st.error("ID da planilha não definido. Acesso aos dados impossível."); return []
        try:
            range_name = f"{sheet_name}!A:Z"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except Exception as e:
            st.error(f"Erro ao ler dados da planilha '{sheet_name}': {e}"); raise

    def append_data_to_sheet(self, sheet_name, data_rows):
        """Adiciona uma ou mais linhas ao final de uma aba específica."""
        if not self.spreadsheet_id:
            st.error("ID da planilha não definido. A escrita de dados falhou."); return None
        try:
            # Garante que os dados estejam sempre em formato de lista de listas
            if not isinstance(data_rows, list): data_rows = []
            if data_rows and not isinstance(data_rows[0], list): data_rows = [data_rows]
            
            if not data_rows: return None # Não faz nada se não houver dados

            body = {'values': data_rows}
            return self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:A", # A:A para encontrar a primeira linha vazia
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
        except Exception as e:
            st.error(f"Erro ao adicionar dados à planilha '{sheet_name}': {e}"); raise

    def update_cells(self, sheet_name, range_name, values):
        """Atualiza um intervalo específico de células em uma aba."""
        if not self.spreadsheet_id:
            st.error("ID da planilha não definido. A atualização de dados falhou."); return None
        try:
            body = {'values': values}
            return self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
        except Exception as e:
            st.error(f"Erro ao atualizar células: {e}"); raise

    def overwrite_sheet(self, sheet_name, dataframe):
        """Apaga todo o conteúdo de uma aba e o substitui pelos dados de um DataFrame."""
        if not self.spreadsheet_id:
            st.error("ID da planilha não definido. A sobrescrita de dados falhou."); return
        try:
            # 1. Limpa a planilha
            self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id, range=sheet_name
            ).execute()
            
            # 2. Prepara os novos dados (cabeçalho + linhas)
            values = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
            body = {'values': values}

            # 3. Atualiza a planilha a partir da célula A1
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A1",
                valueInputOption='RAW', body=body
            ).execute()
        except Exception as e:
            st.error(f"Erro ao sobrescrever a planilha '{sheet_name}': {e}"); raise

    def create_new_spreadsheet(self, name):
        """Cria uma nova Planilha Google e retorna seu ID. (Função de Admin)"""
        spreadsheet_body = {'properties': {'title': name}}
        spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
        st.info(f"Planilha '{name}' criada com sucesso."); return spreadsheet.get('spreadsheetId')

    def setup_sheets_in_new_spreadsheet(self, spreadsheet_id, sheets_config):
        """Cria abas e cabeçalhos em uma nova planilha. (Função de Admin)"""
        requests = [{'addSheet': {'properties': {'title': name}}} for name in sheets_config.keys()]
        requests.append({'deleteSheet': {'sheetId': 0}}) # Remove a 'Página1' padrão
        self.sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': requests}).execute()
        for name, headers in sheets_config.items():
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=f"{name}!A1",
                valueInputOption='USER_ENTERED', body={'values': [headers]}
            ).execute()
        st.info("Abas e cabeçalhos configurados na nova planilha.")

    def create_drive_folder(self, name, parent_folder_id=None):
        """Cria uma nova pasta no Google Drive. (Função de Admin)"""
        file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
        if parent_folder_id: file_metadata['parents'] = [parent_folder_id]
        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
        st.info(f"Pasta '{name}' criada com sucesso no Google Drive."); return folder.get('id')

    def move_file_to_folder(self, file_id, folder_id):
        """Move um arquivo para uma pasta específica no Drive. (Função de Admin)"""
        file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        self.drive_service.files().update(
            fileId=file_id, addParents=folder_id, removeParents=previous_parents, fields='id, parents'
        ).execute()
        st.info("Arquivo movido para a pasta de destino.")

    def upload_file(self, arquivo, novo_nome=None):
        """Faz upload de um arquivo para a pasta do usuário logado."""
        if not self.folder_id: st.error("ID da pasta do usuário não definido. Upload falhou."); return None
        
        # Usa um arquivo temporário para garantir a compatibilidade e a limpeza
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(arquivo.name)[1]) as tmp:
            tmp.write(arquivo.getbuffer())
            tmp_path = tmp.name
        
        try:
            file_metadata = {'name': novo_nome or arquivo.name, 'parents': [self.folder_id]}
            media = MediaFileUpload(tmp_path, mimetype=arquivo.type)
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
            return file.get('webViewLink')
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path) # Garante que o arquivo temporário seja removido

    def upload_image_and_get_direct_link(self, image_file, novo_nome=None):
        """Faz upload de uma imagem, torna-a pública e retorna um link de visualização direta."""
        if not self.folder_id: st.error("ID da pasta do usuário não definido. Upload de imagem falhou."); return None
        if not image_file: return None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(image_file.getbuffer())
            tmp_path = tmp.name
            
        try:
            file_metadata = {'name': novo_nome, 'parents': [self.folder_id]}
            media = MediaFileUpload(tmp_path, mimetype='image/jpeg')
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
            file_id = file.get('id')
            self.drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
            
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)