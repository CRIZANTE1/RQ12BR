import numpy as np
import os
import json
from datetime import datetime
import uuid

class CalculadoraEscada:
    """Classe para realizar cálculos relacionados a escadas industriais"""
    
    def __init__(self):
        """Inicializa a calculadora com valores padrão"""
        # Valores padrão conforme normas
        self.altura_minima_guarda_corpo = 1100  # mm
        self.altura_minima_rodape = 200  # mm
        self.altura_maxima_degrau = 250  # mm
        self.profundidade_minima_degrau = 250  # mm
        self.largura_minima = 800 # mm
        self.blondel_min = 630  # mm
        self.blondel_max = 640  # mm
        self.inclinacao_maxima = 39  # graus
        self.altura_maxima_sem_plataforma = 3000  # mm
        
    def calcular_num_degraus(self, altura_total, altura_degrau):
        """Calcula o número de degraus necessários"""
        return int(np.ceil(altura_total / altura_degrau))
    
    def calcular_inclinacao(self, altura_degrau, profundidade_degrau):
        """Calcula a inclinação da escada em graus"""
        return np.degrees(np.arctan(altura_degrau / profundidade_degrau))
    
    def calcular_blondel(self, altura_degrau, profundidade_degrau):
        """Calcula o valor da fórmula de Blondel (2h + p)"""
        return (2 * altura_degrau) + profundidade_degrau
    
    def calcular_num_plataformas(self, altura_total):
        """Calcula o número de plataformas necessárias"""
        if altura_total <= self.altura_maxima_sem_plataforma:
            return 0
        return int(np.ceil(altura_total / self.altura_maxima_sem_plataforma)) - 1
    
    def avaliar_escada(self, altura_total, altura_degrau, profundidade_degrau, 
                      largura, tem_saliencias=False, altura_guarda_corpo=1100, 
                      altura_rodape=200):
        """Avalia a conformidade da escada com as normas"""
        # Calcular valores derivados
        inclinacao = self.calcular_inclinacao(altura_degrau, profundidade_degrau)
        blondel = self.calcular_blondel(altura_degrau, profundidade_degrau)
        
        # Avaliar conformidade
        resultados = {
            'altura_degrau_ok': altura_degrau <= self.altura_maxima_degrau,
            'profundidade_ok': profundidade_degrau >= self.profundidade_minima_degrau,
            'profundidade_confortavel': 280 <= profundidade_degrau <= 320,
            'largura_ok': largura >= self.largura_minima,
            'formula_blondel_ok': self.blondel_min <= blondel <= self.blondel_max,
            'inclinacao_ok': inclinacao <= self.inclinacao_maxima,
            'saliencias_ok': not tem_saliencias
        }
        
        return resultados
    
    def avaliar_protecoes(self, altura_guarda_corpo, altura_rodape):
        """Avalia a conformidade das proteções (guarda-corpo e rodapé)"""
        return {
            'guarda_corpo_ok': altura_guarda_corpo >= self.altura_minima_guarda_corpo,
            'rodape_ok': altura_rodape >= self.altura_minima_rodape
        }
    
    def avaliar_plataforma(self, altura_plataforma, largura_plataforma, 
                          comprimento_plataforma, altura_total):
        """Avalia a conformidade da plataforma"""
        # Verificar se a altura da plataforma é adequada
        # Uma plataforma deve estar a cada 3000mm ou menos
        plataformas_necessarias = self.calcular_num_plataformas(altura_total)
        
        # Se não precisar de plataforma, qualquer altura é ok
        if plataformas_necessarias == 0:
            altura_plataforma_ok = True
        else:
            # Verificar se a altura da plataforma está em um múltiplo de 3000mm
            # com uma tolerância de ±300mm
            tolerancia = 300  # mm
            alturas_ideais = [i * self.altura_maxima_sem_plataforma for i in range(1, plataformas_necessarias + 1)]
            altura_plataforma_ok = any(abs(altura_plataforma - h) <= tolerancia for h in alturas_ideais)
        
        return {
            'altura_plataforma_ok': altura_plataforma_ok,
            'largura_plataforma_ok': largura_plataforma >= 600,
            'comprimento_plataforma_ok': comprimento_plataforma >= 600
        }
