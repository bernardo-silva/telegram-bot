from datetime import datetime
import pandas as pd


def entry_to_string(data: datetime) -> str:
    return f"{data.day}/{data.month} às {data.hour}h{data.minute:02}"


def mbway(data):
    tabela_premios = pd.read_csv("tabela_premios.csv",
                                 index_col="data",
                                 parse_dates=["data"])
    tabela_premios = tabela_premios.sort_index()

    premio_diario = tabela_premios.loc[tabela_premios.index.date == data.date(
    )].loc[tabela_premios.tipo.str.contains("Diário")]

    premio_semanal = tabela_premios.loc[tabela_premios.tipo ==
                                        "Prémio Semanal"].loc[data:].head(1)
    premio_mensal = tabela_premios.loc[tabela_premios.tipo ==
                                       "Prémio Mensal"].loc[data:].head(1)

    premio_diario_str = ""
    for data_indice in premio_diario.index:
        premio_diario_str += f"Diário:  " + entry_to_string(data_indice)
        premio_diario_str += f" ({int(premio_diario.loc[data_indice].valor)}€) "
        premio_diario_str += f"{premio_diario.loc[data_indice].parceiro} \n"

    data_semanal = premio_semanal.index[0]
    data_mensal = premio_mensal.index[0]

    return premio_diario_str + \
    f"Semanal: " + entry_to_string(data_semanal) + f" (100€) \n"\
    f"Mensal:  " + entry_to_string(data_mensal) + f" (200€)"


if __name__ == "__main__":
    print(mbway(datetime.now()))
