import sqlite3
import os
import ssl
import urllib.request
from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
import re
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser import MultifieldParser
from whoosh import scoring

#Evitamos problemas con SSL
if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
    ssl._create_default_https_context = ssl._create_unverified_context

def extraer_datos():
    url = "https://es.wikipedia.org/wiki/Anexo:Especies_en_peligro_de_extinci%C3%B3n_en_Espa%C3%B1a"
    try:
        f = urllib.request.urlopen(url)
        soup = BeautifulSoup(f, "lxml")
        #Obtenemos todas las tablas de la página
        tablas = soup.find_all("table", {"class": "wikitable"})

        if len(tablas) < 7:
            raise ValueError("No se encontraron suficientes tablas en la página")

        tabla_aves = tablas[5] #Seleccionamos la 6ta tabla (índice 5) ya que es la que contiene la información de las aves
        tabla_mamiferos = tablas[6] #Seleccionamos la 7a tabla (índice 6) ya que es la que contiene la información de los mamíferos
        datos_aves = extraer_datos_tabla(tabla_aves, "Ave")
        datos_mamiferos = extraer_datos_tabla(tabla_mamiferos, "Mamífero")
        return datos_aves + datos_mamiferos
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo extraer información de Wikipedia:\n{e}")
        return []

def extraer_datos_tabla(tabla, categoria):
    #Obtenemos todas las filas de la tabla dada y los clasifica por categoría
    filas = tabla.find_all("tr")[1:]  #Saltamos la cabecera
    datos = []
    for fila in filas:
        columnas = fila.find_all("td")

        nombre_cientifico = columnas[0].text.strip()
        nombre_comun = columnas[1].text.strip()

        if columnas[4].text.strip():
            poblacion_protegida = columnas[4].text.strip()
        else:
            poblacion_protegida = "Sin datos"

        enlace_animal = columnas[0].find("a")  #Buscamos el enlace a la página de la especie
        estado_conservacion, info = obtener_detalles(enlace_animal)

        datos.append((nombre_cientifico, nombre_comun, poblacion_protegida, estado_conservacion, info))
    return datos

#Función para obtener detalles extra de la ave desde su enlace en Wikipedia
def obtener_detalles(enlace):
    if enlace and "href" in enlace.attrs:
        url_animal = "https://es.wikipedia.org" + enlace["href"]
        try:
            f = urllib.request.urlopen(url_animal)
            soup = BeautifulSoup(f, "lxml")

            #Buscamos el estado de conservación en la tabla infobox
            estado_conservacion = "Desconocido"
            infobox = soup.find("table", {"class": "infobox"})
            if infobox:
                for fila in infobox.find_all("tr"):
                    if fila.th and "Estado de conservación" in fila.th.text:
                        trConInfo= fila.find_next_sibling("tr")
                        estado_conservacion = trConInfo.find("td").find("a")["title"].strip()
                        break

            #Obtenemos la descripción del ave (primer párrafo)
            info = "Sin información"
            parrafos = soup.find_all("p")
            for p in parrafos:
                texto = p.text.strip()
                if texto and not texto.startswith("La Wikipedia") and len(texto) > 50: #Filtramos párrafos cortos o que inicien con "La Wikipedia", evitamos así que aparezca info que no corresponde con lo que estamos buscando
                    info = re.sub(r'\[\d+\]', '', texto) #Eliminamos la posible referencia numérica
                    break
            return estado_conservacion, info
        except Exception as e:
            print(f"Error al obtener detalles de {url_animal}: {e}")
            return "Error", "No se pudo obtener la información"
    print(f"Datos extraídos: {enlace.text.strip()}")
    return "No disponible", "No hay enlace a Wikipedia"

def almacenar_bd():
    conn = sqlite3.connect('animales.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS ANIMALES")
    conn.execute('''CREATE TABLE ANIMALES (
        NOMBRE_CIENTIFICO TEXT NOT NULL,
        NOMBRE_COMUN TEXT NOT NULL,
        POBLACION_PROTEGIDA TEXT NOT NULL,
        ESTADO_CONSERVACION TEXT NOT NULL,
        INFO TEXT NOT NULL)''')
    
    datos = extraer_datos()

    #Verificación: Si no se obtienen datos, termina la función
    if not datos:
        print("No se pudieron extraer datos.")
        return

    for animal in datos:
        conn.execute("INSERT INTO ANIMALES VALUES (?, ?, ?, ?, ?)", animal)

    conn.commit()
    conn.close()

    #Creamos el índice automáticamente después de guardar los datos
    crear_indice()
    return "Base de datos creada correctamente"


def listar_bd():
    conn = sqlite3.connect('animales.db')
    cursor = conn.execute("SELECT * FROM ANIMALES")

    resultados = []
    for row in cursor:
        resultados.append({
            'nombre_cientifico': row[0],
            'nombre_comun': row[1],
            'poblacion_protegida': row[2],
            'estado_conservacion': row[3],
            'info': row[4]
        })
    conn.close()
    return resultados

def crear_indice():
    if not os.path.exists("indice"):
        os.mkdir("indice")
    schema = Schema(nombre_cientifico=TEXT(stored=True), nombre_comun=TEXT(stored=True),
                    poblacion_protegida=TEXT(stored=True), estado_conservacion=TEXT(stored=True), info=TEXT(stored=True))
    ix = create_in("indice", schema)
    writer = ix.writer()
    conn = sqlite3.connect('animales.db')
    cursor = conn.execute("SELECT * FROM ANIMALES")
    for row in cursor:
        writer.add_document(nombre_cientifico=row[0], nombre_comun=row[1],
                            poblacion_protegida=row[2], estado_conservacion=row[3], info=row[4])
    writer.commit()
    conn.close()
    

def buscar_animales(termino, estado=None, descripcion=False):
    ix = open_dir("indice")

    
    weighting = scoring.TF_IDF()
    with ix.searcher(weighting=weighting) as searcher:
        query = None
        if(termino):
            campos = ["info"] if descripcion else ["nombre_cientifico", "nombre_comun"]
            boosts = {"nombre_comun": 2.0, "nombre_cientifico": 1.5}
            parser = MultifieldParser(campos, schema=ix.schema, fieldboosts=boosts)
            query = parser.parse(termino)

        # Si hay filtro por estado, creamos la subquery y la combinamos con AND
        if estado:
            qp = MultifieldParser(["estado_conservacion"], schema=ix.schema)
            estado_query = qp.parse(estado)
            if query:
                query = query & estado_query
            else:
                query = estado_query
            print("query",query)


        # Si no se ha introducido ningún criterio, devolvemos aviso
        if not query:
            return "sinCriterio"

        whoosh_results = searcher.search(query, limit=None)
        print("Resultados de Whoosh:", whoosh_results)

        resultados = []
        for row in whoosh_results:
            resultados.append({
                'nombre_cientifico': row['nombre_cientifico'],
                'nombre_comun': row['nombre_comun'],
                'poblacion_protegida': row['poblacion_protegida'],
                'estado_conservacion': row['estado_conservacion'],
                'info': row['info']
            })

        return resultados