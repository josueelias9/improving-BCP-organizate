from bs4 import BeautifulSoup
import sys
from pathlib import Path
import pandas as pd


# Verifica si se pasó un argumento
def start_program():
    nombre_del_archivo = f"pagina_{sys.argv[1]}.html"

    if len(sys.argv) == 0:
        return {
            "log": "No se ha proporcionado ningún argumento. Ingresa un mes adecuado.",
            "type": "error",
        }

    # verificar si el argumento existe en la carpeta
    ruta_actual = Path.cwd()
    ruta_sub_carpeta = ruta_actual / "data"
    ruta_del_mes = [
        archivo
        for archivo in ruta_sub_carpeta.rglob("*")
        if nombre_del_archivo == archivo.name
    ]

    if not ruta_del_mes:
        return {"log": f"No existe el archivo {nombre_del_archivo}", "type": "error"}

    with open(f"./data/{nombre_del_archivo}", "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")

    dias = soup.find_all("div", class_="list-container__wrapper")

    data = {
        "fecha": [],
        "descripcion 1": [],
        "category": [],
        "payment_method": [],
        "monto": [],
    }

    for dia in dias:
        dia_fecha = dia.find("div", class_="headline-content").get_text(strip=True)

        gastos = dia.find_all(
            "div", class_="item"
        )  # Cambia la clase según el tipo de gasto que deseas

        for gasto in gastos:
            # Extraer la descripción
            descripcion_1 = gasto.find("div", class_="item__description--one").get_text(
                strip=True
            )
            descripcion_2 = gasto.find("div", class_="item__description--two").get_text(
                strip=True
            )
            payment_method = gasto.find("div", class_="payment-method box").get_text(
                strip=True
            )
            monto_negative = gasto.find("div", class_="item__amount--one negative")
            monto_positive = gasto.find("div", class_="item__amount--one positve")

            data["fecha"].append(dia_fecha)
            data["descripcion 1"].append(descripcion_1)
            data["category"].append(descripcion_2)
            data["payment_method"].append(payment_method)
            data["monto"].append(
                monto_positive.get_text(strip=True)
                if monto_positive
                else monto_negative.get_text(strip=True)
            )

    df = pd.DataFrame(data)
    df.to_csv(f"./db/gastos_{sys.argv[1]}.csv", index=False)

    return {
        "log": f"Datos extraídos y guardados en gastos_{sys.argv[1]}.csv.",
        "type": "success",
    }


a = start_program()
print(a)
