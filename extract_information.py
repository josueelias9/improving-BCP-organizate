import re
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import my_data


# Verifica si se pasó un argumento
def extract_transaction(html_content):
    return {"data": html_content, "type": "success"}


def transform_transaction(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
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

        #
        dataframe["date_id"] = pd.to_datetime(dataframe["date_id"], format="%d %B %Y %M", errors="coerce")

        # add column to get more info of the date
        dataframe["date"] = dataframe["date_id"].dt.strftime("%M - %A %d, %B")

        return {
            "log": f"data extracted successfully",
            "type": "success",
            "data": dataframe,
        }
    except:
        return {
            "log": f"The data could not be extracted",
            "type": "error",
        }


def load_transaction(dataframe):
    file_path = "./db/transaction.csv"

    # check if the file exists
    if Path(file_path).is_file():
        combined_data = pd.concat([pd.read_csv(file_path), dataframe], ignore_index=True)
        combined_data["date_id"] = pd.to_datetime(combined_data["date_id"], errors="coerce")
        # sort reverse
        combined_data.sort_values(by="date_id", inplace=True, ascending=False)
        combined_data.drop_duplicates(inplace=True)
        combined_data.to_csv(file_path, index=False)

    # If file doesn't exist, simply write the dataframe to it
    else:
        dataframe.to_csv(file_path, index=False)

    return {
        "log": f"data loaded successfully in {file_path}.",
        "type": "success",
    }


def ETL_transaction(html_content):
    extracted_data = extract_transaction(html_content)

    if extracted_data["type"] == "success":
        transformed_data = transform_transaction(extracted_data["data"])

        if transformed_data["type"] == "success":
            loaded_data = load_transaction(transformed_data["data"])

            if loaded_data["type"] == "success":
                print(loaded_data["log"])

            else:
                print(loaded_data["log"])

        else:
            print(transformed_data["log"])

    else:
        print(extracted_data["log"])


def corregir_texto(texto):
    # Diccionario de códigos de escape y sus reemplazos Unicode
    reemplazos = {
        r"\\'e1": "á",
        r"\\'e9": "é",
        r"\\'ed": "í",
        r"\\'f3": "ó",
        r"\\'fa": "ú",
        r"\'c1": "Á",
        r"\'c9": "É",
        r"\'cd": "Í",
        r"\'d3": "Ó",
        r"\'da": "Ú",
        r"\'f1": "ñ",
        r"\'d1": "Ñ",
        r"\'fc": "ü",
        r"\'dc": "Ü",
    }

    # Reemplazar cada secuencia de escape en el texto
    for codigo, caracter in reemplazos.items():
        texto = re.sub(codigo, caracter, texto)

    return texto


def ETL_category():
    # fails if the file doesn't exist. Correct it
    with open("./data/categories.html", "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    categories = soup.find_all("ul", class_="options")

    data = {
        "category": ["Sin categoría"],
        "description": ["not defined in the web"],
    }

    for category in categories:
        data["category"].append(corregir_texto(category.find("div", class_="description--one").get_text(strip=True)))
        data["description"].append(corregir_texto(category.find("div", class_="description--two").get_text(strip=True)))

    dataframe = pd.DataFrame(data)

    dataframe.to_csv("./db/category.csv", index=False)


ETL_category()
