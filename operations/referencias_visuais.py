import streamlit as st

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