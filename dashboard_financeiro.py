import streamlit as st
import pandas as pd
import plotly.express as px
import os

CSV_FILE = "dados_mensais.csv"

NOMES_MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def init_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=["ano", "mes", "faturamento", "vendas", "conversao", "estoque"])
        df.to_csv(CSV_FILE, index=False)
    return df

def salvar_e_recarregar(df):
    df.to_csv(CSV_FILE, index=False)
    return pd.read_csv(CSV_FILE)

def main():
    st.set_page_config(page_title="Dashboard Galvanosul", layout="wide")
    st.title("Dashboard Galvanosul")

    # SEM CACHE! Sempre leia os dados do arquivo no início de cada execução
    df = init_data()

    # --- FILTRO ---
    st.sidebar.header("Filtro de Período")
    anos = sorted(df["ano"].unique(), reverse=True)
    meses = list(range(1, 13))

    # Caso não tenha nenhum dado, crie filtros default
    if len(anos) == 0:
        anos = [2025]
    ano_filtro = st.sidebar.selectbox("Selecione o ano:", anos)
    mes_filtro = st.sidebar.selectbox("Selecione o mês:", meses, format_func=lambda m: NOMES_MESES[m])

    filtrado = df[(df["ano"] == ano_filtro) & (df["mes"] == mes_filtro)]

    # --- FORMULÁRIO DE DADOS ---
    st.header("Cadastro ou Edição de Dados")
    with st.form("form_dados", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            faturamento = st.number_input("Faturamento (R$)", value=float(filtrado["faturamento"].values[0]) if not filtrado.empty else 0.0, format="%.2f")
        with col2:
            vendas = st.number_input("Vendas (R$)", value=float(filtrado["vendas"].values[0]) if not filtrado.empty else 0.0, format="%.2f")
        with col3:
            conversao = st.number_input("Conversão (%)", min_value=0.0, max_value=100.0, value=float(filtrado["conversao"].values[0]) if not filtrado.empty else 0.0, format="%.2f")
        with col4:
            estoque = st.number_input("Estoque (R$)", value=float(filtrado["estoque"].values[0]) if not filtrado.empty else 0.0, format="%.2f")

        salvar = st.form_submit_button("Salvar Dados")

    # --- SALVAR E RECARRREGAR OS DADOS ---
    if salvar:
        novo_dado = {
            "ano": ano_filtro,
            "mes": mes_filtro,
            "faturamento": faturamento,
            "vendas": vendas,
            "conversao": conversao,
            "estoque": estoque
        }
        if not filtrado.empty:
            idx = filtrado.index[0]
            df.loc[idx] = novo_dado
            st.success("Dados ATUALIZADOS com sucesso!")
        else:
            df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            st.success("NOVO dado adicionado com sucesso!")
        df = salvar_e_recarregar(df)  # <- Recarrrega sempre!
        # Atualize filtros para o mês/ano recém-editados



    # Sempre use o DataFrame atualizado
    df["mes_nome"] = df["mes"].map(NOMES_MESES)
    df.sort_values(["ano", "mes"], inplace=True)
    df_filtrado = df[df["ano"] == ano_filtro]

    # --- KPIs ---
    st.header(f"Indicadores de {NOMES_MESES[mes_filtro]} / {ano_filtro}")
    kpi = df[(df["ano"] == ano_filtro) & (df["mes"] == mes_filtro)]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Faturamento", f"R$ {kpi['faturamento'].values[0]:,.2f}" if not kpi.empty else "R$ 0,00")
    with col2:
        st.metric("Vendas", f"R$ {kpi['vendas'].values[0]:,.2f}" if not kpi.empty else "R$ 0,00")
    with col3:
        st.metric("Conversão", f"{kpi['conversao'].values[0]:.2f}%" if not kpi.empty else "0,00%")
    with col4:
        st.metric("Estoque (R$)", f"R$ {kpi['estoque'].values[0]:,.2f}" if not kpi.empty else "R$ 0,00")

    # --- GRÁFICOS ---
    st.header(f"Gráficos de Desempenho - {ano_filtro}")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(df_filtrado, x="mes_nome", y="faturamento", text_auto='.2s',
                      title="Faturamento Mensal", color_discrete_sequence=['#0077b6'])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.line(df_filtrado, x="mes_nome", y="conversao", markers=True,
                       title="Taxa de Conversão Mensal", color_discrete_sequence=['#ff6b6b'])
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.area(df_filtrado, x="mes_nome", y="estoque",
                   title="Evolução do Estoque (R$)", color_discrete_sequence=['#52b788'])
    st.plotly_chart(fig3, use_container_width=True)

    # --- TABELA DE DADOS ---
    st.header("Tabela de Dados")
    st.dataframe(df_filtrado.drop(columns=["mes_nome"]))

if __name__ == "__main__":
    main()

