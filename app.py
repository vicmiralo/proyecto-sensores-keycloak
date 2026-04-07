from fastapi import FastAPI
import psycopg2
# import os
import socket

app = FastAPI()

# Configuración de conexión
def get_db_connection():
    return psycopg2.connect(
        host="db-sensores",
        database="sensores_db",
        user="admin",
        password="password123"
    )

@app.get("/sensor/{tipo}")
def leer_sensor(tipo: str):
    nodo_id = socket.gethostname() 
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, valor, unidad FROM lectura_sensores WHERE nombre ILIKE %s LIMIT 1;", (f'%{tipo}%',))
        dato = cur.fetchone()
        cur.close()
        conn.close()
        
        if dato:
            return {
                "sensor": dato[0],
                "valor": dato[1],
                "unidad": dato[2],
                "respondido_por_nodo": nodo_id
            }
        return {"error": "No encontrado", "nodo": nodo_id}
    except Exception as e:
        return {"error": str(e), "nodo": nodo_id}

@app.get("/estado")
def leer_estado():
    nodo_id = socket.gethostname()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT componente, estatus FROM sistema_estado LIMIT 1;")
        dato = cur.fetchone()
        cur.close()
        conn.close()
        
        if dato:
            return {
                "sistema": dato[0],
                "estatus": dato[1],
                "nodo_que_responde": nodo_id,
                "fuente": "PostgreSQL"
            }
        return {"error": "No hay datos de estado", "nodo": nodo_id}
    except Exception as e:
        return {"error": str(e), "nodo": nodo_id}
    
@app.get("/health")
def health_check():
    # Muy útil para que WSO2 sepa qué instancia específica está saludable
    return {
        "status": "operativo", 
        "database": "conectada", 
        "nodo": socket.gethostname()
    }

@app.get("/puesto-seguro")
def leer_puesto():
    nodo_id = socket.gethostname()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT puesto, nivel FROM puesto_seguro LIMIT 1;") # <--- Nombre
        fila = cur.fetchone()
        cur.close()
        conn.close()
        
        if fila:
            return {
                "Puesto": fila[0],
                "Nivel": fila[1],
                "Estado": "Monitorizado",
                "respondido_por_nodo": nodo_id
            }
        return {"error": "No hay datos en la tabla", "nodo": nodo_id}
    except Exception as e:
        return {"error": str(e), "nodo": nodo_id}