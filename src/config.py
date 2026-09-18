DB_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "port": "colocar el puerto de la base de datos", 
    "password": "colocar la contraseña de la base de datos",
    "database": "inseguridad_alimentaria",
}

DB_SERVER_CONFIG = {
    key: value
    for key, value in DB_CONFIG.items()
    if key != "database"
}
