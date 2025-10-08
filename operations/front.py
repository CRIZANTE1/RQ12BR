import streamlit as st
from operations.calculadora_escada import CalculadoraEscada
from operations.avaliador_escada import avaliar_escada_existente
from operations.calculadora_nova_escada import calcular_nova_escada
from operations.referencias_visuais import mostrar_referencias_visuais
from operations.historico_avaliacoes import mostrar_historico_avaliacoes

# Inicializar calculadora e gerenciador de histórico
calculadora = CalculadoraEscada()


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

    # Menu lateral
    opcao = st.sidebar.selectbox(
        "Selecione uma opção:",
        ["Calculadora de Escadas", "Referências Visuais", "Histórico de Avaliações"]
    )

    if opcao == "Calculadora de Escadas":
        mostrar_calculadora()
    elif opcao == "Referências Visuais":
        mostrar_referencias_visuais()
    elif opcao == "Histórico de Avaliações":
        mostrar_historico_avaliacoes()


def mostrar_calculadora():
    """Exibe a calculadora de escadas"""
    st.header("Calculadora de Escadas")
    
    # Tabs para os modos da calculadora
    modo = st.radio(
        "Selecione o modo:",
        ["Avaliar Escada Existente", "Calcular Nova Escada"],
        horizontal=True
    )
    
    if modo == "Avaliar Escada Existente":
        avaliar_escada_existente(calculadora)
    elif modo == "Calcular Nova Escada":
        calcular_nova_escada(calculadora)