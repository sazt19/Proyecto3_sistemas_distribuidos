from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col, to_date, lit

BUCKET = "st0263-covid-sazu"

def main():
    spark = (
        SparkSession.builder
        .appName("ETL_RAW_TO_TRUSTED")
        .getOrCreate()
    )

    # ==========================
    # 1. LEER COVID API RAW (JSON)
    # ==========================
    covid_raw_path = f"s3://{BUCKET}/raw/covid_api/"
    covid_raw = spark.read.json(covid_raw_path)

    # JSON viene como estructura anidada → aplanemos:
    covid_ts = covid_raw.select(
        explode("timeline.cases").alias("date", "cases")
    )
    covid_ts = covid_ts.withColumn("cases", col("cases").cast("int"))
    covid_ts = covid_ts.withColumn("date", to_date(col("date"), "M/d/yy"))

    # ==========================
    # 2. LEER RDS EXPORTADO (CSV)
    # ==========================
    rds_path = f"s3://{BUCKET}/raw/rds/"
    hospital = spark.read.csv(f"{rds_path}/hospital/", header=True, inferSchema=True)
    departamentos = spark.read.csv(f"{rds_path}/dim_departamento/", header=True, inferSchema=True)
    poblacion = spark.read.csv(f"{rds_path}/poblacion_departamento/", header=True, inferSchema=True)

    # ==========================
    # 3. TRANSFORMACIONES
    # ==========================

    # Tabla: población por departamento
    poblacion = poblacion.withColumnRenamed("anio", "year")

    # Unir hospitales con departamentos
    hospitales_full = hospital.join(
        departamentos,
        hospital.id_departamento == departamentos.id_departamento,
        "left"
    ).select(
        "id_hospital", "nombre", "ciudad", "region",
        hospital.id_departamento, "capacidad_camas"
    )

    # ==========================
    # 4. ESCRIBIR EN TRUSTED (PARQUET)
    # ==========================

    covid_ts.write.mode("overwrite").parquet(
        f"s3://{BUCKET}/trusted/covid_timeseries/"
    )

    hospitales_full.write.mode("overwrite").parquet(
        f"s3://{BUCKET}/trusted/hospital_departamento/"
    )

    poblacion.write.mode("overwrite").parquet(
        f"s3://{BUCKET}/trusted/poblacion/"
    )

    print("ETL RAW → TRUSTED COMPLETADO.")

    spark.stop()


if __name__ == "__main__":
    main()
