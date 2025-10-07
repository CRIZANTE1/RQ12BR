import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import uuid
from operations.calculadora_escada import CalculadoraEscada, GerenciadorHistorico
from operations.avaliador_escada import avaliar_escada_existente
from operations.calculadora_nova_escada import calcular_nova_escada
from operations.referencias_visuais import mostrar_referencias_visuais
from operations.historico_avaliacoes import mostrar_historico_avaliacoes
from auth.auth_utils import (
    get_effective_user_plan, 
    has_pro_features, 
    has_ai_features,
    get_user_info
)

# Inicializar calculadora e gerenciador de histórico
calculadora = CalculadoraEscada()
gerenciador_historico = GerenciadorHistorico()

def front():
    """Função principal para a interface do usuário"""
    st.set_page_config(
        page_title="RQ12BR - Avaliador de Escadas NR-12",
        page_icon="🪜",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("RQ12BR - Avaliador de Escadas NR-12")
    st.markdown("### Ferramenta para avaliação de conformidade de escadas industriais")

    # Obter informações do usuário e plano
    user_info = get_user_info()
    plano_atual = get_effective_user_plan()
    
    # Exibir informações do plano na sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Seu Plano")
    st.sidebar.info(f"**{plano_atual.replace('_', ' ').title()}**")
    
    # Recursos disponíveis por plano
    if plano_atual == 'basico':
        st.sidebar.markdown("""
        ✅ Avaliar até 5 escadas/mês
        ❌ Calcular novas escadas
        ❌ Análise com IA
        """)
    elif plano_atual in ['pro', 'premium_ia']:
        st.sidebar.markdown("""
        ✅ Avaliações ilimitadas
        ✅ Calcular novas escadas
        ✅ Relatórios em PDF
        """)
        if plano_atual == 'premium_ia':
            st.sidebar.markdown("✅ Análise com IA")

    # Menu lateral
    opcoes_disponiveis = ["Calculadora de Escadas", "Referências Visuais", "Histórico de Avaliações"]
    
    opcao = st.sidebar.selectbox(
        "Selecione uma opção:",
        opcoes_disponiveis
    )

    if opcao == "Calculadora de Escadas":
        mostrar_calculadora()
    elif opcao == "Referências Visuais":
        mostrar_referencias_visuais()
    elif opcao == "Histórico de Avaliações":
        mostrar_historico_avaliacoes()


def mostrar_calculadora():
    """Exibe a calculadora de escadas com controle de acesso"""
    st.header("Calculadora de Escadas")
    
    plano_atual = get_effective_user_plan()
    
    # Verificar limite de avaliações para plano básico
    if plano_atual == 'basico':
        # Contar avaliações do mês atual
        if 'historico_avaliacoes' in st.session_state:
            from datetime import datetime
            mes_atual = datetime.now().strftime("%m/%Y")
            avaliacoes_mes = [
                a for a in st.session_state.historico_avaliacoes 
                if mes_atual in a.get('data', '')
            ]
            
            if len(avaliacoes_mes) >= 5:
                st.error("🚫 Você atingiu o limite de 5 avaliações mensais do plano básico.")
                st.info("Upgrade para o plano Pro para avaliações ilimitadas!")
                return
            else:
                st.info(f"📊 Avaliações este mês: {len(avaliacoes_mes)}/5")
    
    # Tabs para os modos da calculadora
    if plano_atual == 'basico':
        modo = "Avaliar Escada Existente"
        st.info("💡 O modo 'Calcular Nova Escada' está disponível apenas nos planos Pro e Premium.")
    else:
        modo = st.radio(
            "Selecione o modo:",
            ["Avaliar Escada Existente", "Calcular Nova Escada"],
            horizontal=True
        )
    
    if modo == "Avaliar Escada Existente":
        avaliar_escada_existente(calculadora, gerenciador_historico)
    elif modo == "Calcular Nova Escada":
        if has_pro_features():
            calcular_nova_escada(calculadora, gerenciador_historico)
        else:
            st.warning("🔒 Este recurso está disponível apenas nos planos Pro e Premium.")
            st.info("Entre em contato para fazer upgrade!")


def mostrar_referencias_visuais():
    """Exibe referências visuais para escadas industriais"""
    st.header("Referências Visuais para Escadas Industriais")
    
    # Criar abas para diferentes tipos de referências
    tabs = st.tabs(["Dimensões Básicas", "Guarda-corpo", "Plataformas", "Exemplos"])
    
    with tabs[0]:
        st.subheader("Dimensões Básicas de Escadas")
        
        # Criar colunas para organizar o conteúdo
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Parâmetros Principais
            - **Altura do degrau (h)**: 150mm a 200mm (ideal: 180mm)
            - **Profundidade do degrau (p)**: Mínimo 250mm (ideal: 280mm)
            - **Fórmula de Blondel**: 2h + p = 630mm a 640mm
            - **Largura mínima**: 800mm
            - **Inclinação máxima**: 38°
            """)
            
            st.markdown("""
            ### Requisitos NR-12
            - Degraus com superfície antiderrapante
            - Sem saliências ou rebarbas
            - Resistência para suportar cargas móveis
            - Fixação segura na estrutura
            """)
        
        with col2:
            # Imagem ilustrativa das dimensões básicas
            st.image("https://www.metalica.com.br/wp-content/uploads/2019/05/escada-marinheiro-dimensoes.jpg", 
                    caption="Dimensões básicas de uma escada industrial", 
                    use_container_width=True)
    
    with tabs[1]:
        st.subheader("Guarda-corpo e Proteções")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Requisitos do Guarda-corpo
            - **Altura mínima**: 1100mm
            - **Travessão intermediário**: a 700mm do piso
            - **Rodapé**: 200mm de altura
            - **Vãos**: Não devem permitir a passagem de uma esfera de 110mm
            - **Resistência**: Suportar esforços de 150 kgf/m
            """)
        
        with col2:
            # Imagem ilustrativa de guarda-corpo
            st.image("https://www.ciser.com.br/wp-content/uploads/2021/01/guarda-corpo-nr12.jpg", 
                    caption="Exemplo de guarda-corpo conforme NR-12", 
                    use_container_width=True)
    
    with tabs[2]:
        st.subheader("Plataformas de Descanso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Requisitos para Plataformas
            - **Quando usar**: Escadas com altura superior a 3000mm
            - **Posicionamento**: A cada 3000mm de altura
            - **Dimensões mínimas**: 800mm x 800mm
            - **Proteção**: Guarda-corpo em todo o perímetro
            - **Piso**: Antiderrapante e resistente
            """)
        
        with col2:
            # Imagem ilustrativa de plataforma
            st.image("https://www.escadasnr12.com.br/wp-content/uploads/2019/08/plataforma-descanso-escada.jpg", 
                    caption="Plataforma de descanso em escada industrial", 
                    use_container_width=True)
    
    with tabs[3]:
        st.subheader("Exemplos de Escadas Conformes")
        
        # Galeria de exemplos
        col1, col2 = st.columns(2)
        
        with col1:
            st.image("https://www.metalurgicasc.com.br/wp-content/uploads/2021/03/escada-industrial-nr12.jpg", 
                    caption="Escada industrial com guarda-corpo", 
                    use_container_width=True)
            
            st.image("https://www.escadasnr12.com.br/wp-content/uploads/2019/08/escada-marinheiro-nr12.jpg", 
                    caption="Escada tipo marinheiro com gaiola de proteção", 
                    use_container_width=True)
        
        with col2:
            st.image("https://www.metalica.com.br/wp-content/uploads/2019/05/escada-industrial-plataforma.jpg", 
                    caption="Escada com plataforma intermediária", 
                    use_container_width=True)
            
            st.image("https://www.ciser.com.br/wp-content/uploads/2021/01/escada-industrial-nr12-exemplo.jpg", 
                    caption="Escada industrial com degraus antiderrapantes", 
                    use_container_width=True)
    
    # Adicionar referências normativas em formato ABNT
    st.markdown("---")
    st.subheader("Referências Normativas")
    st.markdown("""
    - BRASIL. Ministério do Trabalho e Emprego. **NR-12 - Segurança no Trabalho em Máquinas e Equipamentos**. Brasília: MTE, 2019.
    
    - ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. **ABNT NBR ISO 14122-3:2023**: Segurança de máquinas — Meios de acesso permanentes às máquinas — Parte 3: Escadas, escadas de degraus e guarda-corpos. Rio de Janeiro: ABNT, 2023.
    """)


def mostrar_historico_avaliacoes():
    """Exibe o histórico de avaliações salvas"""
    st.header("Histórico de Avaliações")
    
    # Criar diretórios se não existirem
    gerenciador_historico.criar_diretorios()
    
    # Carregar histórico do JSON se não estiver na sessão
    if 'historico_avaliacoes' not in st.session_state:
        historico_json = gerenciador_historico.carregar_historico_json()
        st.session_state.historico_avaliacoes = historico_json
    
    # Exibir histórico existente
    if not st.session_state.historico_avaliacoes:
        st.info("Nenhuma avaliação salva no histórico. Realize avaliações na calculadora e salve-as para visualizar aqui.")
    else:
        # Mostrar lista de avaliações salvas em formato de tabela com imagens
        st.subheader("Avaliações Salvas")
        
        # Criar colunas para cada avaliação
        num_avaliacoes = len(st.session_state.historico_avaliacoes)
        colunas_por_linha = 3
        
        # Dividir em linhas
        for i in range(0, num_avaliacoes, colunas_por_linha):
            cols = st.columns(colunas_por_linha)
            
            # Preencher cada coluna com uma avaliação
            for j in range(colunas_por_linha):
                idx = i + j
                if idx < num_avaliacoes:
                    avaliacao = st.session_state.historico_avaliacoes[idx]
                    
                    with cols[j]:
                        st.markdown(f"**ID:** {avaliacao['id']}")
                        st.markdown(f"**Local:** {avaliacao.get('local', 'Não informado')}")
                        st.markdown(f"**Data:** {avaliacao.get('data', 'Não informada')}")
                        
                        # Exibir foto se existir
                        foto_path = avaliacao.get('foto_path')
                        if foto_path and os.path.exists(foto_path):
                            st.image(foto_path, caption="Foto da escada", width=200)
                        else:
                            st.info("Sem foto")
                        
                        # Calcular conformidade
                        itens_ok = sum(1 for status in avaliacao.get('status_itens', []) if status == '✅')
                        total_itens = len(avaliacao.get('status_itens', []))
                        if total_itens > 0:
                            conformidade = f"{(itens_ok/total_itens)*100:.1f}%"
                        else:
                            conformidade = "N/A"
                        
                        st.markdown(f"**Conformidade:** {conformidade}")
                        
                        # Botão para visualizar detalhes
                        if st.button(f"Ver Detalhes #{idx+1}", key=f"btn_detalhes_{idx}"):
                            st.session_state.avaliacao_selecionada = idx
                        
                        # Botão para excluir avaliação
                        if st.button(f"Excluir Avaliação #{idx+1}", key=f"btn_excluir_{idx}"):
                            st.session_state.historico_avaliacoes = gerenciador_historico.excluir_avaliacao(
                                st.session_state.historico_avaliacoes, idx)
                            st.success(f"Avaliação ID {avaliacao['id']} excluída com sucesso!")
                            # Remover a seleção se a avaliação excluída era a selecionada
                            if 'avaliacao_selecionada' in st.session_state and st.session_state.avaliacao_selecionada == idx:
                                del st.session_state.avaliacao_selecionada
                            st.rerun()

    # Exibir detalhes da avaliação selecionada
    if 'avaliacao_selecionada' in st.session_state and st.session_state.avaliacao_selecionada is not None:
        idx = st.session_state.avaliacao_selecionada
        if isinstance(idx, int) and 0 <= idx < len(st.session_state.historico_avaliacoes):
            avaliacao = st.session_state.historico_avaliacoes[idx]
            st.subheader(f"Detalhes da Avaliação ID: {avaliacao['id']}")
            
            # Informações básicas
            st.markdown(f"**Local:** {avaliacao.get('local', 'Não informado')}")
            st.markdown(f"**Data:** {avaliacao.get('data', 'Não informada')}")
            st.markdown(f"**Altura Total:** {avaliacao.get('altura_total', 'Não informado')} mm")
            
            # Criar colunas para gráfico e foto lado a lado
            col_grafico, col_foto = st.columns(2)
            
            with col_grafico:
                st.subheader("Gráfico da Escada")
                grafico_path = avaliacao.get('grafico_path')
                if grafico_path and os.path.exists(grafico_path):
                    st.image(grafico_path, caption="Gráfico da Escada", use_container_width=True)
                else:
                    st.info("Sem gráfico disponível")
            
            with col_foto:
                st.subheader("Foto da Escada")
                foto_path = avaliacao.get('foto_path')
                if foto_path and os.path.exists(foto_path):
                    st.image(foto_path, caption="Foto da escada", use_container_width=True)
                else:
                    st.info("Sem foto disponível")
            
            # Tabela de medidas abaixo das imagens
            st.subheader("Tabela de Medidas e Conformidade")
            medidas = avaliacao.get('medidas', [])
            valores = avaliacao.get('valores', [])
            status_itens = avaliacao.get('status_itens', [])
            recomendacoes = avaliacao.get('recomendacoes', ['-' for _ in status_itens])
            df_detalhes = pd.DataFrame({
                'Medida': medidas,
                'Valor': valores,
                'Status': status_itens,
                'Recomendação de Ajuste': recomendacoes
            })
            st.dataframe(df_detalhes, hide_index=True)