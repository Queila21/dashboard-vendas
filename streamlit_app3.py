import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da página em modo "wide"
st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS para ajustar espaçamentos idêntico ao modelo
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    h1 { font-weight: 800 !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Carregar dados tratando o separador ';' 
@st.cache_data
def carregar_dados():
    # Lendo o arquivo local com separador correto
    df = pd.read_csv("vendas_dashboard.csv", sep=";")
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    return df

try:
    df = carregar_dados()
except Exception as e:
    st.error("Erro ao carregar os dados. Verifique se o arquivo 'vendas_dashboard.csv' contém as 100 linhas.")
    st.stop()

# 3. Cabeçalho Principal (Igual ao modelo)
st.title("📊 Dashboard de Vendas — APP3 (Dataset Fixo)")
st.caption("Base: vendas_dashboard.csv — upload e download desabilitados.")

# 4. Painel de Filtros em Grade (2 linhas x 4 colunas)
col_est, col_loj, col_ven, col_per = st.columns(4)
with col_est:
    estado_sel = st.selectbox("Estado", ["(Todos)"] + sorted(list(df["estado"].dropna().unique())))
with col_loj:
    loja_sel = st.selectbox("Loja", ["(Todos)"] + sorted(list(df["loja"].dropna().unique())))
with col_ven:
    vendedor_sel = st.selectbox("Vendedor", ["(Todos)"] + sorted(list(df["nome_vendedor"].dropna().unique())))
with col_per:
    data_min = df["data_venda"].min().to_pydatetime()
    data_max = df["data_venda"].max().to_pydatetime()
    periodo_sel = st.date_input("Período (Data da Venda)", [data_min, data_max])

col_mun, col_cat, col_cli, col_par = st.columns(4)
with col_mun:
    municipio_sel = st.selectbox("Município", ["(Todos)"] + sorted(list(df["municipio"].dropna().unique())))
with col_cat:
    categoria_sel = st.selectbox("Categoria", ["(Todos)"] + sorted(list(df["categoria_produto"].dropna().unique())))
with col_cli:
    cat_cliente_sel = st.selectbox("Categoria do Cliente", ["(Todos)"] + sorted(list(df["categoria_cliente"].dropna().unique())))
with col_par:
    venda_parc_sel = st.selectbox("Venda Parcelada", ["(Todos)"] + sorted(list(df["venda_parcelada"].dropna().unique())))

# 5. Filtragem dos Dados
df_filtrado = df.copy()

if estado_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sel]
if loja_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["loja"] == loja_sel]
if vendedor_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["nome_vendedor"] == vendedor_sel]
if municipio_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["municipio"] == municipio_sel]
if categoria_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["categoria_produto"] == categoria_sel]
if cat_cliente_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["categoria_cliente"] == cat_cliente_sel]
if venda_parc_sel != "(Todos)":
    df_filtrado = df_filtrado[df_filtrado["venda_parcelada"] == venda_parc_sel]
if isinstance(periodo_sel, list) or isinstance(periodo_sel, tuple):
    if len(periodo_sel) == 2:
        df_filtrado = df_filtrado[(df_filtrado["data_venda"] >= pd.to_datetime(periodo_sel[0])) & 
                                   (df_filtrado["data_venda"] <= pd.to_datetime(periodo_sel[1]))]

st.write("")
st.header("☑ KPIs")

# 6. Cálculos dos KPIs
total_faturamento = df_filtrado["preco_total"].sum()
total_vendas = len(df_filtrado)
ticket_medio = total_faturamento / total_vendas if total_vendas > 0 else 0.0

vendas_parceladas = len(df_filtrado[df_filtrado["venda_parcelada"].str.lower() == "sim"])
pct_parceladas = (vendas_parceladas / total_vendas) * 100 if total_vendas > 0 else 0.0

if not df_filtrado.empty:
    estado_lider = df_filtrado.groupby("estado")["preco_total"].sum().idxmax()
else:
    estado_lider = "-"

clientes_unicos = df_filtrado["nome_cliente"].nunique()
media_itens = df_filtrado["quantidade_vendida"].mean() if total_vendas > 0 else 0.0

def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Exibição dos KPIs em colunas (Casando com a Imagem 1)
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns([1.2, 0.8, 1.2, 1.1, 1.3, 1.5])
with kpi1:
    st.metric("Faturamento", formatar_br(total_faturamento))
with kpi2:
    st.metric("Nº de Vendas", f"{total_vendas}")
with kpi3:
    st.metric("Ticket Médio", formatar_br(ticket_medio))
with kpi4:
    st.metric("% Parceladas", f"{pct_parceladas:.2f}%")
with kpi5:
    st.metric("Estado Líder", estado_lider)
with kpi6:
    st.metric("Clientes Únicos / Itens/Venda", f"{clientes_unicos} / {media_itens:.2f}")

st.write("")
st.markdown("---")
st.header("🔷 Vendas por Cliente / Vendedor / Categoria / Loja")

# 7. Gráfico 1: Faturamento por Cliente
st.write("### Faturamento por Cliente")
df_cliente = df_filtrado.groupby("nome_cliente")["preco_total"].sum().reset_index().sort_values(by="preco_total", ascending=False)
fig_cliente = px.bar(df_cliente, x="nome_cliente", y="preco_total", color="nome_cliente",
                     labels={"nome_cliente": "Cliente", "preco_total": "Faturamento (R$)"},
                     color_discrete_sequence=px.colors.qualitative.Pastel)
fig_cliente.update_layout(showlegend=True, legend_title_text="Cliente")
st.plotly_chart(fig_cliente, use_container_width=True)

# 8. Gráfico 2: Faturamento por Vendedor
st.write("### Faturamento por Vendedor")
df_vendedor = df_filtrado.groupby("nome_vendedor")["preco_total"].sum().reset_index().sort_values(by="preco_total", ascending=False)
fig_vendedor = px.bar(df_vendedor, x="nome_vendedor", y="preco_total",
                      labels={"nome_vendedor": "Vendedor", "preco_total": "Faturamento (R$)"},
                      color_discrete_sequence=["#56a5ff"])
st.plotly_chart(fig_vendedor, use_container_width=True)

# 9. Gráfico 3: Quantidade Vendida por Categoria
st.write("### Quantidade Vendida por Categoria")
df_categoria = df_filtrado.groupby("categoria_produto")["quantidade_vendida"].sum().reset_index().sort_values(by="quantidade_vendida", ascending=False)
fig_categoria = px.bar(df_categoria, x="categoria_produto", y="quantidade_vendida",
                       labels={"categoria_produto": "Categoria", "quantidade_vendida": "Quantidade"},
                       color_discrete_sequence=["#73d154"])
st.plotly_chart(fig_categoria, use_container_width=True)

# 10. Gráfico 4: Faturamento por Loja (Adicionado para ficar idêntico!)
st.write("### Faturamento por Loja")
df_loja = df_filtrado.groupby("loja")["preco_total"].sum().reset_index().sort_values(by="preco_total", ascending=False)
fig_loja = px.bar(df_loja, x="loja", y="preco_total",
                  labels={"loja": "Loja", "preco_total": "Faturamento (R$)"},
                  color_discrete_sequence=["#cccccc"]) # Cor cinza idêntica ao rodapé do modelo
st.plotly_chart(fig_loja, use_container_width=True)