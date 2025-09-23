import pyodbc
from dotenv import load_dotenv
import os
from fastapi import Depends

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

server = os.getenv("MSSQL_SERVER_HOST")
database = os.getenv("MSSQL_SERVER_DB")


def get_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
            f"Encrypt=no;"
            f"TrustServerCertificate=yes;"
        )
        return conn
    except pyodbc.Error as e:
        print(f"DB connection failed: {e}")
        raise


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


# conn = get_connection()
# cursor = conn.cursor()
# cursor.execute("SELECT GETDATE()")
# row = cursor.fetchone()
# print("DB Connection successful! Server time:", row[0])
# cursor.close()
# conn.close()


