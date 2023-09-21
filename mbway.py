from datetime import datetime
import pandas as pd


def entry_to_string(data: datetime, valor: int, parceiro: str) -> str:
    text = f"{data.hour:02}h{data.minute:02} {valor}€ {parceiro}"
    now = datetime.now()
    if data.day == now.day and data.month == now.month:
        text = f"**{text}**"
    return text + "\n"


def mbway(data):
    tabela_premios = pd.read_csv("tabela_premios.csv",
                                 index_col="data",
                                 parse_dates=["data"])
    tabela_premios = tabela_premios.sort_index()

    premio_diario = tabela_premios.loc[(tabela_premios.index.date == data.date()) & (
        tabela_premios.tipo.str.contains("Diário"))]

    premio_semanal = tabela_premios.loc[tabela_premios.tipo ==
                                        "Prémio Semanal"].loc[data:].head(1)
    premio_mensal = tabela_premios.loc[tabela_premios.tipo ==
                                       "Prémio Mensal"].loc[data:].head(1)

    premio_diario_str = f"Dia {data.day:02}/{data.month:02}:\n"

    for data_indice, premio in premio_diario.iterrows():
        premio_diario_str += entry_to_string(data_indice,
                                             int(premio.valor), premio.parceiro)
        #premio_diario_str += f"Diário:  " + entry_to_string(data_indice)
        #premio_diario_str += f" {int(premio_diario.loc[data_indice].valor):3}€ "
        #premio_diario_str += f"{premio_diario.loc[data_indice].parceiro} \n"

    data_semanal = premio_semanal.index[0]
    data_mensal = premio_mensal.index[0]

    premio_semanal_str = f"Semanal: {data_semanal.day:02}/{data_semanal.month:02}, "
    premio_semanal_str += entry_to_string(data_semanal,
                                          premio_semanal.loc[data_semanal].valor,
                                          premio_semanal.loc[data_semanal].parceiro)

    premio_mensal_str = f"Mensal:  {data_mensal.day:02}/{data_mensal.month:02}, "
    premio_mensal_str += entry_to_string(data_mensal,
                                         premio_mensal.loc[data_mensal].valor,
                                         premio_mensal.loc[data_mensal].parceiro)

    return premio_diario_str + "\n" + premio_semanal_str + premio_mensal_str


def fetch_prize_table():
    dataframes_mbway = pd.read_html(
        "https://www.mbway.pt/challenge-regulamento/")
    premios = dataframes_mbway[5]
    premios = premios.drop(5, axis=1)
    premios.columns = ["tipo", "dia", "hora", "valor", "parceiro"]
    premios = premios.drop(0)
    premios["data"] = premios.dia+" "+premios.hora
    premios = premios.drop(["dia", "hora"], axis=1)
    premios.data = pd.to_datetime(premios.data, dayfirst=True)
    premios.to_csv("tabela_premios.csv", index=False)


if __name__ == "__main__":
    fetch_prize_table()
    print(mbway(datetime.now()))
