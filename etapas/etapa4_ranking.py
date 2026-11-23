import pandas as pd
from scipy.stats import spearmanr
from pathlib import Path

DADOS = Path(__file__).parent.parent / "dados"
custo = pd.read_csv(DADOS / "cesta_mercado_mes.csv", parse_dates=["Mes_Ano_Data"])

# Conversção da tabela em "mercado x mês"
tabela = custo.pivot(index="Estab", columns="Mes_Ano_Data", values="Custo_Cesta")
meses = list(tabela.columns)
print("Tabela mercado x mês:", tabela.shape)


#Comparar o ranking de um mês com o de outro
def comparar(distancia):
    resultados = []
    for i in range(len(meses) - distancia):
        mes_a, mes_b = meses[i], meses[i + distancia]
        # só os mercados que têm cesta completa nos DOIS meses
        par = tabela[[mes_a, mes_b]].dropna()
        if len(par) < 8:          # poucos mercados = correlação pouco confiável
            continue
        rho, p_valor = spearmanr(par[mes_a], par[mes_b])
        resultados.append({"Mes_A": mes_a, "Mes_B": mes_b, "Distancia_meses": distancia,
                           "N_Mercados": len(par), "Spearman": rho, "p_valor": p_valor})
    return pd.DataFrame(resultados)

# 1 = mês seguinte; 6 = meio ano depois; 12 = um ano depois
resultado = pd.concat([comparar(1), comparar(6), comparar(12)], ignore_index=True)

resumo = (resultado.groupby("Distancia_meses")
                   .agg(Comparacoes=("Spearman", "count"),
                        Spearman_medio=("Spearman", "mean"),
                        Spearman_minimo=("Spearman", "min"),
                        Mercados_medio=("N_Mercados", "mean"),
                        Pct_significativo=("p_valor", lambda p: 100 * (p < 0.05).mean())))
print("\nEstabilidade do ranking:")
print(resumo.to_string(float_format="%.2f"))

resultado.to_csv(DADOS / "estabilidade_ranking.csv", index=False)
print("\nArquivo salvo: estabilidade_ranking.csv")