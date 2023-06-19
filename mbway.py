from datetime import datetime
import pandas as pd


def mbway(data):
    tabela_premios = pd.read_csv("tabela_premios.csv",
                                 index_col="data",
                                 parse_dates=["data"])
    tabela_premios = tabela_premios.sort_index()

    premio_diario = tabela_premios.loc[tabela_premios.index.date == data.date(
    )].loc[tabela_premios.tipo == "Prémio Diário"]

    premio_semanal = tabela_premios.loc[tabela_premios.tipo ==
                                        "Prémio Semanal"].loc[data:].head(1)
    premio_mensal = tabela_premios.loc[tabela_premios.tipo ==
                                       "Prémio Mensal"].loc[data:].head(1)

    premio_diario_str = ""
    for data_indice in premio_diario.index:
        premio_diario_str += f"Diário: {data_indice.day}/{data_indice.month} às {data_indice.hour}h{data_indice.minute} ({int(premio_diario.loc[data_indice].valor)}€) {premio_diario.loc[data_indice].parceiro} \n"

    data_semanal = premio_semanal.index[0]
    data_mensal = premio_mensal.index[0]

    return premio_diario_str + \
    f"Semanal: {data_semanal.day}/{data_semanal.month} às {data_semanal.hour}h{data_semanal.minute} (100€) \n"\
    f"Mensal:  {data_mensal.day}/{data_mensal.month} às {data_mensal.hour}h{data_mensal.minute}  (200€)"


if __name__ == "__main__":
    print(mbway(datetime.now()))
