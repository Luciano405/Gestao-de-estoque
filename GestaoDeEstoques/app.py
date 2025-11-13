import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from dataset import prepare_dataset
from GS_otimizado import BranchAndBoundSolver

st.set_page_config(page_title="Gestão de Estoques - B&B", layout="wide")

st.title(" Otimização de Estoque — Branch & Bound")
st.markdown("Carregue um dataset (CSV) ou use o padrão. Ajuste parâmetros e execute o B&B com budgets.")


st.sidebar.header("Configuração de dados")
uploaded = st.sidebar.file_uploader("Faça upload do CSV (opcional)", type=["csv"])

sample_frac = st.sidebar.slider(
    "Porcentagem do dataset a ser usada:",
    min_value=0.01,
    max_value=1.0,
    value=0.05,
    step=0.01
)


st.sidebar.header("Budgets / Condições de parada")
time_limit_input = st.sidebar.number_input("Limite de tempo (s) - 0 = sem limite", min_value=0, value=30, step=5)
max_nodes_input = st.sidebar.number_input("Limite de nós expandidos - 0 = sem limite", min_value=0, value=10000, step=500)

time_limit = None if time_limit_input == 0 else float(time_limit_input)
max_nodes = None if max_nodes_input == 0 else int(max_nodes_input)


capacidade_total = st.sidebar.slider(
    "Capacidade total do estoque (unidade arbitrária):",
    min_value=50,
    max_value=2000,
    value=1000,
    step=25
)


if uploaded is not None:
    
    df_raw = pd.read_csv(uploaded)
    df = prepare_dataset(uploaded, sample_fraction=sample_frac)  
else:
    
    try:
        df = prepare_dataset("GS.csv", sample_fraction=sample_frac)
    except Exception as e:
        st.error(f"Erro ao preparar dataset padrão: {e}")
        st.stop()

# Tabelas: EDA / Execução / Resultados
tab1, tab2, tab3 = st.tabs(["EDA", "Execução (B&B)", "Resultados"])

# ---------- TABELA 1: EDA ----------
with tab1:
    st.header("Análise Exploratória (EDA)")
    st.write("Tamanho do dataset (após amostragem):", len(df))
    st.subheader("Estatísticas descritivas")
    st.dataframe(df[["Lucro Estimado", "Volume (m³)", "Giro de Estoque"]].describe().transpose())

    st.subheader("Gráficos")
    fig1, ax1 = plt.subplots()
    ax1.scatter(df["Volume (m³)"], df["Lucro Estimado"], alpha=0.6)
    ax1.set_xlabel("Volume (m³)")
    ax1.set_ylabel("Lucro Estimado")
    ax1.set_title("Lucro Estimado vs Volume")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.hist(df["Lucro Estimado"].clip(upper=df["Lucro Estimado"].quantile(0.99)), bins=30)
    ax2.set_title("Distribuição (Lucro Estimado) - truncado p/ outliers")
    st.pyplot(fig2)

# ---------- TABELA 2: Execução (B&B) ----------
with tab2:
    st.header("Execução do Branch & Bound")
    st.write("Parâmetros:")
    st.write(f"- Capacidade: {capacidade_total}")
    st.write(f"- Time limit: {time_limit if time_limit is not None else 'sem limite'}")
    st.write(f"- Max nodes: {max_nodes if max_nodes is not None else 'sem limite'}")

    run_button = st.button("Executar B&B")

    if run_button:
        with st.spinner("Executando Branch & Bound..."):
            solver = BranchAndBoundSolver(df, capacity=capacidade_total, time_limit=time_limit, max_nodes=max_nodes)
            best_value, best_x, metrics = solver.solve()

        st.success("Execução concluída")
        st.metric("Lucro Ótimo (B&B)", f"R$ {best_value:,.2f}")
        st.metric("Tempo (s)", f"{metrics['Tempo Total (s)']:.4f}")
        st.metric("Nós Expandidos", metrics["Nós Expandidos"])
        st.metric("Nós Podados", metrics["Nós Podados"])
        st.metric("Soluções Viáveis", metrics["Soluções Viáveis"])
        st.write(f"Profundidade Máxima: {metrics['Profundidade Máxima']}")

       
        npl = metrics.get("Nodes per Level", {})
        if npl:
            st.subheader("Nós por nível (evidência de poda)")
            npl_df = pd.DataFrame(list(npl.items()), columns=["Level", "Nodes"])
            fig3, ax3 = plt.subplots()
            ax3.bar(npl_df["Level"].astype(str), npl_df["Nodes"])
            ax3.set_xlabel("Nível")
            ax3.set_ylabel("Nós expandidos")
            st.pyplot(fig3)

        
        selected_idx = [i for i, v in enumerate(best_x) if v == 1]
        if selected_idx:
            selected_df = df.iloc[selected_idx].reset_index(drop=True)
        else:
            selected_df = pd.DataFrame(columns=df.columns)

        
        st.session_state["selected_df"] = selected_df
        st.session_state["best_value"] = best_value

        df_local = df.copy()
        df_local["ratio"] = df_local["Lucro Estimado"] / (df_local["Volume (m³)"] + 1e-9)
        greedy_df = df_local.sort_values(by="ratio", ascending=False)
        vol_acc = 0.0
        greedy_sel = []
        for _, row in greedy_df.iterrows():
            if vol_acc + row["Volume (m³)"] <= capacidade_total:
                greedy_sel.append(row)
                vol_acc += row["Volume (m³)"]
        greedy_value = sum([r["Lucro Estimado"] for r in greedy_sel])

        st.write("### Comparação com Heurística Gulosa")
        st.metric("Lucro Guloso", f"R$ {greedy_value:,.2f}")
        diff = best_value - greedy_value
        diff_pct = (diff / greedy_value * 100) if greedy_value != 0 else 0.0
        st.metric("Diferença (B&B - Gulosa)", f"R$ {diff:,.2f} ({diff_pct:.2f}%)")

# ---------- TABELA 3: RESULTADOS ----------
with tab3:
    st.header("Resultados")
    sel = st.session_state.get("selected_df", pd.DataFrame())
    best_value = st.session_state.get("best_value", None)

    if not sel.empty:
        st.subheader("Produtos selecionados (B&B)")
        st.dataframe(sel[["Product ID", "Category", "Lucro Estimado", "Volume (m³)"]].reset_index(drop=True))
        st.metric("Lucro Total (B&B)", f"R$ {best_value:,.2f}")
        st.metric("Capacidade usada", f"{sel['Volume (m³)'].sum():.2f} (unidades)")

        st.subheader("Resumo por Categoria")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(sel.groupby("Category")["Lucro Estimado"].sum())
        with col2:
            st.bar_chart(sel.groupby("Category")["Volume (m³)"].sum())

        st.download_button("Exportar seleção (CSV)", sel.to_csv(index=False).encode('utf-8'), "selection.csv", "text/csv")
    else:
        st.info("Execute o B&B na aba 'Execução (B&B)' para gerar uma seleção.")
