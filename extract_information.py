from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import my_data


# Verifica si se pasó un argumento
def extract(month):
    nombre_del_archivo = f"pagina_{month}.html"

    # check if any argument was passed by
    if not month:
        return {
            "log": "No se ha proporcionado ningún argumento. Ingresa un mes adecuado.",
            "type": "error",
        }

    # verificar si el argumento existe en la carpeta
    ruta_actual = Path.cwd()
    ruta_sub_carpeta = ruta_actual / "data"
    ruta_del_mes = [archivo for archivo in ruta_sub_carpeta.rglob("*") if nombre_del_archivo == archivo.name]

    if not ruta_del_mes:
        return {"log": f"No existe el archivo {nombre_del_archivo}", "type": "error"}

    with open(f"./data/{nombre_del_archivo}", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    return {"data": soup}


def transform(soup):
    dias = soup.find_all("div", class_="list-container__wrapper")

    data = {
        "date_id": [],
        "description": [],
        "category": [],
        "payment_method": [],
        "amount": [],
        "type": [],
    }

    for dia in dias:

        # get date
        fecha = dia.find("div", class_="headline-content").get_text(strip=True)
        fecha = fecha.split(" ")
        fecha = f"{fecha[1]} {my_data.translate[fecha[2]]} 2024"

        gastos = dia.find_all("div", class_="item")

        for minute, gasto in enumerate(gastos[::-1]):
            # get description
            description = gasto.find("div", class_="item__description--one").get_text(strip=True)
            # get caetgory
            category = gasto.find("div", class_="item__description--two").get_text(strip=True)
            # get payment method
            payment_method = gasto.find("div", class_="payment-method box").get_text(strip=True)
            # get amount
            amount_negative = gasto.find("div", class_="item__amount--one negative")
            amount_positive = gasto.find("div", class_="item__amount--one positve")

            # since I dont have the exact information about the time the expense take place, I im asuming that every minute a expense happened. It means that at max, there must be 59 register each day
            data["date_id"].append(f"{fecha} {minute}")
            data["description"].append(description)
            data["category"].append(category)
            data["payment_method"].append(payment_method)
            data["amount"].append(amount_positive.get_text(strip=True) if amount_positive else amount_negative.get_text(strip=True))
            data["type"].append("income" if amount_positive else "expense")

    dataframe = pd.DataFrame(data)

    # just for testing
    dataframe["date_id"] = pd.to_datetime(dataframe["date_id"], format="%d %B %Y %M", errors="coerce")

    return {
        "log": f"data extracted successfully",
        "type": "success",
        "data": dataframe,
    }


def load(dataframe):
    file_name = "transaction.csv"
    dataframe.to_csv(f"./db/{file_name}", index=False)
    return {
        "log": f"data loaded successfully in {file_name}.",
        "type": "success",
    }


def ETL_transaction_table(month):
    extracted_data = extract(month)
    transformed_data = transform(extracted_data["data"])
    load(transformed_data["data"])


month = "octubre"
ETL_transaction_table(month)
