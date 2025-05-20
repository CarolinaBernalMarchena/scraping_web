import sqlite3
import ssl
from bs4 import BeautifulSoup
import re
import urllib
from whoosh.fields import Schema, TEXT, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, FuzzyTermPlugin
from whoosh.query import NumericRange
import os

#Evitamos problemas con SSL
if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
    ssl._create_default_https_context = ssl._create_unverified_context

def limpiar_estado(texto):
    #Quitar ESXXXXXXX (7 números después de "ES")
    texto = re.sub(r'ES\d{7}\s*', '', texto)
    
    #Quitar "(Pdf, X.XX MB)" o "(Pdf, X.XX MB)"
    texto = re.sub(r'\(Pdf, \d+\.\d{1,2} MB\)', '', texto)

     #Quitar "(***)", "(**)", "(*)" si aparecen después del nombre
    texto = re.sub(r'\s*\(\*+\)', '', texto)

    #Quitar cualquier cantidad de asteriscos (*) si aparecen solos después del nombre
    texto = re.sub(r'\s*\*+', '', texto)

    return texto.strip()

def limpiar_celda(texto):
    #""" Limpia el texto de una celda y reemplaza '-' por 'Sin datos'. """
    texto = texto.strip()
    return "Sin datos" if texto == "-" else texto

def extraer_datos():
    url = "https://www.juntadeandalucia.es/medioambiente/portal/areas-tematicas/espacios-protegidos/espacios-protegidos-red-natura-2000/relacion-espacios-protegidos-red-natura-2000-zec-zepa"
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f, "lxml")

    #Obtenemos todas las tablas de la página
    tabla = soup.find_all("table", {"summary": "Relacion de ZEC y ZEPAS"})
    
    #Verificamos si se encuentra la tabla
    if not tabla:
        print("No se encontró la tabla esperada.")
        return []  # Retorna una lista vacía si no se encuentra la tabla
    
    #Tomamos la primera tabla (en caso de haber más de una)
    filas = tabla[0].find_all("tr")  # Buscamos todas las filas <tr> dentro de la tabla

    #Verificamos si se encontraron filas
    if not filas:
        print("No se encontraron filas en la tabla.")
        return []  # Retorna una lista vacía si no se encuentran filas

    datos_zepa_zec = []

    #Recorremos todas las filas para extraer los datos
    for fila in filas:
        columnas = fila.find_all("td")
        
        #Si la fila tiene menos de 8 columnas, la ignoramos
        if len(columnas) < 8:
            continue  #Saltamos la fila si no tiene las columnas esperadas

        #Limpiamos y obtenemos los datos de las celdas
        espacio = limpiar_estado(columnas[0].text.strip())  #Aplica la limpieza al nombre
        superficie_texto = columnas[2].text.strip().replace(".", "").replace(",", ".")
        
        try:
            superficie_total = float(superficie_texto) if superficie_texto else 0.0
        except ValueError:
            superficie_total = 0.0

        #Usamos la función limpiar_celda() para normalizar los valores
        declaracion_zec = limpiar_celda(columnas[3].text)
        declaracion_zepa = limpiar_celda(columnas[5].text)
        plan_vigor = limpiar_celda(columnas[7].text)

        #Añadimos los datos a la lista
        datos_zepa_zec.append((espacio, superficie_total, declaracion_zec, declaracion_zepa, plan_vigor))
    return datos_zepa_zec

def almacenar_bd():
   
    conn = sqlite3.connect('zec_zepa.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS ZEC_ZEPA")
    conn.execute('''CREATE TABLE ZEC_ZEPA
       (ESPACIO TEXT NOT NULL,
       SUPERFICIE_TOTAL FLOAT NOT NULL,
       DECLARACION_ZEC TEXT NOT NULL,
       DECLARACION_ZEPA TEXT NOT NULL,
       PLAN_VIGOR TEXT NOT NULL);''')

    datos_zec_zepa = extraer_datos()

    #Verificación: Si no se obtienen datos, termina la función
    if not datos_zec_zepa:
        print("No se pudieron extraer datos.")
        return

    for zec_zepa in datos_zec_zepa:
        conn.execute("INSERT INTO ZEC_ZEPA VALUES (?, ?, ?, ?, ?)", zec_zepa)

    conn.commit()
    conn.close()

    #Creamos el índice automáticamente después de guardar los datos
    crear_indice()
    return "Base de datos creada correctamente"

def listar_bd():
    conn = sqlite3.connect('zec_zepa.db')
    cursor = conn.execute("SELECT * FROM ZEC_ZEPA")

    resultados = []
    for row in cursor:
        resultados.append({
            'espacio': row[0],
            'superficie_total': row[1],
            'declaracion_zec': row[2],
            'declaracion_zepa': row[3],
            'plan_vigor': row[4],
        })
    conn.close()
    return resultados

def crear_indice():
    if not os.path.exists("indiceAndalucia"):
        os.mkdir("indiceAndalucia")
    schema = Schema(espacio=TEXT(stored=True), superficie_total=NUMERIC(stored=True, decimal_places=2),
                    declaracion_zec=TEXT(stored=True), declaracion_zepa=TEXT(stored=True), plan_vigor=TEXT(stored=True))
    ix = create_in("indiceAndalucia", schema)
    writer = ix.writer()
    conn = sqlite3.connect('zec_zepa.db')
    cursor = conn.execute("SELECT * FROM ZEC_ZEPA")
    for row in cursor:
        writer.add_document(espacio=row[0], superficie_total=row[1],
                            declaracion_zec=row[2], declaracion_zepa=row[3], plan_vigor=row[4])
    writer.commit()
    conn.close()

#---------Función de búsqueda avanzada---------
def buscar_espacios_combinada(espacio=None, min_sup=None, max_sup=None, fuzzy=False,ordenarPorSuperficie=False):
    resultados = []
    ix = open_dir("indiceAndalucia")
    print(f"Espacio: {espacio}, Min: {min_sup}, Max: {max_sup}, Fuzzy: {fuzzy}")
    with ix.searcher() as searcher:
        query = None

        #Filtro por nombre (fuzzy search)
        if espacio:
            parser = QueryParser("espacio", ix.schema)
            if fuzzy:
                parser.add_plugin(FuzzyTermPlugin())  #Activa fuzzy si es True
                query = parser.parse(f"{espacio}~1")  #Permitirmos 1 error de escritura
            else:
                query = parser.parse(espacio)

        #Filtro por rango de superficie
        if min_sup is not None or max_sup is not None:
            try:
                min_sup = float(min_sup) if min_sup is not None else None
                max_sup = float(max_sup) if max_sup is not None else None
                print(f"Min: {min_sup}, Max: {max_sup}")
            except ValueError:
                raise ValueError("Los parámetros min_sup y max_sup deben ser números válidos.")
            superficie_query = NumericRange("superficie_total", min_sup, max_sup)
            if query:
                query = query & superficie_query
            else:
                query = superficie_query

        #Si no se especifica ningún filtro, se busca todo
        if not query:
            return "sinCriterio"
        print(f"Query: {query}")
        if ordenarPorSuperficie:
            results = searcher.search(query, sortedby="superficie_total", reverse=True, limit=None)
        else:
            results = searcher.search(query, sortedby="espacio", reverse=True, limit=None)

        for r in results:
            resultados.append({
                'espacio': r['espacio'],
                'superficie_total': r['superficie_total'],
                'declaracion_zec': r['declaracion_zec'],
                'declaracion_zepa': r['declaracion_zepa'],
                'plan_vigor': r['plan_vigor'],
            })

    return resultados