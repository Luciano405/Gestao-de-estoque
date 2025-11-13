# Otimização de Estoque — Branch & Bound

Projeto para disciplina de Pesquisa Operacional — implementação do Branch & Bound aplicado à seleção de itens para estoque usando dataset publico do Kaggle.

# 1. Dataset
- Nome: Retail Store Inventory Forecasting Dataset (Kaggle)
- Link: (https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset?resource=download)
- Colunas usadas: Product ID, Category, Inventory Level, Units Sold, Demand Forecast, Price

# 2. Estrutura do repositório
- `dataset.py` — prepara e amostra o CSV.
- `GS_otimizado.py` — implementação do Branch & Bound com budgets.
- `app.py` — interface Streamlit (EDA, execução e resultados).
- `requirements.txt` — dependências.

# 3. Como rodar
1. Instalar dependências:
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py

