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
2. Acesse `http://localhost:5173/` no seu navegador
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
# Acesse: http://localhost:5173
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

## 📊 Performance & Testes

Sistema validado com bateria completa de testes demonstrando **aprendizado progressivo** e **escalabilidade**.

### Resultados dos Testes

| Teste | Documentos | Acurácia | Tempo Médio | Status |
|-------|------------|----------|-------------|--------|
| Básico | 1 | 100% (7/7) | 16.7s | ✅ |
| API | 1 | 100% (7/7) | 15.9s | ✅ |
| Aprendizado | 5 | 100% (35/35) | 8.0s | ✅ |

### Aprendizado Progressivo 📈

O sistema **melhora com o tempo** através de few-shot learning:

```
Doc 1 (baseline):    ############################################################ 16.7s
Doc 2 (few-shot):    ##################### 6.0s (64% mais rápido)
Doc 3 (few-shot):    ##################### 5.9s
Doc 4 (few-shot):    #################### 5.8s
Doc 5 (few-shot):    #################### 5.7s
```

**Economia em 100 documentos:**
- Sem otimização: 27.8 min
- Com few-shot: 9.9 min (**2.8x mais rápido**)
- Com cache (20%): 8.0 min (**3.5x mais rápido**)

### Executar Testes

```bash
python test_extractor.py    # Teste básico (~20s)
python test_api.py          # Teste da API (~20s)
python test_learning.py     # Aprendizado progressivo (~45s)
python visualize_learning.py # Visualização (<1s)
```

Ver documentação completa: [README_TESTES.md](README_TESTES.md)

### Tech Stack

- **Model:** GPT-5-mini (gpt-5-mini-2025-08-07)
- **AI Coding:** Claude Code
- **Cache:** Dual-layer com embeddings semânticos
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **PDF Parsing:** PyMuPDF (fitz)
- **Backend:** Flask + CORS
- **Frontend:** React + TypeScript + Vite


---

Desenvolvido para o **Enter AI Fellowship Challenge** 🚀

Ian Klein
lots of energy and desire to be part of it.
