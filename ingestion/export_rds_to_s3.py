import pymysql
import pandas as pd
import boto3
from io import StringIO
from datetime import datetime

# ====== CONFIGURA ESTO CON TUS DATOS ======
RDS_HOST = "covid-rds.c7e0k02o8a41.us-east-2.rds.amazonaws.com"  # pon exactamente tu endpoint
RDS_PORT = 3306
RDS_USER = "admin"
RDS_PASSWORD = "0819montes"  # puedes leerlo de un .env si quieres
RDS_DB = "covid_db"

BUCKET = "st0263-covid-sazu"
TABLES = ["dim_departamento", "poblacion_departamento", "hospital"]
# ==========================================


def export_table(table_name: str):
    print(f"Conectando a RDS para leer tabla {table_name}...")

    conn = pymysql.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        user=RDS_USER,
        password=RDS_PASSWORD,
        db=RDS_DB,
        cursorclass=pymysql.cursors.DictCursor,
    )

    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql(query, conn)
    conn.close()

    print(f"Tabla {table_name}: {len(df)} filas leídas")

    # Convertir a CSV en memoria
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client("s3")
    fecha = datetime.now().strftime("%Y-%m-%d")
    key = f"raw/rds/{table_name}/{table_name}_{fecha}.csv"

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=csv_buffer.getvalue().encode("utf-8")
    )

    print(f"Subido a s3://{BUCKET}/{key}")


def main():
    for table in TABLES:
        export_table(table)


if __name__ == "__main__":
    main()
