DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "port":"colocar el puerto" ,
    "password": "",
    "database": "inseguridad_alimentaria",
}

DB_SERVER_CONFIG = {
    key: value
    for key, value in DB_CONFIG.items()
    if key != "database"
}
