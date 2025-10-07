import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import uuid
from datetime import datetime
from operations.gdrive_manager import EscadasGDriveManager
from auth.auth_utils import get_effective_user_plan

def avaliar_escada_existente(calculadora, gerenciador_historico):
    """Interface para avaliar uma escada existente"""
    # Inicializar variáveis com valores padrão
    num_degraus = 0
    resultados_avaliacao = {}
    resultados_protecoes = {}
    resultados_plataforma = {}

    # Colunas para organizar a entrada de dados
    col1, col2 = st.columns(2)
    
    with col1:
        local_instalacao = st.text_input("Local de Instalação:", "Escada de acesso")
        altura_total = st.number_input(
            "Altura Total da Escada (mm):",
            min_value=500.0,
            max_value=10000.0,
            value=3000.0,
            step=100.0,
            help="Altura total da escada em milímetros",
            format="%.1f",
        )
        altura_degrau = st.number_input(
            "Altura do Degrau (mm):",
            min_value=100.0,
            max_value=300.0,
            value=180.0,
            step=10.0,
            help="Altura de cada degrau em milímetros",
            format="%.1f",
        )
        profundidade_degrau = st.number_input(
            "Profundidade do Degrau (mm):",
            min_value=150.0,
            max_value=400.0,
            value=280.0,
            step=10.0,
            help="Profundidade de cada degrau em milímetros",
            format="%.1f",
        )
    
    with col2:
        largura = st.number_input(
            "Largura da Escada (mm):",
            min_value=500.0,
            max_value=2000.0,
            value=800.0,
            step=50.0,
            help="Largura da escada em milímetros",
            format="%.1f",
        )
        tem_saliencias = st.checkbox(
            "Degraus possuem saliências?",
            value=False,
            help="Marque se os degraus possuem saliências ou rebarbas"
        )
        altura_guarda_corpo = st.number_input(
            "Altura do Guarda-corpo (mm):",
            min_value=0.0,
            max_value=2000.0,
            value=1100.0,
            step=50.0,
            help="Altura do guarda-corpo em milímetros",
            format="%.1f",
        )
        altura_rodape = st.number_input(
            "Altura do Rodapé (mm):",
            min_value=0.0,
            max_value=500.0,
            value=200.0,
            step=10.0,
            help="Altura do rodapé em milímetros",
            format="%.1f",
        )
    
    # Opção para plataforma
    tem_plataforma = st.checkbox(
        "A escada possui plataforma de descanso?",
        value=False,
        help="Marque se a escada possui plataforma de descanso"
    )
    
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
    
    # Colunas para os botões
    col_botoes = st.columns(2)
    
    with col_botoes[0]:
        if st.button("Avaliar Conformidade"):
            # Set a flag in session state to indicate that the button has been pressed
            st.session_state.avaliacao_realizada = True

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
                    '150',  # CORRIGIDO (não '0')
                    '150',  # CORRIGIDO (não '250')
                    '600',  # CORRIGIDO (não '800')
                    '600',  # CORRIGIDO (não '630')
                    '20°',  # CORRIGIDO (não '30°')
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
                    '660',  # CORRIGIDO (não '640')
                    '45°',  # CORRIGIDO (não '38°')
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
                    '-',
                    'Aumentar largura da plataforma para pelo menos 800mm' if not resultados_plataforma['largura_plataforma_ok'] else '-',
                    'Aumentar comprimento da plataforma para pelo menos 800mm' if not resultados_plataforma['comprimento_plataforma_ok'] else '-'
                ])
            
            # Criar DataFrame
            df_medidas = pd.DataFrame(medidas_dict)
            
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
            
            # Criar gráfico da escada
            st.subheader("Visualização da Escada")
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
            st.pyplot(fig)
            
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
    
    with col_botoes[1]:
        # Botão de salvar só aparece após a avaliação
        if 'avaliacao_realizada' in st.session_state and st.session_state.avaliacao_realizada:
            if st.button("Salvar no Histórico"):
                plano_atual = get_effective_user_plan()
                
                # Verificar limite do plano básico
                if plano_atual == 'basico':
                    from datetime import datetime
                    mes_atual = datetime.now().strftime("%m/%Y")
                    avaliacoes_mes = [
                        a for a in st.session_state.get('historico_avaliacoes', []) 
                        if mes_atual in a.get('data', '')
                    ]
                    
                    if len(avaliacoes_mes) >= 5:
                        st.error("🚫 Limite de 5 avaliações mensais atingido (Plano Básico)")
                        st.info("💎 Faça upgrade para o Plano Pro para avaliações ilimitadas!")
                        st.stop()
                
                # Criar diretórios se não existirem
                gerenciador_historico.criar_diretorios()
                
                # Gerar ID único para esta avaliação
                avaliacao_id = str(uuid.uuid4())
                
                # Salvar o gráfico da escada
                grafico_path = f"images/grafico_{avaliacao_id}.png"
                
                # ... código existente para salvar gráfico ...
                
                # Processar a foto da escada
                foto_path = None
                if st.session_state.dados_avaliacao['foto_escada'] is not None:
                    foto_path = f"images/foto_{avaliacao_id}.png"
                    with open(foto_path, "wb") as f:
                        f.write(st.session_state.dados_avaliacao['foto_escada'].getvalue())
                
                # Calcular dados para o Drive
                itens_ok = sum(1 for s in st.session_state.dados_avaliacao['status_itens'] if s == '✅')
                total_itens = len(st.session_state.dados_avaliacao['status_itens'])
                conformidade = (itens_ok / total_itens) * 100 if total_itens > 0 else 0
                
                # Preparar dados da avaliação
                avaliacao_drive_data = {
                    'id': avaliacao_id,
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'local': st.session_state.dados_avaliacao['local'],
                    'tipo_escada': 'Escada com degraus',
                    'altura_total': altura_total,
                    'num_degraus': num_degraus,
                    'altura_degrau': altura_degrau,
                    'profundidade_degrau': profundidade_degrau,
                    'largura': largura,
                    'inclinacao': np.degrees(np.arctan(altura_degrau/profundidade_degrau)),
                    'formula_blondel': 2*altura_degrau + profundidade_degrau,
                    'status_conformidade': 'Conforme' if conformidade == 100 else 'Não conforme',
                    'conformidade_percentual': conformidade,
                    'tem_plataforma': tem_plataforma,
                    'tem_guarda_corpo': altura_guarda_corpo > 0,
                    'observacoes': ''
                }
                
                # Salvar no Google Drive (se disponível)
                try:
                    gdrive_manager = EscadasGDriveManager()
                    success, grafico_id, foto_id = gdrive_manager.salvar_avaliacao(
                        avaliacao_drive_data, 
                        grafico_path, 
                        foto_path
                    )
                    
                    if success:
                        st.success("✅ Avaliação salva no Google Drive!")
                    else:
                        st.warning("⚠️ Avaliação salva localmente, mas não foi possível sincronizar com o Drive")
                except Exception as e:
                    st.warning(f"⚠️ Erro ao salvar no Drive: {e}. Salvo apenas localmente.")
                
                # Criar registro local da avaliação
                avaliacao = {
                    'id': avaliacao_id,
                    'local': st.session_state.dados_avaliacao['local'],
                    'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'altura_total': st.session_state.dados_avaliacao['altura_total'],
                    'medidas': st.session_state.dados_avaliacao['medidas'],
                    'valores': st.session_state.dados_avaliacao['valores'],
                    'status_itens': st.session_state.dados_avaliacao['status_itens'],
                    'recomendacoes': st.session_state.dados_avaliacao['recomendacoes'],
                    'grafico_path': grafico_path,
                    'foto_path': foto_path
                }
                
                # Adicionar ao histórico na sessão
                if 'historico_avaliacoes' not in st.session_state:
                    st.session_state.historico_avaliacoes = []
                
                st.session_state.historico_avaliacoes.append(avaliacao)
                
                # Salvar histórico em JSON (backup local)
                gerenciador_historico.salvar_historico_json(st.session_state.historico_avaliacoes)
                
                st.success("✅ Avaliação salva com sucesso!")
                st.session_state.avaliacao_realizada = False
                st.rerun() 