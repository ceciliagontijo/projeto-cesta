import pandas as pd
import numpy as np
import warnings
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")

DADOS = Path(__file__).parent.parent / "dados"
series = pd.read_csv(DADOS / "series_produtos.csv", index_col="Mes_Ano_Data", parse_dates=True)
INICIO_TESTE = 24  


# Teste de estacionariedade (ADF)
# teste da tendência de um produto
print("Teste ADF (primeiros 24 meses):")
d_por_produto = {}
for produto in series.columns:
    treino = series[produto].values[:INICIO_TESTE]
    p_valor = adfuller(treino)[1]
    d_por_produto[produto] = 0 if p_valor < 0.05 else 1
    print(f"  {produto:25s} p-valor = {p_valor:.3f} -> d = {d_por_produto[produto]}")


# Escolher p e q pelo AIC
# p = quantos meses passados o modelo usa
# q = quantos erros passados o modelo usa
# Testamos combinações pequenas (0, 1 ou 2) e ficamos com a de menor AIC.
print("\nOrdem escolhida (p, d, q) para cada produto:")
ordem = {}
for produto in series.columns:
    treino = series[produto].values[:INICIO_TESTE]
    d = d_por_produto[produto]
    melhor_aic, melhor = np.inf, None
    for p in range(3):
        for q in range(3):
            try:
                aic = ARIMA(treino, order=(p, d, q)).fit().aic
            except Exception:
                continue         
            if aic < melhor_aic:
                melhor_aic, melhor = aic, (p, d, q)
    ordem[produto] = melhor
    print(f"  {produto:25s} {melhor}")

# A cada mês, o modelo é reajustado com todo o passado disponível
# e prevê só o mês seguinte.
linhas = []
for produto in series.columns:
    valores = series[produto].values
    for t in range(INICIO_TESTE, len(valores)):
        passado = valores[:t]
        modelo = ARIMA(passado, order=ordem[produto]).fit()
        previsto = modelo.forecast(steps=1)[0]
        linhas.append({"Produto": produto,
                       "Mes_Ano_Data": series.index[t],
                       "Modelo": "ARIMA",
                       "Real": valores[t],
                       "Previsto": previsto})
arima = pd.DataFrame(linhas)


# Juntar com os modelos da etapa 5 e comparar
previsoes = pd.read_csv(DADOS / "previsoes.csv", parse_dates=["Mes_Ano_Data"])
previsoes = previsoes[previsoes["Modelo"] != "ARIMA"]          # evita duplicar se rodar 2x
previsoes = pd.concat([previsoes, arima], ignore_index=True)
previsoes["Erro"] = previsoes["Previsto"] - previsoes["Real"]

def metricas(g):
    return pd.Series({
        "MAE":  g["Erro"].abs().mean(),
        "RMSE": np.sqrt((g["Erro"] ** 2).mean()),
        "MAPE": 100 * (g["Erro"].abs() / g["Real"]).mean(),
    })

erros = previsoes.groupby(["Produto", "Modelo"]).apply(metricas).reset_index()

print("\nMAPE (%) por produto e modelo:")
print(erros.pivot(index="Produto", columns="Modelo", values="MAPE").round(1).to_string())
print("\nMédia geral por modelo:")
print(erros.groupby("Modelo")[["MAE", "RMSE", "MAPE"]].mean().round(2).to_string())

previsoes.to_csv(DADOS / "previsoes.csv", index=False)
erros.to_csv(DADOS / "erros_modelos.csv", index=False)
pd.DataFrame([{"Produto": k, "p": v[0], "d": v[1], "q": v[2]} for k, v in ordem.items()]) \
  .to_csv(DADOS / "arima_ordens.csv", index=False)
print("\nArquivos salvos: previsoes.csv, erros_modelos.csv, arima_ordens.csv")