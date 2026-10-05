# Sabor do Sertão — Painel de vendas

Atividade prática de análise de dados com Python, Streamlit, pandas e Plotly. O painel ajuda a comparar vendas das lojas de Recife, Olinda, Caruaru, Petrolina e Garanhuns.

## Como executar no VS Code (Windows)

1. Extraia o ZIP e abra a pasta `sabor-do-sertao` no VS Code.
2. Abra o terminal. Use Python 3.10 ou superior.
3. Execute os comandos abaixo, um por vez:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe gerar_dados.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost --browser.serverAddress localhost --browser.gatherUsageStats false
```

Esses comandos usam o Python da venv diretamente, sem precisar ativá-la no PowerShell. Se o comando `python` não estiver disponível, tente `py` no primeiro comando ou selecione a instalação de Python no VS Code.

O navegador abrirá em `http://localhost:8501`. Para encerrar o painel, pressione `Ctrl+C` no terminal.

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python gerar_dados.py
.venv/bin/python -m streamlit run app.py --server.address localhost --browser.serverAddress localhost --browser.gatherUsageStats false
```

## O que foi implementado

- **Nível 1:** primeiras linhas, `describe()` e contagem de valores ausentes antes e depois do tratamento.
- **Nível 2:** faturamento, número de vendas, ticket médio e avaliação média.
- **Nível 3:** filtros por cidade, categoria e intervalo de datas.
- **Nível 4:** linha do faturamento mensal, barras por cidade, top 5 produtos por quantidade e participação dos pagamentos. Também inclui mapa de calor por dia da semana e hora.
- **Nível 5:** três insights calculados com o recorte atual e botão para exportar o CSV filtrado.
- **Bônus:** explorador de CSV com eixos X/Y e gráficos de barras, linha, dispersão e pizza.

Os KPIs, gráficos de vendas, insights e exportação usam o mesmo recorte. O diagnóstico de ausentes usa a base completa para mostrar o tratamento. O explorador livre usa o CSV enviado pelo usuário e não recebe os filtros da base de vendas.

## Dados e tratamento

O gerador segue o código do enunciado: semente `42`, 5.000 registros de 2025 e 60 avaliações ausentes. O CSV já acompanha o projeto; o aplicativo também o gera se não estiver presente.

Preenchi as avaliações ausentes com a mediana da base original. Essa escolha preserva as vendas e reduz a influência de valores extremos na substituição. A avaliação média exibida inclui essas avaliações preenchidas.

Cada linha representa uma venda de um produto, pois a base não fornece um identificador de pedido. Assim:

- Faturamento = soma da coluna `total`.
- Número de vendas = quantidade de linhas no recorte.
- Ticket médio = faturamento dividido pelo número de vendas.
- Avaliação média = média após preencher os ausentes.
- Participação dos pagamentos = proporção do número de vendas, sem ponderar pelo faturamento.

No explorador, barras e dispersão mostram registros individuais; a linha ordena por X e a pizza soma Y por categoria X. Para pizza, Y precisa ser numérico, não negativo e ter soma positiva.

## Arquivos

- `app.py`: interface e análises.
- `gerar_dados.py`: geração reproduzível da base.
- `requirements.txt`: dependências.
- `vendas_sabor_do_sertao.csv`: base fictícia.
- `imagens/painel.png`: print real do painel executando.

## Print do painel funcionando

![Painel Sabor do Sertão](imagens/painel.png)

## Entrega no GitHub

Crie um repositório e envie os arquivos desta pasta, incluindo a pasta `imagens`. Não envie `.venv` ou `__pycache__`. Copie o link do repositório para entregar ao professor. Revise o código com sua dupla e alternem os papéis de piloto e navegador a cada 20 minutos, conforme o enunciado.

