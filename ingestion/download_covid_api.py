import boto3
import json
import requests
from datetime import datetime

BUCKET = "st0263-covid-sazu"

def download_covid_api():
    # API de ejemplo
    api_url = "https://www.datos.gov.co/resource/gt2j-8ykr.json?$limit=5000"

    print("Llamando a la API...")
    r = requests.get(api_url)

    if r.status_code == 200:
        data = r.json()
        fecha = datetime.now().strftime("%Y-%m-%d")

        file_name = f"covid_api_{fecha}.json"
        s3_key = f"raw/covid_api/{file_name}"

        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=BUCKET,
            Key=s3_key,
            Body=json.dumps(data)
        )

        print(f"Datos API guardados en s3://{BUCKET}/{s3_key}")
    else:
        print("Error:", r.status_code)

if __name__ == "__main__":
    download_covid_api()
