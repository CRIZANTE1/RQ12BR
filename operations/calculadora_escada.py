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
        self.altura_minima_degrau = 150  # mm - NOVO
        self.altura_maxima_degrau = 250  # mm
        self.profundidade_minima_degrau_sem_espelho = 150  # mm - Item 11.b
        self.profundidade_minima_degrau_com_espelho = 200  # mm - Item 12.b
        self.largura_minima = 600  # mm - Item 11.a (não 800!)
        self.formula_nr12_min = 600  # mm - Item 11.g (não 630!)
        self.formula_nr12_max = 660  # mm - Item 11.g (não 640!)
        self.inclinacao_minima = 20  # graus - NOVO
        self.inclinacao_maxima = 45  # graus - Figura 1 (não 38 ou 39!)
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
            'altura_degrau_ok': 150 <= altura_degrau <= 250,  # CORRIGIDO
            'profundidade_ok': profundidade_degrau >= 150,  # CORRIGIDO para sem espelho
            'profundidade_confortavel': 280 <= profundidade_degrau <= 320,
            'largura_ok': largura >= 600,  # CORRIGIDO (Item 11.a)
            'formula_blondel_ok': 600 <= blondel <= 660,  # CORRIGIDO
            'inclinacao_ok': 20 <= inclinacao <= 45,  # CORRIGIDO
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


class GerenciadorHistorico:
    """Classe para gerenciar o histórico de avaliações"""
    
    def __init__(self):
        """Inicializa o gerenciador de histórico"""
        self.criar_diretorios()
    
    def criar_diretorios(self):
        """Cria os diretórios necessários para armazenar dados e imagens"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("images", exist_ok=True)
    
    def salvar_historico_json(self, historico_avaliacoes):
        """Salva o histórico de avaliações em um arquivo JSON"""
        # Verificar se o diretório existe
        self.criar_diretorios()
        
        # Converter o histórico para um formato serializável
        historico_serializavel = []
        
        for avaliacao in historico_avaliacoes:
            # Criar cópia da avaliação sem as imagens binárias
            aval_serializavel = avaliacao.copy()
            historico_serializavel.append(aval_serializavel)
        
        # Salvar em arquivo JSON
        with open("data/historico.json", "w", encoding="utf-8") as f:
            json.dump(historico_serializavel, f, ensure_ascii=False, indent=4)
        
        print(f"Histórico salvo em data/historico.json com {len(historico_serializavel)} avaliações")
    
    def carregar_historico_json(self):
        """Carrega o histórico de avaliações do arquivo JSON"""
        if os.path.exists("data/historico.json"):
            try:
                with open("data/historico.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar histórico: {e}")
                return []
        return []
    
    def excluir_avaliacao(self, historico_avaliacoes, idx):
        """Exclui uma avaliação do histórico"""
        avaliacao = historico_avaliacoes.pop(idx)
        
        # Remover arquivos associados
        grafico_path = avaliacao.get('grafico_path')
        foto_path = avaliacao.get('foto_path')
        
        if grafico_path and os.path.exists(grafico_path):
            os.remove(grafico_path)
        if foto_path and os.path.exists(foto_path):
            os.remove(foto_path)
        
        # Atualizar o arquivo JSON
        self.salvar_historico_json(historico_avaliacoes)
        
        return historico_avaliacoes
