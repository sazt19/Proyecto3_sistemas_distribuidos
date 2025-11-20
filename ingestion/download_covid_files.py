import requests
import boto3
from datetime import datetime

BUCKET = "st0263-covid-sazu"

def download_covid_file():
    # URL de ejemplo — cámbiala por la que te dé el profe o la data real
    url = "https://www.datos.gov.co/api/views/gt2j-8ykr/rows.csv?accessType=DOWNLOAD"

    fecha = datetime.now().strftime("%Y-%m-%d")
    file_name = f"covid_data_{fecha}.csv"
    s3_key = f"raw/covid/{file_name}"

    print(f"Descargando archivo desde {url} ...")
    response = requests.get(url)

    if response.status_code == 200:
        open(file_name, "wb").write(response.content)
        print(f"Guardado localmente como {file_name}")

        s3 = boto3.client("s3")
        s3.upload_file(file_name, BUCKET, s3_key)

        print(f"Subido a S3: s3://{BUCKET}/{s3_key}")
    else:
        print("Error al descargar el archivo:", response.status_code)

if __name__ == "__main__":
    download_covid_file()
