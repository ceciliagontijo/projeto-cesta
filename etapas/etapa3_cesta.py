import pandas as pd
from pathlib import Path

DADOS = Path(__file__).parent.parent / "dados"
mensal = pd.read_csv(DADOS / "preco_mensal_mercado.csv", parse_dates=["Mes_Ano_Data"])

# PASSO 1 - Definir a cesta (quantidades do DIEESE, Região 1)
# Quantidade de cada produto que uma pessoa adulta consome por mês
cesta = {
    "Carne Bovina Coxão Mole": 6.0,
    "Leite":                   7.5,
    "Feijão":                  4.5,
    "Arroz":                   3.0,
    "Farinha de Trigo":        1.5,
    "Batata":                  6.0,
    "Tomate":                  9.0,
    "Pão Francês":             6.0,
    "Café":                    0.6,
    "Banana":                  7.5,   # oficial: 90 unidades; adotamos ~7,5 kg (ver PASSO 2)
    "Açúcar":                  3.0,
    "Óleo":                    0.75,
    "Manteiga":                0.75,
}

# PASSO 2 - Juntar as duas bananas em uma só
bananas = mensal[mensal["Produto"].isin(["Banana Nanica", "Banana Prata"])]
banana = (bananas.groupby(["Mes_Ano_Data", "Estab"], as_index=False)["PPK"].mean()
                 .assign(Produto="Banana"))

mensal = pd.concat([mensal, banana], ignore_index=True)   # concat = empilhar tabelas


# PASSO 3 - Custo da cesta em cada mercado, em cada mês
itens = mensal[mensal["Produto"].isin(cesta.keys())].copy()

# Custo de cada item = preço por kg x quantidade da cesta
itens["Quantidade_Cesta"] = itens["Produto"].map(cesta)
itens["Custo_Item"] = itens["PPK"] * itens["Quantidade_Cesta"]

# Somamos os itens de cada mercado/mês e contamos quantos produtos ele tinha
custo = (itens.groupby(["Mes_Ano_Data", "Estab"], as_index=False)
              .agg(Custo_Cesta=("Custo_Item", "sum"),
                   N_Produtos=("Produto", "nunique")))

# Só é justo comparar mercados que têm a cesta COMPLETA.
# Um mercado sem carne pareceria "barato" só por faltar o item mais caro.
print("Mercados-mês no total:", len(custo))
custo = custo[custo["N_Produtos"] == len(cesta)].drop(columns="N_Produtos")
print("Mercados-mês com cesta completa:", len(custo))

# Ranking dentro de cada mês: 1 = mercado mais barato
custo["Ranking"] = custo.groupby("Mes_Ano_Data")["Custo_Cesta"].rank(method="min").astype(int)

# PASSO 4 - Resumo por mês: quanto dá para economizar?
resumo = (custo.groupby("Mes_Ano_Data")["Custo_Cesta"]
               .agg(N_Mercados="count", Minimo="min", Media="mean", Maximo="max")
               .reset_index())
resumo["Economia_vs_Media"] = resumo["Media"] - resumo["Minimo"]          # em R$
resumo["Economia_vs_Media_%"] = 100 * resumo["Economia_vs_Media"] / resumo["Media"]
resumo["Diferenca_Max_Min"] = resumo["Maximo"] - resumo["Minimo"]

print("\nResumo mensal (primeiros meses):")
print(resumo.head().to_string(index=False, float_format="%.2f"))
print("\nEconomia média escolhendo o mercado mais barato: "
      f"R$ {resumo['Economia_vs_Media'].mean():.2f} "
      f"({resumo['Economia_vs_Media_%'].mean():.1f}% da cesta média)")

# PASSO 5 - Validação: comparar com o valor oficial publicado

# O Observatório PUC-Campinas calcula a cesta com o preço MÉDIO de
# cada produto entre todos os mercados. Refazemos essa conta e
# comparamos com os valores que eles publicaram.
publicado = {"2023-10-01": 690.91, "2024-06-01": 781.23, "2025-01-01": 754.11}

print("\nValidação contra o valor publicado:")
for mes, oficial in publicado.items():
    do_mes = mensal[mensal["Mes_Ano_Data"] == mes]
    preco_medio = do_mes.groupby("Produto")["PPK"].mean()
    calculado = sum(preco_medio[p] * q for p, q in cesta.items())
    erro = 100 * (calculado - oficial) / oficial
    print(f"  {mes[:7]}: calculado R$ {calculado:.2f} | publicado R$ {oficial:.2f} | diferença {erro:+.1f}%")

# PASSO 6 - Salvar para o Power BI
custo.to_csv(DADOS / "cesta_mercado_mes.csv", index=False)
resumo.to_csv(DADOS / "cesta_resumo_mensal.csv", index=False)
print("\nArquivos salvos: cesta_mercado_mes.csv e cesta_resumo_mensal.csv")