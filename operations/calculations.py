import numpy as np

class EscadaCalculator:
    def __init__(self):
        # Dados atualizados conforme ISO NBR 14122
        self.largura_util_minima = 600  # mm - Item 11.a (não 800!)
        self.profundidade_minima_sem_espelho = 150  # mm - Item 11.b (não 250!)
        self.profundidade_minima_com_espelho = 200  # mm - Item 12.b
        self.profundidade_recomendada_min = 280  # mm (conforto)
        self.profundidade_recomendada_max = 320  # mm (conforto)
        self.altura_maxima_degrau = 250  # mm
        self.altura_maxima_plataforma = 3000  # mm (mantido)
        self.largura_minima_plataforma = 800  # mm (mantido)
        self.formula_blondel_min = 600  # mm - Item 11.g (não 630!)
        self.formula_blondel_max = 660  # mm - Item 11.g (não 640!)
        
        self.avaliacao = AvaliacaoEscada()

    def calcular_degraus(self, altura_total, com_espelho):
        """
        Calcula as dimensões dos degraus conforme Anexo 3 da NR-12.
        Baseado na figura do anexo onde:
        t = profundidade total do degrau
        g = profundidade livre do degrau (entre 280mm e 320mm para maior conforto - NBR 14122)
        r = projeção entre degraus
        p = linha de passo
        h = altura entre degraus
        """
        # Calcula número de plataformas necessárias (item e)
        num_plataformas = max(0, int(altura_total / self.altura_maxima_plataforma))
        altura_entre_plataformas = altura_total / (num_plataformas + 1)

        resultado = {
            'degraus': [],
            'plataformas': [],
            'altura_total': altura_total,
            'num_plataformas': num_plataformas
        }

        # Para cada seção entre plataformas
        for secao in range(num_plataformas + 1):
            altura_secao = altura_entre_plataformas
            
            # 1. Cálculo da altura do degrau (h)
            # Deve ser menor ou igual a 250mm (item d)
            num_degraus = int(np.ceil(altura_secao / self.altura_maxima_degrau))
            h = altura_secao / num_degraus
            
            # 2. Cálculo da profundidade livre (g)
            # Deve ser maior ou igual a 260mm (item b)
            # Para maior conforto, usar entre 280mm e 320mm (NBR 14122)
            g = self.profundidade_recomendada_min
            
            # 3. Verificação da fórmula 600 ≤ g + 2h ≤ 660
            soma = g + (2 * h)
            
            # Se não atender à fórmula, ajustamos g ou h
            if soma < 600:
                # Podemos aumentar g mantendo h, mas respeitando o máximo recomendado
                g_necessario = 600 - (2 * h)
                g = min(self.profundidade_recomendada_max, max(g_necessario, self.profundidade_recomendada_min))
            elif soma > 660:
                # Podemos diminuir h mantendo g no mínimo recomendado
                h = (660 - g) / 2
                # Recalcula número de degraus com novo h
                num_degraus = int(np.ceil(altura_secao / h))

            # 4. Cálculo da linha de passo (p)
            p = np.sqrt(g * g + h * h)
            
            # 5. Cálculo da projeção (r) e profundidade total (t)
            # r é a projeção do degrau superior sobre o inferior
            r = 0
            t = g + r

            # Adiciona degraus desta seção
            for i in range(num_degraus):
                degrau = {
                    'altura': h,
                    'profundidade_total': t,
                    'profundidade_livre': g,
                    'linha_passo': p,
                    'projecao': r,
                    'inclinacao': np.degrees(np.arctan(h/g)),
                    'largura': self.largura_util_minima,
                    'soma_g_2h': g + (2 * h)  # Para verificação
                }
                resultado['degraus'].append(degrau)

            # Adiciona plataforma se não for a última seção
            if secao < num_plataformas:
                plataforma = {
                    'altura': (secao + 1) * altura_entre_plataformas,
                    'largura': self.largura_minima_plataforma,
                    'comprimento': self.largura_minima_plataforma
                }
                resultado['plataformas'].append(plataforma)

        return resultado

class AvaliacaoEscada:
    def __init__(self):
        # Limites conforme Anexo 3 NR-12
        self.largura_minima = 800  # mm (item a)
        self.profundidade_minima = 260  # mm (ajustado para pé tamanho 40)
        self.profundidade_recomendada_min = 280  # mm (NBR 14122 - conforto)
        self.profundidade_recomendada_max = 320  # mm (NBR 14122 - conforto)
        self.altura_maxima_degrau = 250  # mm (item d)
        self.altura_maxima_entre_plataformas = 3000  # mm (item e)
        self.formula_nr12_min = 600  # mm (item g)
        self.formula_nr12_max = 660  # mm (item g)
        self.altura_minima_guarda_corpo = 1100  # mm
        self.altura_minima_rodape = 200  # mm
        self.comprimento_minimo_plataforma = 800  # mm (item e)
        self.largura_minima_plataforma = 800  # mm (item e)

    def avaliar_dimensoes(self, largura, altura_degrau, profundidade_livre):
        """
        Avalia as dimensões conforme ISO NBR 14122.
        """
        resultados = {}

        # a) Largura útil mínima (w)
        resultados['largura_ok'] = largura >= self.largura_minima

        # b) Profundidade livre mínima do degrau (g)
        resultados['profundidade_ok'] = profundidade_livre >= self.profundidade_minima
        resultados['profundidade_confortavel'] = self.profundidade_recomendada_min <= profundidade_livre <= self.profundidade_recomendada_max

        # d) Altura máxima entre degraus (h)
        resultados['altura_degrau_ok'] = altura_degrau <= self.altura_maxima_degrau

        # f) Projeção mínima (r)
        # Calcula linha de passo (p) primeiro
        p = np.sqrt(profundidade_livre * profundidade_livre + altura_degrau * altura_degrau)
        r = profundidade_livre * altura_degrau / p
        resultados['projecao_ok'] = r >= 0

        # Fórmula de Blondel: 63 cm ≤ (2 × espelho) + piso ≤ 64 cm
        soma_blondel = (2 * altura_degrau) + profundidade_livre
        resultados['formula_blondel_ok'] = 630 <= soma_blondel <= 640

        # Calcula inclinação para referência
        inclinacao = np.degrees(np.arctan(altura_degrau/profundidade_livre))
        resultados['inclinacao_ok'] = inclinacao <= 39  # Inclinação máxima de 39°

        return resultados

    def avaliar_protecoes(self, altura_guarda_corpo, altura_rodape):
        """
        Avalia as dimensões do guarda-corpo e rodapé.
        """
        resultados = {}
        
        # Avalia guarda-corpo
        resultados['guarda_corpo_ok'] = altura_guarda_corpo >= self.altura_minima_guarda_corpo
        
        # Avalia rodapé
        resultados['rodape_ok'] = altura_rodape >= self.altura_minima_rodape
        
        return resultados

    def avaliar_plataforma(self, largura_plataforma, comprimento_plataforma, altura_plataforma):
        """
        Avalia as dimensões da plataforma de descanso.
        """
        resultados = {}
        
        # Avalia dimensões da plataforma
        resultados['largura_plataforma_ok'] = largura_plataforma >= self.largura_minima_plataforma
        resultados['comprimento_plataforma_ok'] = comprimento_plataforma >= self.comprimento_minimo_plataforma
        resultados['altura_plataforma_ok'] = altura_plataforma <= self.altura_maxima_entre_plataformas
        
        return resultados
