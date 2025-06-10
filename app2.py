import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from folium.plugins import MarkerCluster

st.set_page_config(page_title="ReciclaMack Dashboard", layout="wide")

# Carregamento dos dados
@st.cache_data
def load_data():
    df = pd.read_csv("pontos_de_coleta_capitais_notebook.csv")
    df = df.dropna(subset=["lat", "lng"])
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df["canal"] = df["canal"].astype(str)
    df = df.dropna(subset=["lat", "lng"])
    df["estado"] = df["endereco"].str.extract(r"([A-Z]{2})$")
    return df

df = load_data()


populacao_estado = {
    "AC": 830_018,
    "AL": 3_127_683,
    "AM": 4_269_995,
    "AP": 733_759,
    "BA": 14_141_626,
    "CE": 9_058_931,
    "DF": 3_094_325,
    "ES": 4_108_508,
    "GO": 7_056_495,
    "MA": 7_610_361,
    "MG": 20_539_989,
    "MS": 2_817_381,
    "MT": 3_833_712,
    "PA": 8_120_131,
    "PB": 3_974_687,
    "PE": 9_051_113,
    "PI": 3_302_729,
    "PR": 11_444_380,
    "RJ": 16_615_526,
    "RN": 3_271_199,
    "RO": 1_581_196,
    "RR": 636_707,
    "RS": 11_444_380,
    "SC": 7_610_361,
    "SE": 2_210_004,
    "SP": 46_024_937,
    "TO": 1_511_460
}

estado_para_regiao = {
    'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte',
    'BA': 'Nordeste', 'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste',
    'GO': 'Centro-Oeste', 'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'MG': 'Sudeste', 'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul',
    'PE': 'Nordeste', 'PI': 'Nordeste', 'RJ': 'Sudeste', 'RN': 'Nordeste',
    'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte', 'SC': 'Sul',
    'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
}

pop_df = pd.DataFrame(list(populacao_estado.items()), columns=["estado", "populacao"])

# Navegação
aba = st.sidebar.radio(
    "Escolha uma visualização:",
    ["Mapa Interativo", "Análise de Dados", "Cobertura por População"]
)

# ------------------------- ABA 1: MAPA INTERATIVO ------------------------
if aba == "Mapa Interativo":
    st.title("Pontos de Coleta de Lixo Eletrônico no Brasil")

    cidades = ["Todas"] + sorted(df["cidade_consulta"].dropna().unique())
    cidade_selecionada = st.selectbox("Filtrar por cidade", cidades)

    canais = ["Todos"] + sorted(df["canal"].dropna().unique())
    canal_selecionado = st.selectbox("Filtrar por canal", canais)

    df_filtro = df.copy()
    if cidade_selecionada != "Todas":
        df_filtro = df_filtro[df_filtro["cidade_consulta"] == cidade_selecionada]
    if canal_selecionado != "Todos":
        df_filtro = df_filtro[df_filtro["canal"] == canal_selecionado]

    st.markdown(f"**Total de pontos encontrados:** {len(df_filtro)}")
    st.markdown(f"**Número de cidades atendidas:** {df_filtro['cidade_consulta'].nunique()}")

    st.markdown("### Mapa de Pontos de Coleta")
    map_center = [df_filtro["lat"].mean(), df_filtro["lng"].mean()]
    m = folium.Map(location=map_center, zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df_filtro.iterrows():
        popup_text = f"<b>{row['nome']}</b><br>{row['endereco']}<br><i>{row['canal']}</i>"
        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=popup_text,
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(marker_cluster)

    folium_static(m, width=1000, height=600)

    st.subheader("Top 10 Cidades com mais Pontos de Coleta")
    top_cidades = df["cidade_consulta"].value_counts().head(10).reset_index()
    top_cidades.columns = ["Cidade", "Quantidade"]
    fig = px.bar(top_cidades, x="Cidade", y="Quantidade", title="Top 10 Cidades com mais Pontos")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.markdown(
        "📌 **Fonte dos dados:** [ABREE - Associação Brasileira de Reciclagem de Eletroeletrônicos e Eletrodomésticos](https://abree.org.br)"
    )


# -------------------------- ABA 2: ANÁLISE DE DADOS -------------------------
elif aba == "Análise de Dados":
    st.title("Análise Exploratória dos Pontos de Coleta")

    col1, col2, col3= st.columns(3)
    with col1:
        st.metric("Total de Pontos de Coleta", len(df))
        st.metric("Total de Cidades", df['cidade_consulta'].nunique())
    with col2:
        st.metric("Estados Representados", df['estado'].nunique())
        st.metric("Canais Únicos", df['canal'].nunique())
    with col3:
        st.metric("Total de Regiões", value = 5)

    st.subheader("Distribuição por Canal")
    canal_counts = df["canal"].value_counts().reset_index()
    canal_counts.columns = ["Canal", "Quantidade"]
    fig_canal = px.pie(canal_counts, names="Canal", values="Quantidade", title="Distribuição de Pontos por Canal")
    st.plotly_chart(fig_canal)

    st.subheader("Distribuição Geográfica por Estado")
    estado_counts = df["estado"].value_counts().reset_index()
    estado_counts.columns = ["Estado", "Quantidade"]
    fig_estado = px.bar(estado_counts, x="Estado", y="Quantidade", title="Quantidade de Pontos por Estado")
    st.plotly_chart(fig_estado, use_container_width=True)

    st.subheader("Tamanho dos Pontos (Porte)")
    porte_counts = df["porte"].value_counts().reset_index()
    porte_counts.columns = ["Porte", "Quantidade"]
    fig_porte = px.pie(porte_counts, names="Porte", values="Quantidade", title="Distribuição por Porte")
    st.plotly_chart(fig_porte)

    st.dataframe(df[["nome", "endereco", "canal", "cidade_consulta", "cep_consulta"]].reset_index(drop=True))

    st.subheader("Distribuição por Região")
    df['Região'] = df['estado'].map(estado_para_regiao)
    count_regiao = df['Região'].value_counts().reset_index()
    count_regiao.columns = ["Região", "Quantidade"]
    fig_regiao = px.pie(count_regiao, names="Região", values="Quantidade", title="Distribuição por Região")
    st.plotly_chart(fig_regiao)
    st.markdown("---")
    st.markdown(
        "📌 **Fonte dos dados:** [ABREE - Associação Brasileira de Reciclagem de Eletroeletrônicos e Eletrodomésticos](https://abree.org.br)"
    )

# ------------------------ NOVA ABA: COBERTURA POR POPULAÇÃO ---------------------
elif aba == "Cobertura por População":
    st.title("Cobertura de Pontos de Coleta por População")

    estado_pontos = df["estado"].value_counts().reset_index()
    estado_pontos.columns = ["estado", "qtd_pontos"]

    cobertura = pd.merge(estado_pontos, pop_df, on="estado", how="left")
    cobertura["pontos_por_100mil"] = (cobertura["qtd_pontos"] / cobertura["populacao"]) * 100000
    cobertura = cobertura.sort_values(by="pontos_por_100mil", ascending=False)

    st.markdown("### Pontos de Coleta por 100 mil Habitantes")
    fig_cobertura = px.bar(
        cobertura,
        x="estado",
        y="pontos_por_100mil",
        title="Cobertura por População (pontos a cada 100 mil hab)",
        labels={"pontos_por_100mil": "Pontos / 100 mil hab"},
        color="pontos_por_100mil",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_cobertura, use_container_width=True)

    st.dataframe(cobertura[["estado", "qtd_pontos", "populacao", "pontos_por_100mil"]].round(2))
    st.markdown("---")
    st.markdown(
        "📌 **Fonte dos dados:** [ABREE - Associação Brasileira de Reciclagem de Eletroeletrônicos e Eletrodomésticos](https://abree.org.br)"
    )


