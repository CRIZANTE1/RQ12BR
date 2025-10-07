import streamlit as st
import pandas as pd
import os
from operations.calculadora_escada import GerenciadorHistorico

# Inicializar o gerenciador de histórico
gerenciador_historico = GerenciadorHistorico()

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