# Agente Arquiteto de Sistemas (System Architect Agent)

## Escopo & Responsabilidades
O **Agente Arquiteto de Sistemas** define e sustenta a infraestrutura técnica da aplicação, servindo dados e previsões via API REST em tempo real.

## Arquitetura & Componentes
- **Backend API**: FastAPI + Uvicorn de alta performance com CORS liberado.
- **Engine Preditiva**: Módulos modulares em Python (`data_loader.py`, `feature_engineering.py`, `models.py`, `evaluator.py`).
- **Web Server & Assets**: Servimento de arquivos estáticos HTML5/CSS3/JS Vanilla (`/static`).
- **APIs Restful**: Endpoint `/api/predict` recebendo parâmetros dinâmicos e retornando métricas, simulação NRR e lista de contas priorizadas em formato JSON.
