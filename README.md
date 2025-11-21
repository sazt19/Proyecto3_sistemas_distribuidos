# Proyecto 3 – Automatización de Ingesta, Procesamiento y Analítica de Datos COVID en AWS  
ST0263 – Tópicos Especiales en Telemática – 2025-2  
Universidad EAFIT  


## 1. Descripción General

Este proyecto implementa un **pipeline de datos completo (batch)** en AWS para capturar, almacenar, procesar y analizar datos relacionados con COVID en Colombia. La solución cubre todas las capas de un data lake moderno:

1. **Captura de datos**  
   - Datos COVID desde API pública (disease.sh).  
   - Datos relacionales desde MySQL en AWS RDS.

2. **Ingesta automática**  
   - Scripts Python ejecutados en AWS EC2.  
   - Datos enviados a S3 en la **zona RAW**.

3. **Procesamiento ETL**  
   - Spark ejecutado sobre un clúster EMR.  
   - Transformaciones y escritura de datos limpios a **zona TRUSTED**.

4. **Analítica (opcional)**  
   - Arquitectura lista para usar SparkSQL, DataFrames y SparkML.  
   - Resultados finales proyectados a la **zona REFINED**.

La solución cumple los requerimientos del proyecto institucional de AWS Data Engineering.

## 2. Arquitectura del Sistema

API COVID → EC2 (Python) → S3 Raw/covid_api

RDS MySQL → EC2 (Python) → S3 Raw/rds

S3 RAW → EMR Spark Steps → S3 TRUSTED

S3 TRUSTED → Spark SQL / Spark ML → S3 REFINED (Opcional)

S3 REFINED → Athena / API Gateway (Opcional)

Servicios utilizados:

- **AWS RDS (MySQL)**  
- **AWS S3 (Data Lake)**  
- **AWS EC2 (Nodo de ingesta)**  
- **AWS EMR (Spark Cluster)**  
- **IAM Roles**  
- **AWS Systems Manager (SSM) para EC2 sin llaves**  


## 3. Ingesta desde RDS → RAW

Archivo: `ingestion/export_rds_to_s3.py`

### Funcionalidad:
- Conectar al RDS MySQL.  
- Extraer todas las tablas del esquema.  
- Convertir resultados a CSV.  
- Subirlos automáticamente a:


s3://st0263-covid-sazu/raw/rds/<tabla>/<timestamp>.csv


### Ejecución:

```bash
python3 ingestion/export_rds_to_s3.py
````

Este script se ejecuta desde una EC2 con rol IAM que permite acceso total al bucket S3.

## 4. Ingesta desde API COVID → RAW

Archivo: `ingestion/download_covid_api.py`

API utilizada:

```
https://disease.sh/v3/covid-19/historical/Colombia?lastdays=all
```

### Funcionalidad:

* Descarga datos históricos de COVID.
* Guarda JSON sin procesar.
* Lo sube a:

```
s3://st0263-covid-sazu/raw/covid_api/<timestamp>.json
```

### Ejecución:

```bash
python3 ingestion/download_covid_api.py
```

## 5. ETL con Spark (RAW → TRUSTED)

Archivo: `etl_spark/etl_raw_to_trusted.py`

### Funciones principales:

* Lee datos RAW de:

  * JSON (API)
  * CSV (RDS)
* Transforma:

  * Aplanamiento de JSON.
  * Conversión de fechas.
  * Limpieza de columnas.
  * Uniones entre tablas relacionales.
* Escribe datos limpios en formato Parquet:

```
s3://st0263-covid-sazu/trusted/covid_timeseries/
s3://st0263-covid-sazu/trusted/hospital_departamento/
s3://st0263-covid-sazu/trusted/poblacion/
```

### Ejecución en EMR:

1. Subir script a S3:

   ```bash
   aws s3 cp etl_spark/etl_raw_to_trusted.py s3://<TU_BUCKET>/etl/
   ```

2. Crear un clúster EMR (Spark + Hadoop).

3. Agregar un Step:

   * Tipo: Spark
   * Script:

     ```
     s3://st0263-covid-sazu/etl/etl_raw_to_trusted.py
     ```
   * Deploy mode: `cluster`

## 6. Resultados en el Data Lake

### RAW

* `raw/covid_api/*.json`
* `raw/rds/<tabla>/*.csv`

### TRUSTED

* `trusted/covid_timeseries/*.parquet`
* `trusted/hospital_departamento/*.parquet`
* `trusted/poblacion/*.parquet`

### (Opcional) REFINED

* Resultados avanzados (Spark ML / agregados finales)

## 7. Reproducir Todo el Proyecto Desde Cero

### 1️⃣ Configurar RDS

* Crear instancia MySQL
* Crear tablas y cargar datos iniciales

### 2️⃣ Configurar EC2

* Asignar IAM Role con acceso S3
* Conectarse por **Session Manager**
* Instalar dependencias:

  ```bash
  sudo dnf install python3 git -y
  pip3 install boto3 pymysql pandas
  ```

### 3️⃣ Ingestar datos a RAW

```bash
python3 ingestion/export_rds_to_s3.py
python3 ingestion/download_covid_api.py
```

### 4️⃣ Crear clúster EMR

* Spark 3.x
* Hadoop 3.x
* Roles: EMR_DefaultRole, EC2-S3-Access-Role

### 5️⃣ Ejecutar ETL

Agregar Step en EMR:

```
spark-submit --deploy-mode cluster s3://st0263-covid-sazu/etl/etl_raw_to_trusted.py
```

### 6️⃣ Confirmar salida en TRUSTED

Revisar carpetas:

```
trusted/covid_timeseries
trusted/poblacion
trusted/hospital_departamento
```

## 8. Estructura del Repositorio

```
PROYECTO3_SISTEMAS_DISTRIBUIDOS/
│
├── analytics_spark/
│   └── analytics_covid.py            # Script Spark para análisis con EMR
│
├── api/
│   └── lambda_athena_query.py        # Lambda para ejecutar consultas en Athena
│
├── env/                              # Entorno virtual (NO se sube a GitHub)
│   ├── Include/
│   ├── Lib/
│   └── Scripts/
│
├── etl_spark/
│   ├── etl_covid_join.py             # Join final de tablas transformadas
│   └── etl_raw_to_trusted.py         # Limpieza y formateo de datos RAW → TRUSTED
│
├── infra/
│   (Aquí se documentan los recursos creados en AWS: RDS, EC2, EMR, roles IAM, etc.)
│
├── ingestion/
│   ├── download_covid_api.py         # Descarga datos de la API pública
│   ├── download_covid_files.py       # Descarga de archivos adicionales (si aplica)
│   └── export_rds_to_s3.py           # Exporta tablas de RDS hacia S3
│
├── download_covid_api.py             # Versión principal usada durante pruebas
│
├── .gitignore
│
└── README.md                         # Este documento

```

## 9. Datos del Estudiante

**Nombre:** Sara Zuluaga
**Curso:** ST0263 – Tópicos Especiales en Telemática
**Semestre:** 2025-2
**Universidad EAFIT**



