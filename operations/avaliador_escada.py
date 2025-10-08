# --- START OF FILE avaliador_escada.py ---

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import streamlit as st
from operations.calculadora_escada import CalculadoraEscada
from operations.referencias_visuais import mostrar_referencias_visuais
from operations.db_manager import salvar_avaliacao, salvar_arquivo, fig_to_bytes
import uuid
from datetime import datetime

def avaliar_escada_existente(calculadora):
    """Interface para avaliar uma escada existente"""
    # O form agrupa os inputs. A avaliação só ocorre ao clicar no botão de submit do form.
    with st.form(key="avaliacao_form"):
        # Colunas para organizar a entrada de dados
        col1, col2 = st.columns(2)
        
        with col1:
            local_instalacao = st.text_input("Local de Instalação:", "Escada de acesso")
            altura_total = st.number_input(
                "Altura Total da Escada (mm):",
                min_value=500.0, value=3000.0, step=100.0, format="%.1f",
            )
            altura_degrau = st.number_input(
                "Altura do Degrau (mm):",
                min_value=100.0, value=180.0, step=10.0, format="%.1f",
            )
            profundidade_degrau = st.number_input(
                "Profundidade do Degrau (mm):",
                min_value=150.0, value=280.0, step=10.0, format="%.1f",
            )
        
        with col2:
            largura = st.number_input(
                "Largura da Escada (mm):",
                min_value=500.0, value=800.0, step=50.0, format="%.1f",
            )
            tem_saliencias = st.checkbox("Degraus possuem saliências?")
            altura_guarda_corpo = st.number_input(
                "Altura do Guarda-corpo (mm):",
                min_value=0.0, value=1100.0, step=50.0, format="%.1f",
            )
            altura_rodape = st.number_input(
                "Altura do Rodapé (mm):",
                min_value=0.0, value=200.0, step=10.0, format="%.1f",
            )
        
        # Opção para plataforma
        tem_plataforma = st.checkbox(
            "A escada possui plataforma de descanso?",
            value=False,
            help="Marque se a escada possui plataforma de descanso"
        )
        
        altura_plataforma = 0.0
        largura_plataforma = 0.0
        comprimento_plataforma = 0.0

        if tem_plataforma:
            col_plat1, col_plat2 = st.columns(2)
            with col_plat1:
                altura_plataforma = st.number_input(
                    "Altura da Plataforma (mm):",
                    min_value=0.0,
                    max_value=altura_total,
                    value=altura_total / 2,
                    step=100.0,
                    help="Altura da plataforma em relação ao piso",
                    format="%.1f",
                )
            with col_plat2:
                largura_plataforma = st.number_input(
                    "Largura da Plataforma (mm):",
                    min_value=500.0,
                    max_value=3000.0,
                    value=800.0,
                    step=50.0,
                    help="Largura da plataforma em milímetros",
                    format="%.1f",
                )
                comprimento_plataforma = st.number_input(
                    "Comprimento da Plataforma (mm):",
                    min_value=500.0,
                    max_value=4000.0,
                    value=800.0,
                    step=50.0,
                    help="Comprimento da plataforma em milímetros",
                    format="%.1f",
                )
        
        # Upload de foto
        foto_escada = st.file_uploader("Carregar foto da escada (opcional):", type=["jpg", "jpeg", "png"])
        
        # Botão de submit do form
        submitted = st.form_submit_button("Avaliar Conformidade")

    if submitted:
            # Set a flag in session state to indicate that the button has been pressed
            st.session_state.avaliacao_realizada = True

            # Inicializar variáveis com valores padrão
            num_degraus = 0
            resultados_avaliacao = {}
            resultados_protecoes = {}
            resultados_plataforma = {}

            # Calcular número de degraus
            num_degraus = calculadora.calcular_num_degraus(altura_total, altura_degrau)
            
            # Calcular número de plataformas necessárias
            num_plataformas_necessarias = calculadora.calcular_num_plataformas(altura_total)
            
            # Avaliar conformidade da escada
            resultados_avaliacao = calculadora.avaliar_escada(
                altura_total, altura_degrau, profundidade_degrau, largura, 
                tem_saliencias, altura_guarda_corpo, altura_rodape
            )
            
            # Avaliar proteções
            resultados_protecoes = calculadora.avaliar_protecoes(altura_guarda_corpo, altura_rodape)
            
            # Avaliar plataforma se existir
            resultados_plataforma = {}
            if tem_plataforma:
                resultados_plataforma = calculadora.avaliar_plataforma(
                    altura_plataforma, largura_plataforma, comprimento_plataforma, altura_total
                )

            # Store the results in session state
            st.session_state.resultados_avaliacao = resultados_avaliacao
            st.session_state.resultados_protecoes = resultados_protecoes
            st.session_state.resultados_plataforma = resultados_plataforma
            
            # Criar DataFrame para exibir os resultados
            medidas_dict = {
                'Medida': [
                    'Local de Instalação',
                    'Altura Total da Escada',
                    'Altura do Degrau',
                    'Profundidade do Degrau',
                    'Largura da Escada',
                    'Fórmula de Blondel (2h + p)',
                    'Inclinação da Escada',
                    'Número de Degraus',
                    'Altura do Guarda-corpo',
                    'Altura do Rodapé'
                ],
                'Valor Atual': [
                    local_instalacao if local_instalacao else "Não informado",
                    f"{altura_total:.1f} mm",
                    f"{altura_degrau:.1f} mm",
                    f"{profundidade_degrau:.1f} mm",
                    f"{largura:.1f} mm",
                    f"{(2 * altura_degrau) + profundidade_degrau:.1f} mm",
                    f"{np.degrees(np.arctan(altura_degrau/profundidade_degrau)):.1f}°",
                    f"{num_degraus}",
                    f"{altura_guarda_corpo:.1f} mm",
                    f"{altura_rodape:.1f} mm"
                ],
                'Valor Mínimo': [
                    '-',
                    '-',
                    '0',
                    '250',
                    '800',
                    '630',
                    '30°',
                    '-',
                    '1100',
                    '200'
                ],
                'Valor Máximo': [
                    '-',
                    '-',
                    '250',
                    '-',
                    '-',
                    '640',
                    '38°',
                    '-',
                    '-',
                    '-'
                ],
                'Status': [
                    '✅',  # Local de instalação sempre ok
                    '✅',  # Altura total sempre ok
                    '✅' if resultados_avaliacao['altura_degrau_ok'] else '❌',
                    '✅' if resultados_avaliacao['profundidade_ok'] else '❌',
                    '✅' if resultados_avaliacao['largura_ok'] else '❌',
                    '✅' if resultados_avaliacao['formula_blondel_ok'] else '❌',
                    '✅' if resultados_avaliacao['inclinacao_ok'] else '❌',
                    '✅',  # Número de degraus sempre ok
                    '✅' if resultados_protecoes['guarda_corpo_ok'] else '❌',
                    '✅' if resultados_protecoes['rodape_ok'] else '❌'
                ],
                'Recomendação de Ajuste': [
                    '-',  # Local de instalação sempre ok
                    '-',  # Altura total sempre ok
                    f'Ajustar a altura do degrau para {altura_degrau:.1f} mm para atender à fórmula de Blondel. Valor ideal: 635 mm.' if not resultados_avaliacao['altura_degrau_ok'] else '-',
                    f'Aumentar a profundidade do degrau para pelo menos 250 mm. Valor atual: {profundidade_degrau:.1f} mm.' if not resultados_avaliacao['profundidade_ok'] else '-',
                    f'Aumentar a largura da escada para pelo menos 800 mm. Valor atual: {largura:.1f} mm.' if not resultados_avaliacao['largura_ok'] else '-',
                    f'Ajustar a altura do degrau ou a profundidade para atender à fórmula de Blondel (2h + p = 635 mm). Valor atual: {2*altura_degrau + profundidade_degrau:.1f} mm.' if not resultados_avaliacao['formula_blondel_ok'] else '-',
                    f'Ajustar a inclinação para estar entre 30° e 38°. Inclinação atual: {np.degrees(np.arctan(altura_degrau/profundidade_degrau)):.1f}°.' if not resultados_avaliacao['inclinacao_ok'] else '-',
                    '-',  # Número de degraus sempre ok
                    f'Aumentar a altura do guarda-corpo para pelo menos 1100 mm. Valor atual: {altura_guarda_corpo:.1f} mm.' if not resultados_protecoes['guarda_corpo_ok'] else '-',
                    f'Aumentar a altura do rodapé para pelo menos 200 mm. Valor atual: {altura_rodape:.1f} mm.' if not resultados_protecoes['rodape_ok'] else '-'
                ]
            }

            # Adicionar informações da plataforma se existir
            if tem_plataforma:
                medidas_dict['Medida'].extend([
                    'Altura da Plataforma',
                    'Largura da Plataforma',
                    'Comprimento da Plataforma'
                ])
                medidas_dict['Valor Atual'].extend([
                    f"{altura_plataforma:.1f} mm",
                    f"{largura_plataforma:.1f} mm",
                    f"{comprimento_plataforma:.1f} mm"
                ])
                medidas_dict['Valor Mínimo'].extend([
                    '-',
                    '800',
                    '800'
                ])
                medidas_dict['Valor Máximo'].extend([
                    '3000',
                    '-',
                    '-'
                ])
                medidas_dict['Status'].extend([
                    '✅' if resultados_plataforma['altura_plataforma_ok'] else '❌',
                    '✅' if resultados_plataforma['largura_plataforma_ok'] else '❌',
                    '✅' if resultados_plataforma['comprimento_plataforma_ok'] else '❌'
                ])
                medidas_dict['Recomendação de Ajuste'].extend([
                    # CORREÇÃO: Adicionada recomendação para altura da plataforma
                    'Posicionar plataforma a cada 3000mm de altura.' if not resultados_plataforma['altura_plataforma_ok'] else '-',
                    'Aumentar largura da plataforma para pelo menos 800mm' if not resultados_plataforma['largura_plataforma_ok'] else '-',
                    'Aumentar comprimento da plataforma para pelo menos 800mm' if not resultados_plataforma['comprimento_plataforma_ok'] else '-'
                ])
            
            # Criar DataFrame
            df_medidas = pd.DataFrame(medidas_dict)
            st.session_state.df_medidas = df_medidas # Store df_medidas in session state
            
            # Criar gráfico da escada
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Desenhar a escada
            altura_acumulada = 0
            for i in range(num_degraus):
                x0 = i * profundidade_degrau
                y0 = altura_acumulada
                x1 = x0 + profundidade_degrau
                y1 = altura_acumulada + altura_degrau
                
                # Desenha o degrau
                ax.plot([x0, x1], [y0, y0], "g-", linewidth=2)
                ax.plot([x1, x1], [y0, y1], "r-", linewidth=2)
                ax.plot([x0, x1], [y0, y1], "b--", linewidth=1)
                
                # Adiciona plataforma se necessário
                if tem_plataforma and y1 >= altura_plataforma and altura_acumulada < altura_plataforma:
                    ax.axhline(y=altura_plataforma, color='r', linestyle='-', linewidth=2)
                    ax.text(x1 + 50, altura_plataforma, "Plataforma", color='red')
                
                altura_acumulada = y1
            
            # Adicionar guarda-corpo
            if altura_guarda_corpo > 0:
                # Desenhar guarda-corpo ao longo da escada
                x_coords = [i * profundidade_degrau for i in range(num_degraus + 1)]
                y_coords = [min(i * altura_degrau, altura_total) for i in range(num_degraus + 1)]
                
                # Linha superior do guarda-corpo
                for i in range(len(x_coords) - 1):
                    ax.plot([x_coords[i], x_coords[i+1]], 
                           [y_coords[i] + altura_guarda_corpo, y_coords[i+1] + altura_guarda_corpo], 
                           'k-', linewidth=2)
                
                # Postes verticais do guarda-corpo
                for i in range(len(x_coords)):
                    ax.plot([x_coords[i], x_coords[i]], 
                           [y_coords[i], y_coords[i] + altura_guarda_corpo], 
                           'k-', linewidth=2)
            
            ax.set_xlabel("Projeção (mm)")
            ax.set_ylabel("Altura (mm)")
            ax.set_title("Escada Completa com Plataformas")
            ax.grid(True, linestyle="--", alpha=0.7)
            
            # Adiciona a inclinação da escada no gráfico
            inclinacao = np.degrees(np.arctan(altura_degrau/profundidade_degrau))
            ax.text(0.05, 0.95, f"Inclinação: {inclinacao:.1f}°", transform=ax.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
            
            # Ajustar limites do gráfico
            ax.set_xlim(0, (num_degraus + 1) * profundidade_degrau)
            ax.set_ylim(0, altura_total * 1.2)  # Dar espaço para o guarda-corpo
            
            plt.tight_layout()
            
            # Salvar a figura na sessão para uso posterior
            st.session_state.figura_escada = fig
            
            # Verificar se precisa de plataformas adicionais
            if num_plataformas_necessarias > 0 and not tem_plataforma:
                st.warning(f"⚠️ Para esta altura de escada ({altura_total:.1f} mm), são necessárias {num_plataformas_necessarias} plataformas de descanso.")
            
            # Aviso de inclinação excessiva
            if inclinacao > 38:
                st.error(f"⚠️ A inclinação da escada ({inclinacao:.1f}°) é maior que o máximo permitido de 38°. A escada está muito íngreme e pode ser perigosa.")
            
            # Após a avaliação, habilitar o botão de salvar
            st.session_state.avaliacao_realizada = True
            st.session_state.dados_avaliacao = {
                'local': local_instalacao if local_instalacao else "Não informado",
                'altura_total': altura_total,
                'medidas': df_medidas['Medida'].tolist(),
                'valores': df_medidas['Valor Atual'].tolist(),
                'status_itens': df_medidas['Status'].tolist(),
                'recomendacoes': df_medidas['Recomendação de Ajuste'].tolist(),
                'foto_escada': foto_escada
            }
    
    # A lógica para exibir os resultados e o botão de salvar precisa estar fora do form, 
    # mas depender da flag 'avaliacao_realizada'.
    if 'avaliacao_realizada' in st.session_state and st.session_state.avaliacao_realizada:
        # Recupere df_medidas da session_state
        df_medidas = st.session_state.df_medidas
        
        # Exibir resultados
        st.subheader("Resultados da Avaliação")
        st.dataframe(df_medidas, hide_index=True)
        
        # Calcular conformidade geral
        itens_ok = df_medidas['Status'].value_counts().get('✅', 0)
        total_itens = len(df_medidas)
        conformidade = (itens_ok / total_itens) * 100
        
        # Exibir conformidade
        st.subheader("Conformidade Geral")
        if conformidade == 100:
            st.success(f"✅ 100% conforme! Todos os {total_itens} itens atendem às normas.")
        else:
            st.warning(f"⚠️ {conformidade:.1f}% conforme. {itens_ok} de {total_itens} itens atendem às normas.")
        
        # Criar gráfico da escada (já está em st.session_state.figura_escada)
        st.subheader("Visualização da Escada")
        st.pyplot(st.session_state.figura_escada)

        # Botão de salvar
        if st.button("Salvar no Histórico"):
            avaliacao_id = str(uuid.uuid4())
            
            # 1. Salvar o GRÁFICO no Supabase Storage
            grafico_url = None
            if 'figura_escada' in st.session_state:
                grafico_bytes = fig_to_bytes(st.session_state.figura_escada)
                grafico_url = salvar_arquivo(grafico_bytes, f"grafico_{avaliacao_id}.png")

            # 2. Salvar a FOTO no Supabase Storage
            foto_url = None
            foto_escada_obj = st.session_state.dados_avaliacao['foto_escada']
            if foto_escada_obj is not None:
                foto_bytes = foto_escada_obj.getvalue()
                foto_url = salvar_arquivo(foto_bytes, f"foto_{avaliacao_id}.png", content_type=foto_escada_obj.type)
            
            # 3. Criar o dicionário da avaliação com as URLs
            avaliacao = {
                'local': st.session_state.dados_avaliacao['local'],
                'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'altura_total': st.session_state.dados_avaliacao['altura_total'],
                'medidas': st.session_state.dados_avaliacao['medidas'],
                'valores': st.session_state.dados_avaliacao['valores'],
                'status_itens': st.session_state.dados_avaliacao['status_itens'],
                'recomendacoes': st.session_state.dados_avaliacao['recomendacoes'],
                'grafico_url': grafico_url,
                'foto_url': foto_url,
                'tipo': 'Avaliação'
            }
            
            # 4. Salvar os dados no banco de dados PostgreSQL
            salvar_avaliacao(avaliacao)
            
            st.success("Avaliação salva no histórico com sucesso!")
            
            # Limpa o estado da sessão para forçar o recarregamento do histórico
            st.session_state.avaliacao_realizada = False
            if 'historico_avaliacoes' in st.session_state:
                del st.session_state.historico_avaliacoes
            st.rerun()