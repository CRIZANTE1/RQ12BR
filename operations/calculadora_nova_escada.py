import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import uuid
from datetime import datetime
import pandas as pd

def calcular_nova_escada(calculadora, gerenciador_historico):
    """Interface para calcular uma nova escada"""
    col1, col2 = st.columns(2)
    
    with col1:
        altura_total = st.number_input(
            "Altura Total da Escada (mm):",
            min_value=500.0,
            max_value=10000.0,
            value=3000.0,
            step=100.0,
            help="Altura total da escada em milímetros",
            format="%.2f",
        )
        altura_degrau = st.number_input(
            "Altura do Degrau (mm):",
            min_value=150.0,
            max_value=250.0,
            value=180.0,
            step=5.0,
            help="Altura recomendada entre 150mm e 250mm (NR-12)",
            format="%.2f",
        )
        profundidade_degrau = st.number_input(
            "Profundidade do Degrau (mm):",
            min_value=150.0,
            max_value=400.0,
            value=280.0,
            step=10.0,
            help="Profundidade mínima: 150mm (NR-12 Item 11.b)",
            format="%.2f",
        )
    
    with col2:
        inclinacao_maxima = st.number_input(
            "Inclinação Máxima (graus):",
            min_value=20.0,
            max_value=45.0,
            value=35.0,
            step=1.0,
            help="Inclinação: 20° a 45° (NR-12 Figura 1)",
            format="%.1f",
        )
        largura = st.number_input(
            "Largura da Escada (mm):",
            min_value=600.0,
            max_value=2000.0,
            value=800.0,
            step=50.0,
            help="Largura mínima: 600mm (NR-12 Item 11.a)",
            format="%.2f",
        )
        local_instalacao = st.text_input("Local de Instalação:", "Escada de acesso")
    
    incluir_plataformas = st.checkbox(
        "Incluir Plataformas de Descanso",
        value=True,
        help="Recomendado para escadas com altura superior a 3000mm (NR-12 Item 11.e)"
    )
    
    if st.button("Calcular Escada"):
        # Cálculos
        num_degraus = calculadora.calcular_num_degraus(altura_total, altura_degrau)
        inclinacao = np.degrees(np.arctan(altura_degrau/profundidade_degrau))
        comprimento_projetado = num_degraus * profundidade_degrau
        num_plataformas = calculadora.calcular_num_plataformas(altura_total)
        
        # Fórmula NR-12: g + 2h
        formula_nr12 = profundidade_degrau + (2 * altura_degrau)
        formula_ok = 600 <= formula_nr12 <= 660
        
        # Resultados
        resultados = {
            'Parâmetro': [
                'Local de Instalação',
                'Altura Total da Escada',
                'Número de Degraus',
                'Altura do Degrau',
                'Profundidade do Degrau',
                'Largura da Escada',
                'Inclinação da Escada',
                'Fórmula NR-12 (g + 2h)',
                'Comprimento Total Projetado',
                'Número de Plataformas Necessárias'
            ],
            'Valor Calculado': [
                local_instalacao,
                f"{altura_total:.2f} mm",
                f"{num_degraus}",
                f"{altura_degrau:.2f} mm",
                f"{profundidade_degrau:.2f} mm",
                f"{largura:.2f} mm",
                f"{inclinacao:.1f}°",
                f"{formula_nr12:.2f} mm",
                f"{comprimento_projetado:.2f} mm",
                f"{num_plataformas}"
            ],
            'Conformidade': [
                '✅',
                '✅',
                '✅',
                '✅' if 150 <= altura_degrau <= 250 else '❌',
                '✅' if profundidade_degrau >= 150 else '❌',
                '✅' if largura >= 600 else '❌',
                '✅' if 20 <= inclinacao <= 45 else '❌',
                '✅' if formula_ok else '❌',
                '✅',
                '✅' if (num_plataformas == 0) or incluir_plataformas else '❌'
            ]
        }
        
        st.subheader("Resultados do Cálculo")
        st.dataframe(pd.DataFrame(resultados), hide_index=True)
        
        # Conformidade
        itens_ok = resultados['Conformidade'].count('✅')
        total_itens = len(resultados['Conformidade'])
        conformidade = (itens_ok / total_itens) * 100
        
        st.subheader("Conformidade do Projeto")
        if conformidade == 100:
            st.success(f"✅ 100% conforme! Todos os {total_itens} itens atendem às normas NR-12.")
        else:
            st.warning(f"⚠️ {conformidade:.1f}% conforme. {itens_ok} de {total_itens} itens atendem às normas.")
        
        # Visualização
        st.subheader("Visualização da Escada")
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Desenhar escada
        altura_acumulada = 0
        plataformas = []
        
        if incluir_plataformas and num_plataformas > 0:
            altura_entre_plataformas = altura_total / (num_plataformas + 1)
            plataformas = [(i+1) * altura_entre_plataformas for i in range(num_plataformas)]
        
        for i in range(num_degraus):
            x0 = i * profundidade_degrau
            y0 = altura_acumulada
            x1 = x0 + profundidade_degrau
            y1 = altura_acumulada + altura_degrau
            
            plataforma_aqui = False
            for p in plataformas:
                if y0 <= p <= y1:
                    plataforma_aqui = True
                    ax.axhline(y=p, color='r', linestyle='-', linewidth=2)
                    ax.text(x1 + 50, p, f"Plataforma {plataformas.index(p)+1}", color='red')
                    altura_acumulada = p
                    break
            
            if not plataforma_aqui:
                ax.plot([x0, x1], [y0, y0], "g-", linewidth=2)
                ax.plot([x1, x1], [y0, y1], "r-", linewidth=2)
                ax.plot([x0, x1], [y0, y1], "b--", linewidth=1)
                altura_acumulada = y1
        
        # Guarda-corpo
        altura_guarda_corpo = 1100
        x_coords = [i * profundidade_degrau for i in range(num_degraus + 1)]
        y_coords = [min(i * altura_degrau, altura_total) for i in range(num_degraus + 1)]
        
        for i in range(len(x_coords) - 1):
            ax.plot([x_coords[i], x_coords[i+1]], 
                   [y_coords[i] + altura_guarda_corpo, y_coords[i+1] + altura_guarda_corpo], 
                   'k-', linewidth=2)
        
        for i in range(len(x_coords)):
            ax.plot([x_coords[i], x_coords[i]], 
                   [y_coords[i], y_coords[i] + altura_guarda_corpo], 
                   'k-', linewidth=2)
        
        ax.set_xlabel("Projeção (mm)")
        ax.set_ylabel("Altura (mm)")
        ax.set_title("Projeto da Escada - Conforme NR-12")
        ax.grid(True, linestyle="--", alpha=0.7)
        
        ax.text(0.05, 0.95, f"Inclinação: {inclinacao:.1f}°", transform=ax.transAxes, 
                fontsize=12, verticalalignment='top', 
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
        
        ax.set_xlim(0, (num_degraus + 1) * profundidade_degrau)
        ax.set_ylim(0, altura_total * 1.2)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.session_state.figura_escada = fig
        st.session_state.calculo_realizado = True
        st.session_state.dados_calculo = {
            'local': local_instalacao,
            'altura_total': altura_total,
            'num_degraus': num_degraus,
            'altura_degrau': altura_degrau,
            'profundidade_degrau': profundidade_degrau,
            'largura': largura,
            'inclinacao': inclinacao,
            'formula_nr12': formula_nr12,
            'comprimento_projetado': comprimento_projetado,
            'num_plataformas': num_plataformas,
            'incluir_plataformas': incluir_plataformas
        }
    
    # Salvar projeto
    if 'calculo_realizado' in st.session_state and st.session_state.calculo_realizado:
        if st.button("Salvar Projeto no Histórico"):
            gerenciador_historico.criar_diretorios()
            calculo_id = str(uuid.uuid4())
            grafico_path = f"images/grafico_{calculo_id}.png"
            st.session_state.figura_escada.savefig(grafico_path)
            
            calculo = {
                'id': calculo_id,
                'tipo': 'Projeto',
                'local': st.session_state.dados_calculo['local'],
                'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'altura_total': st.session_state.dados_calculo['altura_total'],
                'medidas': resultados['Parâmetro'],
                'valores': resultados['Valor Calculado'],
                'status_itens': resultados['Conformidade'],
                'grafico_path': grafico_path
            }
            
            if 'historico_avaliacoes' not in st.session_state:
                st.session_state.historico_avaliacoes = []
            
            st.session_state.historico_avaliacoes.append(calculo)
            gerenciador_historico.salvar_historico_json(st.session_state.historico_avaliacoes)
            
            st.success("✅ Projeto salvo no histórico com sucesso!")
            st.session_state.calculo_realizado = False
            st.rerun()