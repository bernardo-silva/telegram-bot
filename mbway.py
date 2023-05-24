from datetime import datetime
import pandas as pd


def mbway(date):
    tabela_premios = pd.read_csv("tabela_premios.csv",
                                 index_col="data",
                                 parse_dates=["data"])
    tabela_premios = tabela_premios.sort_index()

    premio_diario = tabela_premios.loc[tabela_premios.tipo ==
                                       "Prémio Diário"].loc[date:].head(1)
    premio_semanal = tabela_premios.loc[tabela_premios.tipo ==
                                        "Prémio Semanal"].loc[date:].head(1)
    premio_mensal = tabela_premios.loc[tabela_premios.tipo ==
                                       "Prémio Mensal"].loc[date:].head(1)

    data_diario = str(premio_diario.index[0]).split()
    data_semanal = str(premio_semanal.index[0]).split()
    data_mensal = str(premio_mensal.index[0]).split()

    return f"Diário:  {data_diario[0]} às {data_diario[1]} (20€) \n" \
    f"Semanal: {data_semanal[0]} às {data_semanal[1]} (100€) \n"\
    f"Mensal:  {data_mensal[0]} às {data_mensal[1]} (200€)"


if __name__ == "__main__":
    print(mbway(datetime.now()))
