import json
from datetime import datetime

import boto3
import requests

BUCKET = "st0263-covid-sazu"
PREFIX = "raw/covid_api/"

# Endpoint de la API disease.sh para histórico de Colombia
API_URL = "https://disease.sh/v3/covid-19/historical/Colombia?lastdays=all"


def download_covid_api():
    print(f"Llamando a la API: {API_URL}")
    resp = requests.get(API_URL, timeout=30)

    if resp.status_code != 200:
        print(f"Error al llamar la API. Status: {resp.status_code}")
        return

    data = resp.json()
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Nombre del archivo en S3 (RAW)
    object_key = f"{PREFIX}covid_api_colombia_{fecha}.json"

    s3 = boto3.client("s3")

    print(f"Subiendo respuesta a s3://{BUCKET}/{object_key} ...")
    s3.put_object(
        Bucket=BUCKET,
        Key=object_key,
        Body=json.dumps(data).encode("utf-8"),
        ContentType="application/json",
    )

    print("¡Listo! Archivo guardado en S3.")


if __name__ == "__main__":
    download_covid_api()
