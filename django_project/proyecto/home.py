from scrapping import jAndalucia_v3, wikipedia_v3, observation_v3

def cargar_todos_los_datos():
    resultados = {}

    try:
        resultado_junta = jAndalucia_v3.almacenar_bd()
        resultados['ZEC_ZEPA'] = resultado_junta or "Error al cargar ZEC/ZEPA"
    except Exception as e:
        resultados['ZEC_ZEPA'] = f"Error: {str(e)}"

    try:
        resultado_wikipedia = wikipedia_v3.almacenar_bd()
        resultados['Wikipedia'] = resultado_wikipedia or "Error al cargar datos de Wikipedia"
    except Exception as e:
        resultados['Wikipedia'] = f"Error: {str(e)}"

    try:
        resultado_observaciones = observation_v3.almacenar_bd()
        resultados['Observaciones'] = resultado_observaciones or "Error al cargar Observaciones"
    except Exception as e:
        resultados['Observaciones'] = f"Error: {str(e)}"

    return resultados
