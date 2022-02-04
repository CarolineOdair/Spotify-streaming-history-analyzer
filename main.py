import json
import pandas as pd
import datetime as dt
from data_analyzer_class import DataAnalyzer


def change_time_by_timezone(column, hours_to_add=1):
    column = pd.to_datetime(column)
    seconds = hours_to_add * 3600
    for index, value in column.items():
        value = dt.datetime.timestamp(value)
        value += seconds
        value = dt.datetime.fromtimestamp(value)
        column.at[index] = value
    return column


if __name__ == "__main__":

    print("Enter a path of file(s) (without quotation marks!). If no more matching files, leave blank")
    data = []
    while True:
        path = input(">>> ")
        if len(path) == 0:
            break
        with open(path, encoding="UTF-8") as f:
            file = list(json.load(f))
        data.extend(file)

    df = pd.DataFrame(data)
    df = df[df["msPlayed"] > 60000]
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df["endTime"] = change_time_by_timezone(df["endTime"])

    pd.set_option("display.width", None)
    pd.set_option("display.max_row", None)
    pd.set_option("display.max_columns", None)

    data_analyzer = DataAnalyzer()
    data_analyzer.main(df)
