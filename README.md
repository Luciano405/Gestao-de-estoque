# Otimização de Estoque — Branch & Bound

Projeto da disciplina de **Pesquisa Operacional**, implementando o algoritmo **Branch & Bound (B&B)** para otimização da seleção de produtos em estoque. A aplicação inclui uma interface interativa via **Streamlit**, análise exploratória, heurística gulosa e controle de budgets.

---

## 1. Dataset

**Fonte:** Retail Store Inventory Forecasting Dataset (Kaggle)
Link: [https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)

**Colunas utilizadas:**

* `Product ID` 
* `Category` 
* `Inventory Level` 
* `Units Sold` 
* `Demand Forecast` 
* `Price` 

Essas variáveis são transformadas pelos scripts para gerar:

* `Lucro Estimado` (função objetivo)
* `Volume (m³)` (restrição / peso)
* `Giro de Estoque` (indicador para EDA)

---

##  2. Estrutura do projeto

```
 GESTAODEESTOQUES
 ├── app.py                # Interface Streamlit (EDA, execução e gráficos)
 ├── dataset.py            # Preparação, amostragem e engenharia de atributos
 ├── GS_otimizado.py       # Implementação completa do Branch & Bound
 ├── GS.csv                # Dataset base 
 ├── requirements.txt      # Dependências do projeto
 └── README.md             # Documentação
```

---

## 3. Funcionamento do sistema

###  3.1 `dataset.py` — Processamento do CSV

Funções principais:

* Lê o CSV original.
* Faz amostragem configurável.
* Agrupa por produto para evitar duplicatas.
* Calcula:

  * `Lucro Estimado = Price * 0.30 * Demand Forecast`
  * `Volume (m³) = Inventory Level` (normalizado 0–100)
  * `Giro de Estoque = Units Sold / Inventory Level`

Retorna um DataFrame final com:

* `Product ID`, `Category`, `Lucro Estimado`, `Volume (m³)`, `Giro de Estoque`.

---

### 3.2 `GS_otimizado.py` — Branch & Bound Completo

Implementa o B&B com:

* **Ordenação por razão valor/pes.**
* **Cálculo de bound fracionário**.
* **Heurística gulosa inicial**.
* **Priority Queue**.
* **Budgets**:

  * limite de tempo (`time_limit`)
  * limite de nós expandidos (`max_nodes`)
* **Métricas coletadas**:

  * Tempo total
  * Nós expandidos e podados
  * Soluções viáveis
  * Profundidade máxima
  * Nós por nível

Funções principais:

* `solve()` — executa o Branch & Bound completo
* `_calculate_bound()` — calcula o upper bound fracionário
* `_greedy_primal()` — gera solução inicial

Retorno:

```
best_value, best_x, metrics
```

---

### 3.3 `app.py` — Interface via Streamlit

Dividida em **3 abas**:

#### **1. EDA (Análise Exploratória)**

* Tamanho do dataset
* Estatísticas descritivas
* Gráficos:

  * Dispersão (Volume vs. Lucro)
  * Distribuição do lucro (com truncamento de outliers)

#### **2. Execução (B&B)**

Parâmetros configuráveis pelo usuário:

* Capacidade do estoque
* Limite de tempo
* Limite de nós expandidos
* Tamanho da amostra do dataset

Ao rodar:

* Mostra métricas completas do B&B
* Gráfico de nós expandidos por nível
* Compara com **Heurística Gulosa**:

  * Lucro guloso
  * Diferença (% e valor)

#### **3. Resultados**

* Tabela de produtos escolhidos
* Resumo por categoria com gráficos
* Botão para exportar CSV

---

## 4. Como executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Rodar a aplicação Streamlit

```bash
streamlit run app.py
```

---

## 5. Heurística Gulosa (Comparação)

A heurística gulosa seleciona itens com maior razão:

```
Lucro Estimado / Volume
```

Isso gera:

* solução rápida
* boa aproximação
* usada como **ponto inicial** do B&B

No relatório final, o Streamlit mostra:

* Lucro guloso
* Lucro ótimo (B&B)
* Diferença percentual

---

## 6. Resultados e Métricas

O Branch & Bound retorna:

* Lucro ótimo
* Vetor de decisão
* Capacidade usada
* Nós expandidos / podados
* Profundidade máxima
* Distribuição dos nós por nível

