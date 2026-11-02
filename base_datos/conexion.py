import mysql.connector

def conectar():

    conexion = mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="",
        database="biblioteca_leon"
    )
    return conexion
