# Desafio Structure data from PDF - Enter AI Fellowship - Ian Klein

> Sistema inteligente de extração de dados estruturados de PDFs usando IA com interface web moderna e cache semântico

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4--mini-412991.svg)](https://openai.com/)

---

## 🎯 Como Usar

Este projeto é uma aplicação **full-stack completa** com backend Flask e frontend React. O Flask serve tanto a API quanto a interface web.

**Para rodar localmente:**
1. Execute os comandos do TL;DR abaixo
2. Acesse `http://localhost:5000` no seu navegador
3. O frontend estará disponível automaticamente (já compilado em `frontend/dist/`)

O servidor Flask entrega a interface React e processa as requisições de extração de PDF. Sem necessidade de rodar frontend separadamente!

---

## ⚡ TL;DR

```bash
# 1. Setup
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt && pip install httpx==0.27.0 httpcore==1.0.5

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env e adicione sua OPENAI_API_KEY

# 3. Build Frontend
cd frontend
cp .env.example .env  # Configurar URL da API (já vem com localhost:5000)
npm install && npm run build
cd ..

# 4. Run
python app.py
# Acesse: http://localhost:5000
```

### 🔑 Variáveis de Ambiente Necessárias

**Backend (`.env` na raiz):**
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Frontend (`frontend/.env`):**
```bash
VITE_API_URL=http://localhost:5000
```

**O que faz:** Extrai dados estruturados de PDFs usando GPT-5-mini com cache inteligente. Interface web moderna com drag & drop, SSE real-time e feedback completo de custos/tokens.

---

## 📊 Optimization Journey - Challenge Results

Durante o desenvolvimento, testamos múltiplas estratégias de otimização para atingir os requisitos do desafio: **<10s por documento** e **100% de acurácia**.

### Resultados Comparativos

| Fase      | Tempo Médio | Acurácia | Campos Corretos | Técnica Principal                        | Status |
|-----------|-------------|----------|-----------------|------------------------------------------|--------|
| **FASE 1**    | 13.89s      | 94.59%   | 35/37           | Prompt optimization (40% token reduction) | ✅ Estável |
| **FASE 2A**   | 20.78s      | 83.78%   | 31/37           | Pattern matching agressivo               | ❌ Falhou |
| **FASE 2B**   | 13.89s      | 94.59%   | 35/37           | Date hints + conservative extraction     | ✅ **MELHOR** |
| **FASE 3**    | 16.25s      | 94.59%   | 35/37           | Template matching via fingerprinting     | ❌ Não detectou similaridade |

### O Que Funcionou ✅

1. **Prompt Optimization (FASE 1)**
   - Reduziu system prompt de ~400 para ~250 tokens (40% redução)
   - Manteve instruções críticas: regras de formatação, dicas estruturais, exemplos compactos
   - Acurácia mantida em 94.59% com tempo de 13.89s

2. **Few-Shot Learning com Cache Semântico**
   - Documentos 2+ com exemplos cached: média de ~10.16s
   - Primeiro documento sem exemplos: ~24s
   - Sistema aprende com extrações anteriores usando embeddings (sentence-transformers)

3. **Date Extraction Hints (FASE 2B)**
   - Extraiu TODAS as datas do documento via regex
   - Passou lista ao LLM: "Há 2 datas no documento: 05/09/2025, 12/10/2025"
   - **Resultado:** Corrigiu erro crítico de `data_verncimento` (antes extraía data errada)

4. **PyMuPDF Local Extraction**
   - Extração de texto local (custo ZERO)
   - Performance 35x superior vs API-based extraction
   - Base sólida para pattern matching conservador

### O Que Não Funcionou ❌

1. **Pattern Matching Agressivo (FASE 2A)**
   - Tentativa: Extrair campos estruturados (CPF, CEP, telefone, números) via regex antes do LLM
   - **Problema:** Confundiu campos similares (CEP de 8 dígitos como telefone, números aleatórios como parcelas)
   - **Impacto:** Acurácia caiu de 94.59% → 83.78%, tempo aumentou para 20.78s
   - **Decisão:** Rollback completo, manter apenas extração de datas múltiplas

2. **Template Matching via Fingerprinting (FASE 3)**
   - Tentativa: Detectar documentos similares (mesmo template OAB) e reusar resultado sem chamar LLM
   - **Problema:** Fingerprint baseado nos primeiros 500 caracteres incluía nome do titular, diferente em cada documento
   - **Impacto:** NENHUM template detectado entre 3 carteiras OAB idênticas, tempo aumentou para 16.25s
   - **Aprendizado:** Fingerprinting estrutural requer análise mais sofisticada (ignorar campos variáveis)

3. **Token Reduction Attempts**
   - Testamos reduzir `max_completion_tokens` de 1500 → 600
   - **Problema:** GPT-5-mini usa 800-1400 tokens para reasoning interno (não controlável)
   - **Impacto:** Respostas vazias com `finish_reason='length'`
   - **Decisão:** Manter 1500 tokens (recomendação do usuário)

### Limitações Técnicas Descobertas ⚠️

1. **GPT-5 Reasoning Tokens (Não Controlável)**
   - Modelo gasta 800-1400 tokens em reasoning interno antes de gerar resposta
   - Isso adiciona ~7-12s por requisição (tempo de inferência mínimo)
   - **Conclusão:** Difícil atingir <10s consistente no primeiro documento sem cache

2. **Variabilidade de Tempo**
   - Primeiro documento: 19-27s (sem exemplos cached)
   - Documentos seguintes: 10-16s (com few-shot learning)
   - Cache hit: <0.01s (extração instantânea)

3. **Campos Persistentemente Problemáticos**
   - `total_de_parcelas`: Valor "96" visível na imagem mas não extraído (null)
   - `produto`: Extrai "0 CONSIGNADO" ao invés de "CONSIGNADO"
   - Pattern matching falhou, LLM com texto completo também falhou

### Current Best Result 🏆

**FASE 2B** é atualmente a melhor versão:

```
✅ Acurácia: 94.59% (35/37 campos corretos)
✅ Tempo médio: 13.89s (documentos 2+ com cache: ~10.16s)
✅ Custo médio: $0.001739 USD (~R$ 0.0093 BRL)
✅ Cache funcional: Few-shot learning ativo
✅ 100% taxa de sucesso (6/6 documentos processados)
```

**Erros Restantes (2/37 campos):**
- `tela_sistema_1.pdf::produto`: Extraído "0 CONSIGNADO" (esperado: "CONSIGNADO")
- `tela_sistema_3.pdf::total_de_parcelas`: Extraído `null` (esperado: "96")

### Tech Stack Utilizado

- **Model:** GPT-5-mini (gpt-5-mini-2025-08-07)
- **Cache:** Dual-layer (.results_cache + cache/ + in-memory)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **PDF Parsing:** PyMuPDF (fitz)
- **Pattern Matching:** Regex conservador (apenas datas múltiplas)
- **Validation:** Framework campo-a-campo (test_accuracy.py)

### Próximos Passos

Para atingir 100% de acurácia e <10s consistente:
1. Investigar por que `total_de_parcelas` não é detectado (visível na imagem)
2. Corrigir extração de `produto` (remover "0 extra)
3. Explorar vision models para casos edge (GPT-4-vision para PDFs com layout complexo)
4. Otimizar fingerprinting para template matching real (ignorar campos variáveis)

---

Desenvolvido para o **Enter AI Fellowship Challenge** 🚀

Ian Klein
lots of energy and desire to be part of it.
