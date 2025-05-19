from datetime import datetime
from whoosh.index import open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import NumericRange

#-----Funciones de recomendación para la página de Wikipedia-----
def recomendar_relacionadas(nombre_especie, top_n=5, index_dir="indice_observaciones"):
    ix = open_dir(index_dir)

    with ix.searcher() as searcher:
        parser = MultifieldParser(["nombre_comun", "nombre_cientifico"], schema=ix.schema)
        query = parser.parse(nombre_especie)
        results = searcher.search(query, limit=1)

        recomendaciones = []
        especie_encontrada = None

        if results:
            especie_encontrada = results[0]
            recomendaciones.append({
                "nombre_comun": especie_encontrada['nombre_comun'],
                "nombre_cientifico": especie_encontrada['nombre_cientifico'],
                "observaciones": especie_encontrada['observaciones'],
                "fecha_ultima": especie_encontrada['fecha_ultima'],
                "motivo": "Coincidencia exacta"
            })

            genero_base = especie_encontrada['nombre_cientifico'].split()[0]
        else:
            genero_base = nombre_especie.split()[0]  #Si no hay match exacto, usamos el género

        #Buscamos especies relacionadas (mismo género o bien observadas)
        similitudes = []
        for hit in searcher.documents():
            if especie_encontrada and hit['nombre_cientifico'] == especie_encontrada['nombre_cientifico']:
                continue  #Saltamos si es la especie exacta ya añadida

            motivo = ""
            if hit['nombre_cientifico'].startswith(genero_base):
                motivo = f"Mismo género: {genero_base}"
            else:
                motivo = "Otras especies observadas"

            similitudes.append({
                "nombre_comun": hit['nombre_comun'],
                "nombre_cientifico": hit['nombre_cientifico'],
                "observaciones": hit['observaciones'],
                "fecha_ultima": hit['fecha_ultima'],
                "motivo": motivo
            })

        #Ordenamos primero por coincidencia de género, luego por observaciones y fecha reciente
        similitudes.sort(
            key=lambda x: (
                0 if x['motivo'].startswith("Mismo género") else 1,
                -x['observaciones'],
                datetime.strptime(x['fecha_ultima'], "%Y-%m-%d")
            )
        )

        #Añadimos las especies relacionadas al listado final (sin repetir especie exacta)
        for especie in similitudes:
            if len(recomendaciones) >= top_n:
                break
            recomendaciones.append(especie)

        if not recomendaciones:
            return f"No se encontraron especies relacionadas con {nombre_especie}"

        return recomendaciones
#-----Funciones de recomendación para la página de Junta de Andalucía-----
def recomendar_espacios(espacio, top_n=5, plan_vigor=None):
    ix = open_dir("indice")
    recomendaciones = []

    with ix.searcher() as searcher:
        #Buscamos el espacio inicial
        parser = QueryParser("espacio", ix.schema)
        query = parser.parse(espacio)

        results = searcher.search(query, limit=1)

        if not results:
            return []

        espacio_referencia = results[0]
        sup_ref = espacio_referencia['superficie_total']

        #Buscamos espacios con superficie similar (+/- 20%) y mismo plan_vigor si se especifica
        margen = sup_ref * 0.2
        rango_sup = NumericRange("superficie_total", sup_ref - margen, sup_ref + margen)

        #Filtro combinado si plan_vigor se especifica
        if plan_vigor:
            parser_vigor = QueryParser("plan_vigor", ix.schema)
            vigor_query = parser_vigor.parse(plan_vigor)
            query_final = rango_sup & vigor_query
        else:
            query_final = rango_sup

        resultados = searcher.search(query_final, limit=top_n + 1)

        for r in resultados:
            if r['espacio'] != espacio_referencia['espacio']:  #Evitamos recomendar el mismo
                recomendaciones.append({
                    'nombre': r['espacio'],
                    'superficie_total': r['superficie_total'],
                    'declaracion_zec': r['declaracion_zec'],
                    'declaracion_zepa': r['declaracion_zepa'],
                    'plan_vigor': r['plan_vigor'],
                })

    return recomendaciones

#-----Funciones de recomendación para la página de Observaciones-----
def recomendar_especies(nombre_especie, top_n=5, index_dir="indice_observaciones"):
    ix = open_dir(index_dir)

    with ix.searcher() as searcher:
        #Buscamos la especie base
        parser = MultifieldParser(["nombre_comun", "nombre_cientifico"], schema=ix.schema)
        query = parser.parse(nombre_especie)
        results = searcher.search(query, limit=1)

        if not results:
            return f"No se encontró la especie {nombre_especie}"

        especie_base = results[0]
        observaciones_base = especie_base['observaciones']
        fecha_ultima_base = especie_base['fecha_ultima']

        fecha_ultima_base_dt = datetime.strptime(fecha_ultima_base, "%Y-%m-%d").date()

        #Comparamos con las demás especies
        similitudes = []
        for hit in searcher.documents():
            if hit['nombre_comun'] == especie_base['nombre_comun']:
                continue  #Saltamos la misma especie

            fecha_ultima_hit = datetime.strptime(hit['fecha_ultima'], "%Y-%m-%d").date()

            #Métrica simple: diferencia de observaciones y cercanía en fecha_ultima
            diff_obs = abs(hit['observaciones'] - observaciones_base)
            diff_fecha = abs((fecha_ultima_hit - fecha_ultima_base_dt).days)

            score = diff_obs + diff_fecha  #A menor score, más similar
            similitudes.append({
                "nombre_comun": hit['nombre_comun'],
                "nombre_cientifico": hit['nombre_cientifico'],
                "observaciones": hit['observaciones'],
                "fecha_ultima": hit['fecha_ultima'],
                "score": score
            })

        similitudes.sort(key=lambda x: x['score'])
        return similitudes[:top_n]