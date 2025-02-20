# 📌 Uso de Variables de Entorno en un Proyecto con Conda y Python

Las variables de entorno permiten almacenar información sensible, como nuestras credenciales de MySQL y Snowflake.
---
Utilizamos Conda para el manejo de entornos virtuales para evitar conflictos entre versiones de paquetes.

## 🔹 1. Definir Variables de Entorno en Conda

Para definir variables de entorno en Conda de forma permanente, sigue estos pasos:

### a) Activar el entorno virtual
```sh
conda activate tu_entorno
```

### b) Agregar variables de entorno
```sh
conda env config vars set DB_HOST="localhost" DB_USER="usuario" DB_PASSWORD="contraseña" DB_NAME="nombre_base"
```

### c) Aplicar los cambios
Desactiva y vuelve a activar el entorno para que las variables sean reconocidas:
```sh
conda deactivate
conda activate tu_entorno
```

### d) Verificar las variables
Para asegurarte de que las variables fueron guardadas correctamente, usa:
```sh
conda env config vars list
```

---

## 🔹 2. Usar las Variables en Python

Dentro de tu código Python, puedes acceder a las variables de entorno utilizando `os.getenv()`:

```python
import os

# Obtener las variables de entorno
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

print(db_config)  # Verificar que las variables se están leyendo correctamente
```

---

## 🔹 3. Eliminar Variables de Entorno en Conda
Si necesitas eliminar una variable de entorno en Conda, usa:
```sh
conda env config vars unset DB_PASSWORD
```
Para eliminar todas las variables configuradas:
```sh
conda env config vars unset DB_HOST DB_USER DB_PASSWORD DB_NAME
```

---

## 🔹 Para trabajar con los notebooks usar `.env`
Configuramos las variables globales usando un archivo `.env` con `python-dotenv`:

### a) Instalar `dotenv`
```sh
pip install python-dotenv
```

### b) Crear un archivo `.env` en el proyecto
```
DB_HOST=localhost
DB_USER=usuario
DB_PASSWORD=contraseña
DB_NAME=nombre_base
```

### c) Modificar el código para cargar las variables desde `.env`
```python
from dotenv import load_dotenv
import os

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}
```

---



