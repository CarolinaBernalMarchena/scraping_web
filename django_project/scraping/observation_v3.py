import sqlite3
import os
import ssl
import urllib.request
from bs4 import BeautifulSoup
from whoosh.fields import Schema, TEXT, DATETIME, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.query import And

#Evitamos problemas con SSL
if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_datos(url):
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, "lxml")

    tabla = soup.find_all("table", {"class": "table table-condensed stupid-table"})
    if not tabla:
        print("No se encontró la tabla esperada.")
        return []

    tabla_util = tabla[0]
    filas = tabla_util.find_all("tr")[1:]

    if not filas:
        print("No se encontraron filas en la tabla.")
        return []

    datos_observaciones = []

    for fila in filas:
        columnas = fila.find_all("td")
        nombre_comun = columnas[1].text.strip()
        nombre_cientifico = columnas[2].text.strip()
        fecha_primera = columnas[3].text.strip()
        fecha_ultima = columnas[4].text.strip()
        observaciones = columnas[5].text.strip()
        individuos = columnas[6].text.strip()

        datos_observaciones.append((nombre_comun, nombre_cientifico, fecha_primera, fecha_ultima, observaciones, individuos))

    print(f"Datos extraídos: {datos_observaciones}")

    return datos_observaciones


def almacenar_bd():
    urls = [
        "https://observation.org/locations/140575/species/?species_group_id=1&start_date=&end_date=&filter_month=&filter_year=",
        "https://observation.org/locations/140575/species/?species_group_id=2&start_date=&end_date=&filter_month=&filter_year="
    ]

    all_data = []
    for url in urls:
        datos = extraer_datos(url)
        all_data.extend(datos)

    if not all_data:
        print("No se pudieron extraer datos de ninguna página.")
        return

    conn = sqlite3.connect('observaciones.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS OBSERVACIONES")
    conn.execute('''CREATE TABLE OBSERVACIONES
       (NOMBRE_COMUN TEXT NOT NULL,
       NOMBRE_CIENTIFICO TEXT NOT NULL,
       FECHA_PRIMERA DATE NOT NULL,
       FECHA_ULTIMA DATE NOT NULL,
       OBSERVACIONES INTEGER NOT NULL,
       INDIVIDUOS INTEGER NOT NULL);''')

    for fila in all_data:
        nombre_comun = fila[0]
        nombre_cientifico = fila[1]
        fecha_primera = fila[2]
        fecha_ultima = fila[3]
        observaciones = int(fila[4].replace(',', ''))
        individuos = int(fila[5].replace(',', ''))
        conn.execute("INSERT INTO OBSERVACIONES VALUES (?, ?, ?, ?, ?, ?)",
                    (nombre_comun, nombre_cientifico, fecha_primera, fecha_ultima, observaciones, individuos))
    conn.commit()
    conn.close()
    crear_indice()

def listar_bd():
    conn = sqlite3.connect('observaciones.db')
    cursor = conn.execute("SELECT * FROM OBSERVACIONES")

    resultados = []
    for row in cursor:
        resultados.append({
            'nombre_comun': row[0],
            'nombre_cientifico': row[1],
            'fecha_primera': row[2],
            'fecha_ultima': row[3],
            'observaciones': row[4],
            'individuos': row[5]
        })
    conn.close()
    return resultados

def crear_indice():
    if not os.path.exists("indice_observaciones"):
        os.mkdir("indice_observaciones")
    schema = Schema(nombre_comun=TEXT(stored=True), nombre_cientifico=TEXT(stored=True), fecha_primera=DATETIME(stored=True),
                    fecha_ultima=DATETIME(stored=True), observaciones=NUMERIC(stored=True), individuos=NUMERIC(stored=True))
    ix = create_in("indice_observaciones", schema)
    writer = ix.writer()
    conn = sqlite3.connect('observaciones.db')
    cursor = conn.execute("SELECT * FROM OBSERVACIONES")
    for row in cursor:
        writer.add_document(nombre_comun=row[0], nombre_cientifico=row[1],
                            fecha_primera=row[2], fecha_ultima=row[3], observaciones=row[4], individuos=row[5])
        print("indice_observaciones", row)

    writer.commit()
    conn.close()

#---------- Búsquedas avanzada con whoosh ----------
def buscar_avanzado(nombre=None, fecha_primera=None, fecha_ultima=None, index_dir="indice_observaciones"):
    ix = open_dir(index_dir)
    print("fecha_primera", fecha_primera)
    with ix.searcher() as searcher:
        query = None

        #Buscarmos por nombre en nombre_comun o nombre_cientifico
        if nombre:
            campos = ["nombre_cientifico", "nombre_comun"]
            boosts = {"nombre_comun": 2.0, "nombre_cientifico": 1.5}
            parser = MultifieldParser(campos, schema=ix.schema, fieldboosts=boosts)
            query = parser.parse(nombre)

        #Buscamos por fecha_primera y fecha_ultima
        if fecha_primera or fecha_ultima:
            qp = QueryParser("fecha_primera", ix.schema)
            qp.add_plugin(DateParserPlugin())
            try:
                fecha_primera_formatted = fecha_primera.replace("-", "") if fecha_primera else None
                fecha_ultima_formatted = fecha_ultima.replace("-", "") if fecha_ultima else None
                if fecha_primera_formatted and len(fecha_primera_formatted) != 8:
                    raise ValueError("Formato de fecha incorrecto")
                if fecha_primera_formatted and fecha_ultima_formatted == None:
                    if query:
                        query = query & qp.parse(f"fecha_primera:[{fecha_primera_formatted} to now]")
                    else:
                        query = qp.parse(f"fecha_primera:[{fecha_primera_formatted} to now]")

                if fecha_ultima_formatted and len(fecha_ultima_formatted) != 8:
                    raise ValueError("Formato de fecha incorrecto")
                if fecha_ultima_formatted and fecha_primera_formatted == None:
                    if query:
                        query = query & qp.parse(f"fecha_ultima:[00010101 to {fecha_ultima_formatted}]")
                    else:
                        query = qp.parse(f"fecha_ultima:[00010101 to {fecha_ultima_formatted}]")

                if fecha_primera_formatted and fecha_ultima_formatted:
                    if query:
                        query = query & qp.parse(f"fecha_primera:[{fecha_primera_formatted} to now]") & qp.parse(f"fecha_ultima:[00010101 to {fecha_ultima_formatted}]")
                    else:
                        query = qp.parse(f"fecha_primera:[{fecha_primera_formatted} to now]") & qp.parse(f"fecha_ultima:[00010101 to {fecha_ultima_formatted}]")

            except:
                return "formato_incorrecto"

        #Si no se ha introducido ningún criterio, devolvemos aviso'''
        if not query:
            return "sin_criterio"

        #Ejecutamos la búsqueda
        whoosh_results = searcher.search(query, limit=None)
        print("whoosh_results:", whoosh_results)

        #Convertimos los resultados en una lista de diccionarios
        resultados = []
        for row in whoosh_results:
            try:
             resultados.append({
                    'nombre_comun': row['nombre_comun'],
                    'nombre_cientifico': row['nombre_cientifico'],
                    'observaciones': row['observaciones'],
                    'fecha_primera': row['fecha_primera'],
                    'fecha_ultima': row['fecha_ultima'],
                    'individuos': row['individuos']
                })
            except Exception as e:
                print(f"Error procesando fila: {e}")

        return resultados if resultados else []

def especies_mas_observadas(limit=10):
    ix = open_dir("indice_observaciones")

    with ix.searcher() as searcher:
        especies = []
        for hit in searcher.documents():

            especies.append({
                "nombre_comun": hit.get("nombre_comun", ""),
                "nombre_cientifico": hit.get("nombre_cientifico", ""),
                "fecha_primera": hit.get("fecha_primera", ""),
                "fecha_ultima": hit.get("fecha_ultima", ""),
                "observaciones": hit.get("observaciones", 0),
                "individuos": hit.get("individuos", 0)
            })

        #Ordenamos por número de observaciones descendente
        especies.sort(key=lambda x: x["observaciones"], reverse=True)

        return especies[:limit]