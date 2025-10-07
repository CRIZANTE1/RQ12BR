import streamlit as st

def mostrar_referencias_visuais():
    """Exibe referências visuais para escadas industriais"""
    st.header("Referências Visuais para Escadas Industriais")
    
    tabs = st.tabs(["Dimensões Básicas", "Guarda-corpo", "Plataformas", "Exemplos"])
    
    with tabs[0]:
        st.subheader("Dimensões Básicas de Escadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Parâmetros Principais (NR-12 Anexo III)
            - **Altura do degrau (h)**: 150mm a 250mm (ideal: 180mm)
            - **Profundidade livre do degrau (g)**: Mínimo 150mm (ideal: 280-320mm)
            - **Fórmula NR-12 Item 11.g**: 600 ≤ g + 2h ≤ 660
            - **Largura mínima**: 600mm (Item 11.a)
            - **Inclinação**: 20° a 45° (Figura 1)
            """)
            
            st.markdown("""
            ### Requisitos Obrigatórios
            - Degraus com superfície antiderrapante
            - Sem saliências ou rebarbas
            - Resistência para suportar cargas
            - Fixação segura na estrutura
            - Degraus uniformes e nivelados
            """)
            
            st.info("**Nota:** Para escadas SEM espelho, a profundidade mínima é 150mm (Item 11.b). Para escadas COM espelho, é 200mm (Item 12.b).")
        
        with col2:
            st.image("https://www.metalica.com.br/wp-content/uploads/2019/05/escada-marinheiro-dimensoes.jpg", 
                    caption="Dimensões básicas de uma escada industrial", 
                    use_container_width=True)
    
    with tabs[1]:
        st.subheader("Guarda-corpo e Proteções")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Requisitos do Guarda-corpo (Item 7)
            - **Altura do travessão superior**: 1,10m a 1,20m (Item 7.c)
            - **Travessão intermediário**: a 0,70m do piso (Item 7.e)
            - **Rodapé**: Mínimo 0,20m de altura (Item 7.e)
            - **Material**: Resistente a intempéries e corrosão (Item 7.b)
            - **Superfície do travessão superior**: Não deve ser plana (Item 7.d)
            
            ### Observações Importantes
            - Dimensionamento seguro e resistente (Item 7.a)
            - Instalado em ambos os lados (Item 7.c)
            - Para escadas antigas (antes de 2010), altura mínima de 1,00m é aceita (Item 7.1)
            """)
        
        with col2:
            st.image("https://www.ciser.com.br/wp-content/uploads/2021/01/guarda-corpo-nr12.jpg", 
                    caption="Exemplo de guarda-corpo conforme NR-12", 
                    use_container_width=True)
    
    with tabs[2]:
        st.subheader("Plataformas de Descanso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Requisitos para Plataformas (Item 11.e)
            - **Quando usar**: Escadas com altura superior a 3,00m
            - **Intervalo**: A cada 3,00m de altura (máximo)
            - **Largura útil mínima**: 0,60m
            - **Comprimento mínimo**: Conforme necessidade de descanso
            - **Proteção**: Guarda-corpo em todo o perímetro
            - **Piso**: Antiderrapante e resistente
            
            ### Item 3 - NR-12
            Locais ou postos de trabalho acima do piso com acesso de trabalhadores 
            devem possuir plataformas de trabalho estáveis e seguras.
            """)
        
        with col2:
            st.image("https://www.escadasnr12.com.br/wp-content/uploads/2019/08/plataforma-descanso-escada.jpg", 
                    caption="Plataforma de descanso em escada industrial", 
                    use_container_width=True)
    
    with tabs[3]:
        st.subheader("Exemplos de Escadas Conformes")
        
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
    
    st.markdown("---")
    st.subheader("Referências Normativas")
    
    col_ref1, col_ref2 = st.columns(2)
    
    with col_ref1:
        st.markdown("""
        ### NR-12 - Anexo III
        **BRASIL. Ministério do Trabalho e Emprego.**  
        NR-12 - Segurança no Trabalho em Máquinas e Equipamentos  
        Anexo III - Meios de Acesso a Máquinas e Equipamentos  
        Brasília: MTE, 2019.
        
        **Principais itens:**
        - Item 11: Escadas de degraus sem espelho
        - Item 12: Escadas de degraus com espelho
        - Item 7: Sistema de proteção contra quedas
        """)
    
    with col_ref2:
        st.markdown("""
        ### ABNT NBR ISO 14122-3:2023
        **ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS.**  
        Segurança de máquinas — Meios de acesso permanentes às máquinas  
        Parte 3: Escadas, escadas de degraus e guarda-corpos  
        Rio de Janeiro: ABNT, 2023.
        
        Esta norma internacional complementa a NR-12 com detalhes 
        técnicos adicionais para projeto e fabricação.
        """)
    
    st.markdown("---")
    st.info("""
    **💡 Dica Importante:** A NR-12 foi atualizada pela Portaria MTP n.º 428, de 07 de outubro de 2021. 
    Máquinas que atendem normas técnicas vigentes em 30/07/2019 estão dispensadas de algumas exigências (Item 1.6).
    """)