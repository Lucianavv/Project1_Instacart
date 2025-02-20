import os
import mysql.connector
import snowflake.connector

# Credenciales de MySQL como variables de entorno
db_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("DATABASE_NAME"),
    "port": os.getenv("MYSQL_PORT"),
}


# Conectar a MySQL
def conectar_mysql():
    return mysql.connector.connect(**db_config)


# Configuración de conexión a Snowflake desde ~/.zshrc
def conectar_snowflake():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        database="INSTACART_DB",
        schema="RAW"
    )


# Crear base de datos y esquema RAW en Snowflake
def configurar_snowflake(conn_sf):
    cursor_sf = conn_sf.cursor()
    cursor_sf.execute("CREATE DATABASE IF NOT EXISTS INSTACART_DB")
    cursor_sf.execute("USE DATABASE INSTACART_DB")
    cursor_sf.execute("CREATE SCHEMA IF NOT EXISTS RAW")
    cursor_sf.execute("USE SCHEMA RAW")
    print("Base de datos y esquema 'RAW' en Snowflake listos.")


# Crear tablas en Snowflake en el esquema RAW
def crear_tablas_snowflake(conn_sf, conn_mysql):
    cursor_mysql = conn_mysql.cursor()
    cursor_sf = conn_sf.cursor()

    cursor_mysql.execute("SHOW TABLES")
    tablas = [t[0] for t in cursor_mysql.fetchall()]

    for tabla in tablas:
        cursor_mysql.execute(f"DESCRIBE {tabla}")
        columnas = cursor_mysql.fetchall()

        columnas_sf = []
        for col_name, col_type, *_ in columnas:
            if "int" in col_type:
                col_type_sf = "INTEGER"
            elif "float" in col_type or "double" in col_type:
                col_type_sf = "FLOAT"
            elif "datetime" in col_type:
                col_type_sf = "TIMESTAMP"
            else:
                col_type_sf = "STRING"

            columnas_sf.append(f"{col_name} {col_type_sf}")

        create_table_query = f"CREATE TABLE IF NOT EXISTS RAW.{tabla} ({', '.join(columnas_sf)})"
        cursor_sf.execute(create_table_query)
        print(f"Tabla '{tabla}' creada en Snowflake en el esquema RAW.")


# Insertar datos en Snowflake en batches
def insertar_datos_snowflake(conn_sf, conn_mysql, batch_size=1000):
    cursor_mysql = conn_mysql.cursor()
    cursor_sf = conn_sf.cursor()

    cursor_mysql.execute("SHOW TABLES")
    tablas = [t[0] for t in cursor_mysql.fetchall()]

    for tabla in tablas:
        cursor_mysql.execute(f"SELECT * FROM {tabla}")
        columnas = [desc[0] for desc in cursor_mysql.description]

        insert_query = f"INSERT INTO RAW.{tabla} ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(columnas))})"
        batch = []

        for fila in cursor_mysql:
            batch.append(fila)
            if len(batch) >= batch_size:
                cursor_sf.executemany(insert_query, batch)
                conn_sf.commit()
                batch = []

        if batch:
            cursor_sf.executemany(insert_query, batch)
            conn_sf.commit()

        print(f"Datos insertados en 'RAW.{tabla}' en batches de {batch_size} filas.")


# Verificar que las cantidades de registros coincidan
def verificar_integridad(conn_sf, conn_mysql):
    cursor_mysql = conn_mysql.cursor()
    cursor_sf = conn_sf.cursor()

    cursor_mysql.execute("SHOW TABLES")
    tablas = [t[0] for t in cursor_mysql.fetchall()]

    for tabla in tablas:
        cursor_mysql.execute(f"SELECT COUNT(*) FROM {tabla}")
        count_mysql = cursor_mysql.fetchone()[0]

        cursor_sf.execute(f"SELECT COUNT(*) FROM RAW.{tabla}")
        count_sf = cursor_sf.fetchone()[0]

        print(f"Tabla 'RAW.{tabla}': MySQL = {count_mysql}, Snowflake = {count_sf}")
        if count_mysql == count_sf:
            print("✅ Los registros coinciden.")
        else:
            print("⚠️ Diferencias detectadas.")


# Ejecutar la migración
if __name__ == "__main__":
    conn_mysql = conectar_mysql()
    conn_sf = conectar_snowflake()

    try:
        configurar_snowflake(conn_sf)
        crear_tablas_snowflake(conn_sf, conn_mysql)
        insertar_datos_snowflake(conn_sf, conn_mysql)
        verificar_integridad(conn_sf, conn_mysql)
    finally:
        conn_mysql.close()
        conn_sf.close()
        print("Conexiones cerradas.")