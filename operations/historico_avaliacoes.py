# operations/historico_avaliacoes.py
import streamlit as st
import pandas as pd
from operations.db_manager import carregar_avaliacoes, excluir_avaliacao

def mostrar_historico_avaliacoes():
    """Exibe o histórico de avaliações salvas a partir do banco de dados."""
    st.header("Histórico de Avaliações")

    # Sempre carrega do banco, a menos que já esteja na sessão
    if 'historico_avaliacoes' not in st.session_state:
        with st.spinner("Carregando histórico..."):
            st.session_state.historico_avaliacoes = carregar_avaliacoes()

    if not st.session_state.historico_avaliacoes:
        st.info("Nenhuma avaliação salva no histórico.")
        return

    st.subheader("Avaliações Salvas")
    
    # Exibir detalhes da avaliação selecionada em um expander
    if 'avaliacao_selecionada' in st.session_state:
        idx = st.session_state.avaliacao_selecionada
        if 0 <= idx < len(st.session_state.historico_avaliacoes):
            avaliacao = st.session_state.historico_avaliacoes[idx]
            
            with st.expander(f"Detalhes do Item ID: {str(avaliacao['id'])[:8]}", expanded=True):
                col_grafico, col_foto = st.columns(2)
                
                with col_grafico:
                    st.subheader("Gráfico")
                    grafico_url = avaliacao.get('grafico_url')
                    if grafico_url:
                        st.image(grafico_url, use_container_width=True)
                    else:
                        st.info("Sem gráfico")
                
                with col_foto:
                    st.subheader("Foto")
                    foto_url = avaliacao.get('foto_url')
                    if foto_url:
                        st.image(foto_url, use_container_width=True)
                    else:
                        st.info("Sem foto")
                
                st.subheader("Tabela de Medidas e Conformidade")
                df_detalhes = pd.DataFrame({
                    'Medida': avaliacao.get('medidas', []),
                    'Valor': avaliacao.get('valores', []),
                    'Status': avaliacao.get('status_itens', []),
                    'Recomendação': avaliacao.get('recomendacoes', [])
                })
                st.dataframe(df_detalhes, hide_index=True)
                
                if st.button("Fechar Detalhes", key=f"btn_fechar_detalhes_{idx}"):
                    del st.session_state.avaliacao_selecionada
                    st.rerun()

    num_avaliacoes = len(st.session_state.historico_avaliacoes)
    colunas_por_linha = 3
    
    for i in range(0, num_avaliacoes, colunas_por_linha):
        cols = st.columns(colunas_por_linha)
        for j in range(colunas_por_linha):
            idx = i + j
            if idx < num_avaliacoes:
                avaliacao = st.session_state.historico_avaliacoes[idx]
                
                with cols[j]:
                    with st.container(border=True): # Adiciona uma borda para melhor visualização
                        st.markdown(f"**Tipo:** {avaliacao.get('tipo', 'Avaliação')}")
                        st.markdown(f"**Local:** {avaliacao.get('local', 'N/A')}")
                        st.markdown(f"**Data:** {avaliacao.get('data', 'N/A')}")
                        
                        foto_url = avaliacao.get('foto_url')
                        if foto_url:
                            st.image(foto_url, caption="Foto da escada", width=200)
                        
                        status_itens = avaliacao.get('status_itens', [])
                        if status_itens and len(status_itens) > 0:
                            itens_ok = sum(1 for status in status_itens if status == '✅')
                            conformidade = f"{(itens_ok / len(status_itens)) * 100:.1f}%"
                            st.markdown(f"**Conformidade:** {conformidade}")

                        botoes_col1, botoes_col2 = st.columns(2)
                        with botoes_col1:
                            if st.button(f"Ver Detalhes", key=f"btn_detalhes_{idx}"):
                                st.session_state.avaliacao_selecionada = idx
                                st.rerun()
                        
                        with botoes_col2:
                            if st.button(f"Excluir", key=f"btn_excluir_{idx}", type="primary"):
                                id_para_excluir = avaliacao['id']
                                # Lógica de exclusão
                                excluir_avaliacao(id_para_excluir)
                                st.success(f"Item ID {str(id_para_excluir)[:8]} excluído!")
                                # Atualiza a lista na session_state sem precisar recarregar tudo
                                st.session_state.historico_avaliacoes = [
                                    item for item in st.session_state.historico_avaliacoes if item['id'] != id_para_excluir
                                ]
                                if 'avaliacao_selecionada' in st.session_state:
                                    del st.session_state.avaliacao_selecionada
                                st.rerun()