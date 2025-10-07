import streamlit as st
import sys
import os
import pandas as pd
import yaml
from datetime import date, timedelta
from functools import reduce
from datetime import datetime, timedelta
import altair as alt


# Adiciona o diretório raiz ao path para encontrar os outros módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auth.auth_utils import get_users_data
from gdrive.gdrive_upload import GoogleDriveUploader
from gdrive.config import (
    USERS_SHEET_NAME, get_central_drive_folder_id, ACCESS_REQUESTS_SHEET_NAME,
    AUDIT_LOG_SHEET_NAME, EXTINGUISHER_SHEET_NAME, SUPPORT_REQUESTS_SHEET_NAME 
)
from config.page_config import set_page_config
from utils.auditoria import log_action

set_page_config()

@st.cache_data(show_spinner=False)
def load_sheets_config():
    """Carrega a configuração de cabeçalhos das planilhas a partir de um arquivo YAML."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sheets_config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        st.error("Arquivo de configuração 'config/sheets_config.yaml' não encontrado ou inválido.")
        return {}

def provision_user_environment(user_email, user_name):
    """Cria a infraestrutura (planilha, pasta) para um novo usuário."""
    DEFAULT_SHEETS_CONFIG = load_sheets_config()
    if not DEFAULT_SHEETS_CONFIG:
        st.error("Configuração YAML das planilhas não carregada. Impossível provisionar.")
        return False, None, None
    try:
        uploader = GoogleDriveUploader()
        central_folder_id = get_central_drive_folder_id()
        
        st.info(f"1/4 - Criando planilha para {user_name}...")
        new_sheet_id = uploader.create_new_spreadsheet(f"ISF IA - Dados de {user_name}")
        
        st.info(f"2/4 - Criando pasta no Google Drive...")
        new_folder_id = uploader.create_drive_folder(f"SFIA - Arquivos de {user_name}", central_folder_id)
        
        st.info(f"3/4 - Organizando arquivos...")
        uploader.move_file_to_folder(new_sheet_id, new_folder_id)

        st.info(f"4/4 - Configurando abas e cabeçalhos...")
        uploader.setup_sheets_in_new_spreadsheet(new_sheet_id, DEFAULT_SHEETS_CONFIG)
        
        log_action("PROVISIONOU_AMBIENTE_USUARIO", f"Email: {user_email}, Sheet ID: {new_sheet_id}")
        return True, new_sheet_id, new_folder_id
    except Exception as e:
        st.error(f"Ocorreu um erro durante o provisionamento para {user_name}."); st.exception(e)
        return False, None, None

def show_page():
    st.title("👑 Painel de Controle do Super Administrador")

    tab_dashboard, tab_requests, tab_users, tab_audit, tab_support_admin = st.tabs([
        "📊 Dashboard Global", "📬 Solicitações", "👤 Usuários e Planos", "🛡️ Auditoria", "🎫 Gerenciar Solicitações de Suporte"
    ])

    try:
        matrix_uploader = GoogleDriveUploader(is_matrix=True)
    except Exception as e:
        st.error(f"Falha ao conectar com os serviços do Google. Verifique as credenciais. Erro: {e}")
        st.stop()
        
    with tab_dashboard:
        st.header("Visão Geral do Status de Todos os Usuários Ativos")
        
        # Botão para recarregar os dados
        if st.button("Recarregar Dados Globais"):
            st.cache_data.clear()
            st.rerun()
    
        # Carregamento dos dados necessários para o dashboard
        users_df = get_users_data()
        requests_data = matrix_uploader.get_data_from_sheet(ACCESS_REQUESTS_SHEET_NAME)
        df_requests = pd.DataFrame(requests_data[1:], columns=requests_data[0]) if requests_data and len(requests_data) > 1 else pd.DataFrame()
        
        # A lógica do dashboard está dentro deste if/else
        if users_df.empty:
            st.warning("Nenhum usuário cadastrado para exibir métricas.")
        else:
            # --- Seção 1: Métricas Principais (KPIs) ---
            st.subheader("📊 Métricas Principais")
            
            active_users_df = users_df[users_df['status'] == 'ativo']
            
            users_df['data_cadastro'] = pd.to_datetime(users_df['data_cadastro'], errors='coerce')
            thirty_days_ago = datetime.now() - timedelta(days=30)
            new_users_last_30_days = users_df[users_df['data_cadastro'] >= thirty_days_ago].shape[0]
            
            pending_requests_count = df_requests[df_requests['status'] == 'Pendente'].shape[0] if not df_requests.empty else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Usuários Ativos Totais", f"{active_users_df.shape[0]}")
            col2.metric("Novos Usuários (30d)", f"+{new_users_last_30_days}")
            col3.metric("Conversão de Trial (Em breve)", "N/A")
            col4.metric("Solicitações Pendentes", f"{pending_requests_count}", delta_color="inverse")
            
            st.markdown("---")
            
            # --- Seção 2: Gráficos de Distribuição ---
            st.subheader("📈 Distribuição de Usuários")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.write("**Distribuição por Plano**")
                plan_counts = active_users_df['plano'].value_counts().reset_index()
                plan_counts.columns = ['plano', 'contagem']
                
                chart = alt.Chart(plan_counts).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="contagem", type="quantitative"),
                    color=alt.Color(field="plano", type="nominal", title="Plano"),
                    tooltip=['plano', 'contagem']
                ).properties(
                    title='Planos dos Usuários Ativos'
                )
                st.altair_chart(chart, use_container_width=True)
                
            with col_chart2:
                st.write("**Atividade Recente (Novos Cadastros)**")
                
                new_users_df = users_df.dropna(subset=['data_cadastro']).copy()
                if not new_users_df.empty:
                    new_users_df['semana_cadastro'] = new_users_df['data_cadastro'].dt.to_period('W').apply(lambda r: r.start_time).dt.date
                    weekly_signups = new_users_df.groupby('semana_cadastro').size().reset_index(name='novos_cadastros')
                    
                    line_chart = alt.Chart(weekly_signups).mark_line(point=True).encode(
                        x=alt.X('semana_cadastro:T', title='Semana'),
                        y=alt.Y('novos_cadastros:Q', title='Novos Usuários'),
                        tooltip=['semana_cadastro', 'novos_cadastros']
                    ).properties(
                        title='Novos Cadastros por Semana'
                    )
                    st.altair_chart(line_chart, use_container_width=True)
                else:
                    st.info("Nenhum dado de cadastro para gerar gráfico de atividade.")
    
            st.markdown("---")
            
            # --- Seção 3: Saúde da Plataforma ---
            st.subheader("🩺 Saúde da Plataforma")
            
            col_health1, col_health2 = st.columns(2)
            
            with col_health1:
                st.write("**Usuários com Provisionamento Incompleto**")
                
                provisioning_issues = active_users_df[
                    (active_users_df['spreadsheet_id'].isnull()) | (active_users_df['spreadsheet_id'] == '') |
                    (active_users_df['folder_id'].isnull()) | (active_users_df['folder_id'] == '')
                ]
                
                if provisioning_issues.empty:
                    st.success("✅ Todos os usuários ativos estão com o ambiente provisionado.")
                else:
                    st.error(f"🚨 {len(provisioning_issues)} usuário(s) com problemas de provisionamento!")
                    st.dataframe(provisioning_issues[['email', 'nome', 'data_cadastro']], use_container_width=True)
        
            with col_health2:
                st.write("**Últimos Erros Registrados na Auditoria**")
                
                audit_data = matrix_uploader.get_data_from_sheet(AUDIT_LOG_SHEET_NAME)
                if not audit_data or len(audit_data) < 2:
                    st.info("Nenhum log de auditoria encontrado.")
                else:
                    df_log = pd.DataFrame(audit_data[1:], columns=audit_data[0])
                    error_logs = df_log[df_log['action'].str.contains("FALHA|ERRO", case=False, na=False)].copy()
                    
                    if error_logs.empty:
                        st.success("✅ Nenhum erro recente registrado.")
                    else:
                        error_logs = error_logs.sort_values(by='timestamp', ascending=False)
                        st.warning(f"Encontrados {len(error_logs)} logs de erro.")
                        st.dataframe(error_logs.head(5)[['timestamp', 'user_email', 'action', 'details']], use_container_width=True)

    with tab_requests:
        st.header("Gerenciar Solicitações de Acesso Pendentes")
        matrix_uploader = GoogleDriveUploader(is_matrix=True)
        try:
            requests_data = matrix_uploader.get_data_from_sheet(ACCESS_REQUESTS_SHEET_NAME)
            df_requests = pd.DataFrame(requests_data[1:], columns=requests_data[0]) if requests_data and len(requests_data) > 1 else pd.DataFrame()
            pending_requests = df_requests[df_requests['status'] == 'Pendente'] if not df_requests.empty else pd.DataFrame()

            if pending_requests.empty:
                st.success("✅ Nenhuma solicitação de acesso pendente.")
            else:
                st.info(f"Você tem {len(pending_requests)} solicitação(ões) para avaliar.")
                for index, request in pending_requests.iterrows():
                    with st.container(border=True):
                        st.write(f"**Usuário:** {request['nome_usuario']} (`{request['email_usuario']}`)")
                        cols = st.columns([2, 1, 1])
                        role = cols[0].selectbox("Atribuir Perfil:", ["editor", "viewer"], key=f"role_{index}")
                        
                        if cols[1].button("Aprovar e Iniciar Trial", key=f"approve_{index}", type="primary"):
                            with st.spinner(f"Provisionando ambiente para {request['nome_usuario']}..."):
                                success, sheet_id, folder_id = provision_user_environment(request['email_usuario'], request['nome_usuario'])
                                if success:
                                    today = date.today()
                                    trial_end = today + timedelta(days=14)
                                    new_user_row = [
                                        request['email_usuario'], request['nome_usuario'], role,
                                        'premium_ia', 'ativo', sheet_id, folder_id,
                                        today.isoformat(), trial_end.isoformat()
                                    ]
                                    matrix_uploader.append_data_to_sheet(USERS_SHEET_NAME, [new_user_row])
                                    matrix_uploader.update_cells(ACCESS_REQUESTS_SHEET_NAME, f"F{index + 2}", [['Aprovado']])
                                    log_action("APROVOU_ACESSO_COM_TRIAL", f"Email: {request['email_usuario']}")
                                    
                                    # NOVA FUNCIONALIDADE: Enviar notificação por email
                                    try:
                                        from utils.github_notifications import notify_access_approved
                                        notification_sent = notify_access_approved(
                                            user_email=request['email_usuario'],
                                            user_name=request['nome_usuario'],
                                            trial_days=14
                                        )
                                        if notification_sent:
                                            st.success(f"✅ Usuário {request['nome_usuario']} aprovado e notificado por email!")
                                        else:
                                            st.success(f"✅ Usuário {request['nome_usuario']} aprovado!")
                                            st.warning("⚠️ Notificação por email falhou, mas o acesso foi liberado.")
                                    except Exception as e:
                                        st.success(f"✅ Usuário {request['nome_usuario']} aprovado!")
                                        st.warning(f"⚠️ Erro na notificação: {e}")
                                    
                                    st.cache_data.clear()
                                    st.rerun()
                        
                        if cols[2].button("Rejeitar", key=f"reject_{index}"):
                            # Adiciona campo para motivo da rejeição
                            rejection_reason = st.text_input(f"Motivo da rejeição (opcional):", key=f"reason_{index}")
                            
                            matrix_uploader.update_cells(ACCESS_REQUESTS_SHEET_NAME, f"F{index + 2}", [['Rejeitado']])
                            log_action("REJEITOU_ACESSO", f"Email: {request['email_usuario']}")
                            
                            # Enviar notificação de rejeição
                            try:
                                from utils.github_notifications import notify_access_denied
                                notify_access_denied(
                                    user_email=request['email_usuario'],
                                    user_name=request['nome_usuario'],
                                    reason=rejection_reason
                                )
                                st.warning(f"Solicitação de {request['nome_usuario']} rejeitada e usuário notificado.")
                            except:
                                st.warning(f"Solicitação de {request['nome_usuario']} rejeitada.")
                            
                            st.cache_data.clear()
                            st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar solicitações: {e}")

    with tab_users:
        st.header("Gerenciar Usuários e Planos")
        users_df = get_users_data()
        if users_df.empty:
            st.info("Nenhum usuário cadastrado.")
        else:
            st.dataframe(users_df.drop(columns=['spreadsheet_id', 'folder_id'], errors='ignore'), use_container_width=True)
            st.markdown("---")
            st.subheader("Ações de Gerenciamento")
            
            user_list = users_df['email'].tolist()
            selected_email = st.selectbox("Selecione um usuário para gerenciar:", options=[""] + user_list)
            
            if selected_email:
                user_data = users_df[users_df['email'] == selected_email].iloc[0]
                user_index_in_df = users_df.index[users_df['email'] == selected_email].tolist()[0]
                
                st.write(f"**Gerenciando:** {user_data['nome']} (`{user_data['email']}`)")

                col1, col2, col3 = st.columns(3)
                with col1:
                    plan_options = ["basico", "pro", "premium_ia"]
                    new_plan = st.selectbox("Plano:", plan_options, index=plan_options.index(user_data['plano']))
                with col2:
                    status_options = ["ativo", "inativo", "cancelado"]
                    new_status = st.selectbox("Status da Conta:", status_options, index=status_options.index(user_data['status']))
                with col3:
                    role_options = ["editor", "viewer", "admin"]
                    new_role = st.selectbox("Perfil de Acesso:", role_options, index=role_options.index(user_data['role']))

                if st.button("Salvar Alterações", type="primary"):
                    row_index_in_sheet = user_index_in_df + 2 # +2 para compensar cabeçalho e index 0
                    range_to_update = f"C{row_index_in_sheet}:E{row_index_in_sheet}"
                    values_to_update = [[new_role, new_plan, new_status]]
                    
                    matrix_uploader = GoogleDriveUploader(is_matrix=True)
                    matrix_uploader.update_cells(USERS_SHEET_NAME, range_to_update, values_to_update)
                    
                    # Se um plano for atribuído manualmente, limpa a data do trial para evitar confusão.
                    if new_plan != user_data['plano'] or new_status != user_data['status']:
                         matrix_uploader.update_cells(USERS_SHEET_NAME, f"I{row_index_in_sheet}", [['']]) # Limpa a célula do trial_end_date
                    
                    log_action("ALTEROU_USUARIO", f"Email: {selected_email}, Plano: {new_plan}, Status: {new_status}, Perfil: {new_role}")
                    st.success("Usuário atualizado com sucesso!")
                    st.cache_data.clear()
                    st.rerun()

    with tab_audit:
        st.header("Log de Auditoria do Sistema")
        matrix_uploader = GoogleDriveUploader(is_matrix=True)
        log_data = matrix_uploader.get_data_from_sheet(AUDIT_LOG_SHEET_NAME)
        if not log_data or len(log_data) < 2:
            st.warning("Nenhum registro de auditoria encontrado.")
        else:
            df_log = pd.DataFrame(log_data[1:], columns=log_data[0]).sort_values(by='timestamp', ascending=False)
            st.dataframe(df_log, use_container_width=True, hide_index=True)

    with tab_support_admin:  
        st.header("🎫 Gerenciar Solicitações de Suporte")
        
        try:
            support_data = matrix_uploader.get_data_from_sheet(SUPPORT_REQUESTS_SHEET_NAME)
            if not support_data or len(support_data) < 2:
                st.info("📭 Nenhuma solicitação de suporte encontrada.")
            else:
                df_support = pd.DataFrame(support_data[1:], columns=support_data[0])
                
                # Filtros
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Status:", ["Todos", "Pendente", "Em Andamento", "Resolvido"])
                with col2:
                    type_filter = st.selectbox("Tipo:", ["Todos"] + df_support['tipo_solicitacao'].unique().tolist())
                with col3:
                    priority_filter = st.selectbox("Prioridade:", ["Todos", "Normal", "Alta", "Crítica"])
                
                # Aplica filtros
                filtered_df = df_support.copy()
                if status_filter != "Todos":
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                if type_filter != "Todos":
                    filtered_df = filtered_df[filtered_df['tipo_solicitacao'] == type_filter]
                if priority_filter != "Todos":
                    filtered_df = filtered_df[filtered_df['prioridade'] == priority_filter]
                
                # Exibe solicitações
                st.dataframe(
                    filtered_df[['data_solicitacao', 'email_usuario', 'tipo_solicitacao', 'assunto', 'prioridade', 'status']], 
                    use_container_width=True
                )
                
                # Responder solicitação
                if not filtered_df.empty:
                    st.markdown("---")
                    selected_ticket = st.selectbox(
                        "Selecionar ticket para responder:", 
                        options=[""] + filtered_df.index.tolist(),
                        format_func=lambda x: f"#{x} - {filtered_df.loc[x, 'assunto']}" if x != "" else "Selecione um ticket"
                    )
                    
                    if selected_ticket != "":
                        ticket_data = filtered_df.loc[selected_ticket]
                        
                        with st.form("response_form"):
                            st.write(f"**Respondendo:** {ticket_data['assunto']}")
                            st.write(f"**De:** {ticket_data['nome_usuario']} ({ticket_data['email_usuario']})")
                            
                            new_status = st.selectbox("Status:", ["Pendente", "Em Andamento", "Resolvido"])
                            response_text = st.text_area("Resposta:", height=150)
                            
                            if st.form_submit_button("Enviar Resposta"):
                                if response_text.strip():
                                    # Atualiza na planilha
                                    row_index = selected_ticket + 2  # +2 para cabeçalho
                                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    
                                    matrix_uploader.update_cells(SUPPORT_REQUESTS_SHEET_NAME, f"H{row_index}", [[new_status]])
                                    matrix_uploader.update_cells(SUPPORT_REQUESTS_SHEET_NAME, f"I{row_index}", [[current_time]])
                                    matrix_uploader.update_cells(SUPPORT_REQUESTS_SHEET_NAME, f"J{row_index}", [[response_text]])
                                    
                                    st.success("✅ Resposta enviada!")
                                    st.cache_data.clear()
                                    st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar solicitações: {e}")
