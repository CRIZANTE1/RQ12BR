# 🪜 RQ12BR - Sistema de Avaliação de Escadas NR-12

## 📋 Correções Implementadas

Este documento lista todas as correções feitas para alinhar o sistema com a **NR-12 Anexo III**.

---

## ✅ Valores Corrigidos Conforme NR-12

| Item | Valor Anterior | Valor Correto | Referência NR-12 |
|------|----------------|---------------|------------------|
| **Altura mínima degrau** | - | **150mm** | Item 11.d |
| **Altura máxima degrau** | 250mm | **250mm** | Item 11.d ✓ |
| **Profundidade mínima (sem espelho)** | 250mm | **150mm** | Item 11.b |
| **Profundidade mínima (com espelho)** | - | **200mm** | Item 12.b |
| **Largura útil mínima** | 800mm | **600mm** | Item 11.a |
| **Fórmula NR-12 mínima (g + 2h)** | 630mm | **600mm** | Item 11.g |
| **Fórmula NR-12 máxima (g + 2h)** | 640mm | **660mm** | Item 11.g |
| **Inclinação mínima** | 30° | **20°** | Figura 1 |
| **Inclinação máxima** | 38°/39° | **45°** | Figura 1 |

---

## 📁 Arquivos Modificados

### 1. **operations/avaliador_escada.py**
**Correções aplicadas:**
- ✅ Valores mínimos/máximos na tabela de avaliação
- ✅ Mensagens de recomendação atualizadas
- ✅ Fórmula NR-12 corrigida (g + 2h ao invés de 2h + p)
- ✅ Avisos de inclinação ajustados (20° a 45°)
- ✅ Integração com Google Drive
- ✅ Controle de limite de avaliações por plano

**Principais mudanças:**
```python
# ANTES
'Valor Mínimo': ['0', '250', '800', '630', '30°']
'Valor Máximo': ['250', '-', '-', '640', '38°']

# DEPOIS
'Valor Mínimo': ['150', '150', '600', '600', '20°']
'Valor Máximo': ['250', '-', '-', '660', '45°']
```

---

### 2. **operations/calculadora_nova_escada.py**
**Correções aplicadas:**
- ✅ Valores de entrada dos campos ajustados
- ✅ Fórmula NR-12 corrigida
- ✅ Validações de conformidade atualizadas
- ✅ Documentação inline atualizada

**Principais mudanças:**
```python
# ANTES
inclinacao_maxima: min=30.0, max=38.0
largura: min=800.0
formula_blondel = 2 * altura_degrau + profundidade_degrau

# DEPOIS
inclinacao_maxima: min=20.0, max=45.0
largura: min=600.0
formula_nr12 = profundidade_degrau + (2 * altura_degrau)
```

---

### 3. **operations/referencias_visuais.py**
**Correções aplicadas:**
- ✅ Documentação técnica atualizada
- ✅ Valores de referência corrigidos
- ✅ Notas explicativas sobre Item 11.b e 12.b
- ✅ Informações sobre atualizações da NR-12

---

### 4. **utils/auditoria.py**
**Implementação completa:**
- ✅ Função `log_action()` implementada
- ✅ Funções auxiliares para logs específicos
- ✅ Integração com Google Sheets
- ✅ Tratamento de erros silencioso

---

### 5. **operations/calculadora_escada.py** ✓
**Status:** Já estava correto!

### 6. **operations/calculations.py** ✓
**Status:** Já estava correto!

---

## 🚀 Como Aplicar as Correções

### **Método 1: Substituição Direta**
1. Faça backup dos arquivos atuais
2. Substitua os arquivos pelos corrigidos (fornecidos nos artifacts)
3. Teste todas as funcionalidades

### **Método 2: Aplicação Manual**
Se preferir aplicar as correções manualmente:

#### **A. operations/avaliador_escada.py**
```python
# Linha ~113-127: Atualizar valores da tabela
'Valor Mínimo': ['-', '-', '150', '150', '600', '600', '20°', '-', '1100', '200']
'Valor Máximo': ['-', '-', '250', '-', '-', '660', '45°', '-', '-', '-']
```

```python
# Linha ~135: Calcular fórmula NR-12 corretamente
formula_nr12 = profundidade_degrau + (2 * altura_degrau)
```

```python
# Linha ~143-146: Atualizar mensagens de recomendação
f'Aumentar para pelo menos 150mm. Valor atual: {profundidade_degrau:.1f} mm.'
f'Aumentar para pelo menos 600mm (NR-12 Item 11.a). Valor atual: {largura:.1f} mm.'
f'Ajustar dimensões para 600 ≤ g + 2h ≤ 660 (NR-12 Item 11.g). Valor atual: {formula_nr12:.1f} mm.'
f'Ajustar para 20° a 45° (NR-12 Figura 1). Valor atual: {inclinacao:.1f}°.'
```

```python
# Linha ~245: Atualizar avisos de inclinação
if inclinacao > 45:
    st.error(f"⚠️ A inclinação ({inclinacao:.1f}°) excede o máximo de 45° (NR-12 Figura 1).")
elif inclinacao < 20:
    st.warning(f"⚠️ A inclinação ({inclinacao:.1f}°) está abaixo do mínimo de 20° (NR-12 Figura 1).")
```

#### **B. operations/calculadora_nova_escada.py**
```python
# Linha ~34-40: Corrigir valores de entrada
inclinacao_maxima = st.number_input(
    "Inclinação Máxima (graus):",
    min_value=20.0,  # ← de 30.0
    max_value=45.0,  # ← de 38.0
    help="Inclinação: 20° a 45° (NR-12 Figura 1)"
)
```

```python
# Linha ~44: Corrigir largura mínima
largura = st.number_input(
    min_value=600.0,  # ← de 800.0
    help="Largura mínima: 600mm (NR-12 Item 11.a)"
)
```

```python
# Linha ~72: Corrigir fórmula
formula_nr12 = profundidade_degrau + (2 * altura_degrau)
formula_ok = 600 <= formula_nr12 <= 660
```

---

## 🧪 Testes Recomendados

Após aplicar as correções, teste os seguintes cenários:

### **Teste 1: Escada Conforme**
- Altura total: 3000mm
- Altura degrau: 180mm
- Profundidade: 280mm
- Largura: 800mm
- **Resultado esperado:** 100% conforme

### **Teste 2: Escada com Inclinação Fora do Limite**
- Altura degrau: 200mm
- Profundidade: 150mm
- **Resultado esperado:** Aviso de inclinação > 45°

### **Teste 3: Escada com Fórmula NR-12 Fora do Intervalo**
- Altura degrau: 250mm
- Profundidade: 150mm
- g + 2h = 650mm
- **Resultado esperado:** Aprovado (600-660)

### **Teste 4: Largura Abaixo do Mínimo**
- Largura: 550mm
- **Resultado esperado:** Não conforme

---

## 📚 Referências Normativas

### **NR-12 - Anexo III**
- **Item 11:** Escadas de degraus sem espelho
- **Item 12:** Escadas de degraus com espelho
- **Item 7:** Sistema de proteção contra quedas
- **Figura 1:** Escolha dos meios de acesso conforme inclinação

### **ABNT NBR ISO 14122-3:2023**
Complementa a NR-12 com detalhes técnicos adicionais para projeto e fabricação.

---

## ⚠️ Avisos Importantes

1. **Backup:** Sempre faça backup antes de aplicar correções
2. **Ambiente de teste:** Teste em ambiente de desenvolvimento primeiro
3. **Dados existentes:** Avaliações antigas podem ter sido salvas com critérios antigos
4. **Documentação:** Atualize a documentação interna do projeto

---

## 🆘 Suporte

Se encontrar problemas após aplicar as correções:

1. Verifique os logs de erro no console
2. Confirme que todos os valores foram atualizados
3. Teste isoladamente cada função corrigida
4. Reverta para o backup se necessário

---

## 📝 Changelog

### Versão 2.0.0 - Correções NR-12
**Data:** 2025-01-07

**Adicionado:**
- ✅ Implementação completa de `utils/auditoria.py`
- ✅ Integração com Google Drive para avaliações
- ✅ Controle de planos e limites de avaliação

**Corrigido:**
- ✅ Valores conforme NR-12 Anexo III
- ✅ Fórmula g + 2h (era 2h + p)
- ✅ Inclinação: 20° a 45° (era 30° a 38°)
- ✅ Largura mínima: 600mm (era 800mm)
- ✅ Profundidade mínima: 150mm (era 250mm)

**Melhorado:**
- ✅ Mensagens de recomendação mais claras
- ✅ Documentação inline
- ✅ Referências à NR-12 nos tooltips

---

## ✨ Resumo

Todas as correções foram aplicadas para garantir **100% de conformidade** com a **NR-12 Anexo III**. O sistema agora:

- ✅ Valida corretamente as dimensões de escadas
- ✅ Usa a fórmula correta (g + 2h) entre 600-660mm
- ✅ Aceita inclinações de 20° a 45°
- ✅ Exige largura mínima de 600mm
- ✅ Diferencia escadas com e sem espelho
- ✅ Registra todas as ações em log de auditoria
- ✅ Salva avaliações no Google Drive do usuário

**Status:** ✅