"""Painel da atividade prática de análise de dados com Streamlit."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from gerar_dados import gerar_dados

st.set_page_config(page_title="Sabor do Sertão | Vendas", page_icon="🌵", layout="wide")
COR = "#c46625"
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [COR, "#397960", "#eab34d", "#597caa", "#9b6d91"]


def moeda(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data
def carregar_dados(conteudo):
    # Conteúdo do CSV faz parte da chave do cache: alterações invalidam a leitura.
    import io
    bruto = pd.read_csv(io.BytesIO(conteudo))
    tratado = bruto.copy()
    tratado["data"] = pd.to_datetime(tratado["data"], errors="raise")
    mediana = tratado["avaliacao"].median()
    tratado["avaliacao"] = tratado["avaliacao"].fillna(mediana)
    return bruto, tratado, mediana


caminho = Path(__file__).parent / "vendas_sabor_do_sertao.csv"
if not caminho.exists():
    gerar_dados().to_csv(caminho, index=False, encoding="utf-8")
bruto, df, mediana = carregar_dados(caminho.read_bytes())

st.title("Sabor do Sertão")
st.caption("Painel de análise de vendas • Pernambuco • Base fictícia de 2025")
st.sidebar.header("Filtrar vendas")
cidades = st.sidebar.multiselect("Cidade", sorted(df["cidade"].unique()), default=sorted(df["cidade"].unique()))
categorias = st.sidebar.multiselect("Categoria", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique()))
inicio, fim = df["data"].min().date(), df["data"].max().date()
periodo = st.sidebar.date_input("Intervalo de datas", value=(inicio, fim), min_value=inicio, max_value=fim, format="DD/MM/YYYY")
st.sidebar.caption("Selecione as duas datas. Desmarcar todas as cidades ou categorias deixa o recorte vazio.")

if len(periodo) == 2:
    filtrado = df.loc[df["cidade"].isin(cidades) & df["categoria"].isin(categorias)
                     & df["data"].between(pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]))].copy()
else:
    filtrado = df.iloc[0:0].copy()
    st.info("Selecione a data final para visualizar o recorte.")

st.caption(f"{len(filtrado):,} registros no recorte de {len(df):,} vendas da base.".replace(",", "."))
colunas = st.columns(4)
colunas[0].metric("Faturamento total", moeda(filtrado["total"].sum()))
colunas[1].metric("Número de vendas", f"{len(filtrado):,}".replace(",", "."))
colunas[2].metric("Ticket médio", moeda(filtrado["total"].mean()) if len(filtrado) else "—")
colunas[3].metric("Avaliação média", f'{filtrado["avaliacao"].mean():.2f} / 5'.replace(".", ",") if len(filtrado) else "—")

abas = st.tabs(["Visão geral", "Produtos e pagamentos", "Horários", "Exploração dos dados", "Explorador livre"])

if not filtrado.empty:
    mensal = filtrado.groupby(filtrado["data"].dt.to_period("M"))["total"].sum().reset_index()
    mensal["data"] = mensal["data"].astype(str)
    por_cidade = filtrado.groupby("cidade", as_index=False)["total"].sum().sort_values("total", ascending=False)
    top = filtrado.groupby("produto", as_index=False)["quantidade"].sum().nlargest(5, "quantidade")
    pagamentos = filtrado.groupby("pagamento").size().reset_index(name="vendas")
    with abas[0]:
        a, b = st.columns(2)
        a.plotly_chart(px.line(mensal, x="data", y="total", markers=True, title="Faturamento mensal", labels={"data": "Mês", "total": "Faturamento (R$)"}), width="stretch")
        b.plotly_chart(px.bar(por_cidade, x="cidade", y="total", title="Faturamento por cidade", labels={"cidade": "Cidade", "total": "Faturamento (R$)"}), width="stretch")
        st.subheader("Insights do recorte")
        cidade = por_cidade.iloc[0]
        produto = top.iloc[0]
        pagamento = pagamentos.sort_values("vendas", ascending=False).iloc[0]
        st.markdown(f'1. **{cidade["cidade"]}** lidera o faturamento, com **{moeda(cidade["total"])}**, representando **{cidade["total"] / filtrado["total"].sum():.1%}** do total selecionado. É uma loja importante para acompanhar estoque e atendimento.\n\n'
                    f'2. **{produto["produto"]}** é o produto mais vendido em quantidade, com **{int(produto["quantidade"])} unidades**. Vale acompanhar sua reposição para evitar falta.\n\n'
                    f'3. **{pagamento["pagamento"]}** é a forma de pagamento mais usada, em **{int(pagamento["vendas"])} vendas ({pagamento["vendas"] / len(filtrado):.1%})**. Esse resultado ajuda a organizar o atendimento no caixa.')
        st.caption("Conclusões calculadas a partir dos filtros atuais. A base é fictícia; os dados não demonstram as causas dos resultados.")
    with abas[1]:
        a, b = st.columns(2)
        fig = px.bar(top.sort_values("quantidade"), x="quantidade", y="produto", orientation="h", title="Top 5 produtos por quantidade", labels={"quantidade": "Unidades vendidas", "produto": "Produto"})
        a.plotly_chart(fig, width="stretch")
        b.plotly_chart(px.pie(pagamentos, names="pagamento", values="vendas", title="Participação dos pagamentos por número de vendas", hole=0.35), width="stretch")
    with abas[2]:
        horarios = filtrado.copy()
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        horarios["dia_semana"] = horarios["data"].dt.dayofweek.map(dict(enumerate(dias)))
        st.plotly_chart(px.density_heatmap(horarios, x="hora", y="dia_semana", histfunc="count", nbinsx=15, category_orders={"dia_semana": dias}, title="Número de vendas por dia da semana e hora", labels={"hora": "Hora", "dia_semana": "Dia da semana"}, color_continuous_scale="Oranges"), width="stretch")
else:
    with abas[0]:
        st.warning("Nenhuma venda encontrada. Ajuste os filtros na barra lateral.")

with abas[3]:
    st.subheader("Primeiras linhas do recorte tratado")
    st.dataframe(filtrado.head(10), width="stretch", hide_index=True)
    st.subheader("Resumo estatístico do recorte")
    st.dataframe(filtrado.describe().astype(str), width="stretch")
    st.subheader("Valores ausentes na base original e após tratamento")
    ausentes = pd.DataFrame({"Antes": bruto.isna().sum(), "Depois": df.isna().sum()})
    st.dataframe(ausentes, width="stretch")
    st.caption(f"Preenchi as 60 avaliações ausentes com a mediana da base original ({mediana:.1f}). Escolhi a mediana porque a avaliação usa uma escala de 1 a 5 e ela é menos influenciada por valores extremos. Assim, mantenho as vendas no cálculo do faturamento. A avaliação média inclui os valores preenchidos. O diagnóstico de ausentes mostra a base inteira para documentar o tratamento.")

with abas[4]:
    st.subheader("Explorador livre de CSV")
    st.caption("Envie um CSV, escolha os eixos e o gráfico. O explorador usa o arquivo enviado e tem seleção própria, independente da base de vendas.")
    arquivo = st.file_uploader("Escolha seu CSV", type=["csv"])
    if arquivo is not None:
        try:
            dados = pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8-sig")
        except UnicodeDecodeError:
            arquivo.seek(0)
            try:
                dados = pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
            except Exception as erro:
                st.error(f"Não foi possível ler o CSV: {erro}")
                dados = None
        except Exception as erro:
            st.error(f"Não foi possível ler o CSV: {erro}")
            dados = None
        if dados is not None:
            st.dataframe(dados.head(10), width="stretch")
            if dados.empty or len(dados.columns) < 2:
                st.warning("O arquivo precisa ter registros e pelo menos duas colunas.")
            else:
                a, b, c = st.columns(3)
                x = a.selectbox("Eixo X", dados.columns)
                y = b.selectbox("Eixo Y", dados.columns, index=1)
                tipo = c.selectbox("Tipo de gráfico", ["Barras", "Linha", "Dispersão", "Pizza"])
                try:
                    if tipo == "Pizza":
                        if not pd.api.types.is_numeric_dtype(dados[y]):
                            st.warning("Para a pizza, selecione uma coluna numérica no eixo Y.")
                        elif dados[y].dropna().lt(0).any() or dados[y].sum() <= 0:
                            st.warning("A pizza precisa de valores não negativos e soma maior que zero.")
                        else:
                            agrupado = dados.groupby(x, as_index=False, dropna=False)[y].sum() if x != y else dados
                            st.plotly_chart(px.pie(agrupado, names=x, values=y, title=f"{y} por {x}"), width="stretch")
                    else:
                        funcoes = {"Barras": px.bar, "Linha": px.line, "Dispersão": px.scatter}
                        grafico = dados.sort_values(x) if tipo == "Linha" else dados
                        st.plotly_chart(funcoes[tipo](grafico, x=x, y=y, title=f"{y} por {x}"), width="stretch")
                    st.caption("Barras e dispersão mostram os registros individuais; a linha ordena pelo eixo X; a pizza soma os valores por categoria.")
                except (ValueError, TypeError, KeyError) as erro:
                    st.warning(f"Essa combinação não pôde ser exibida. Escolha outras colunas. Detalhe: {erro}")

exportacao = filtrado.copy()
exportacao["data"] = exportacao["data"].dt.strftime("%Y-%m-%d")
st.download_button("Baixar CSV filtrado", data=exportacao.to_csv(index=False).encode("utf-8-sig"), file_name="vendas_filtradas.csv", mime="text/csv")
st.caption("Atividade acadêmica • Dados simulados • Cada linha corresponde a uma venda de um produto.")
