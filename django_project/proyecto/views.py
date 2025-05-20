from django.shortcuts import render
from scraping import jAndalucia_v3, wikipedia_v3, observation_v3
from .recommendations import recomendar_especies, recomendar_relacionadas, recomendar_espacios
from .home import cargar_todos_los_datos

def home(request):
    cargado = request.session.get('cargado', False)
    mensaje_resultados = None
    resultados = {}

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'cargar':
            resultados = cargar_todos_los_datos()
            cargado = True
            request.session['cargado'] = cargado
            mensaje_resultados = "Datos cargados correctamente."
            return render(request, 'index.html', {
                'cargado': cargado,
                'mensaje_resultados': mensaje_resultados,
                'resultados': resultados,
                'request': request
            })

        elif accion == 'resetear':
            request.session.pop('cargado', None)
            cargado = False
            mensaje_resultados = "Índices reseteados correctamente."
            return render(request, 'index.html', {
                'cargado': cargado,
                'mensaje_resultados': mensaje_resultados,
                'request': request
            })

    return render(request, 'index.html', {'cargado': cargado, 'request': request})

def page_1(request):
    resultados = []
    mensaje_resultados = ""
    cargado = request.session.get('cargado', False)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'listar':
            resultados = wikipedia_v3.listar_bd()
            print("Resultados:", resultados)
            return render(request, 'page_1.html', {'cargado': cargado, 'resultados': resultados, 'request': request})
        
        elif accion == 'buscar':
            nombre = request.POST.get('nombre', '').strip() if request.POST.get('nombre') != "" else None
            estado = request.POST.get('estado_conservacion')
            descripcion = request.POST.get('descripcion')
            resultados = []

            resultados = wikipedia_v3.buscar_animales(
                termino=nombre if nombre else '',
                estado=estado,
                descripcion=descripcion
            )

            if resultados == "sinCriterio":
                mensaje_resultados = "⚠️ No se ha introducido ningún criterio de búsqueda"
                resultados = []
            print("Resultados:", resultados)

            return render(request, 'page_1.html', {
                'cargado': cargado,
                'resultados': resultados,
                'mensaje_resultados': mensaje_resultados,
                'request': request,
            })
        
        elif accion == 'recomendar_relacionadas':
            nombre_recomendacion = request.POST.get("nombre", "").strip()
            resultados = []
            recomendaciones = []
            
            if nombre_recomendacion:
                recomendaciones = recomendar_relacionadas(nombre_recomendacion)
                if isinstance(recomendaciones, str):
                    mensaje_resultados = recomendaciones
                    recomendaciones = []
                else:
                    mensaje_resultados = f"Especies recomendadas en base a tu búsqueda en Wikipedia ({nombre_recomendacion}), encontradas en la base de datos de observaciones:"
            else:
                mensaje_resultados = "Debes introducir un nombre científico para obtener recomendaciones."
                recomendaciones = []
                resultados = []

            return render(request, 'page_1.html', {
                'resultados': resultados,
                'recomendaciones': recomendaciones,
                'mensaje_resultados': mensaje_resultados,
                'cargado': cargado,
            })

    return render(request, 'page_1.html', {'cargado': cargado,'request': request})

def page_2(request):
    resultados = []
    mensaje_resultados = ""
    cargado = request.session.get('cargado', False)

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'listar':
            resultados = jAndalucia_v3.listar_bd()
            return render(request, 'page_2.html', {'cargado': cargado, 'resultados': resultados, 'request': request})

        elif accion == 'buscar':
            print(request.POST)
            espacio = request.POST.get('espacio', '').strip() if request.POST.get('espacio') != "" else None
            min_sup = request.POST.get('min_sup') if request.POST.get('min_sup') != "" else None
            max_sup = request.POST.get('max_sup') if request.POST.get('max_sup') != "" else None
            ordenarPorSuperficie = request.POST.get('ordenarPorSuperficie')
            fuzzy_activo = request.POST.get('fuzzy')
            print(f"DEBUG -> espacio: {espacio}, min_sup: {min_sup}, max_sup: {max_sup}, fuzzy: {fuzzy_activo}, ordenar: {ordenarPorSuperficie}")
            resultados = []

            resultados = jAndalucia_v3.buscar_espacios_combinada(
                espacio=espacio,
                min_sup=min_sup,
                max_sup=max_sup,
                fuzzy=fuzzy_activo,
                ordenarPorSuperficie=ordenarPorSuperficie
            )

            if resultados=="sinCriterio":
                mensaje_resultados = "⚠️ No se ha introducido ningún criterio de búsqueda"
                resultados = []
            print("Resultados:", resultados)

            return render(request, 'page_2.html', {
                'cargado': cargado,
                'resultados': resultados,
                'mensaje_resultados': mensaje_resultados,
                'request': request,
            })
    
        elif accion == "recomendar_espacios":
            nombre_recomendacion = request.POST.get("nombre", "").strip()
            if nombre_recomendacion:
                recomendaciones = recomendar_espacios(nombre_recomendacion, top_n=5)
                if isinstance(recomendaciones, str):
                    mensaje_resultados = recomendaciones
                    recomendaciones = []
                else:
                    mensaje_resultados = f"Espacios recomendados relacionados con {nombre_recomendacion} (según superficie, plan en vigor y nombre similar):"
            else:
                mensaje_resultados = "Debes introducir el nombre de un espacio ZEC/ZEPA para recomendar."
                recomendaciones = []
                resultados = []

            return render(request, 'page_2.html', {
                'resultados': resultados,
                'recomendaciones': recomendaciones,
                'mensaje_resultados': mensaje_resultados,
                'cargado': cargado,
                'request': request
            })

    return render(request, 'page_2.html', {'cargado': cargado, 'request': request})

def page_3(request):
    resultados = []
    mensaje_resultados = ""
    cargado = request.session.get('cargado', False)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'listar':
            resultados = observation_v3.listar_bd()
            return render(request, 'page_3.html', {'cargado': cargado, 'resultados': resultados, 'request': request})

        elif accion == 'buscar':
            nombre = request.POST.get('nombre', '').strip() if request.POST.get('nombre') != "" else None
            fecha_primera = request.POST.get('fecha_primera', '').strip() if request.POST.get('fecha_primera') != "" else None
            fecha_ultima = request.POST.get('fecha_ultima', '').strip() if request.POST.get('fecha_ultima') != "" else None
            resultados = observation_v3.buscar_avanzado(
                nombre=nombre,
                fecha_primera=fecha_primera,
                fecha_ultima=fecha_ultima,
            )
            if resultados == "sin_criterio":
                mensaje_resultados = "⚠️ No se ha introducido ningún criterio de búsqueda"
                resultados = []
            if resultados == "formato_incorrecto":
                mensaje_resultados = "⚠️ Formato de fecha incorrecto"
                resultados = []
            print("Resultados:", resultados)

            return render(request, 'page_3.html', {
                'cargado': cargado,
                'resultados': resultados,
                'mensaje_resultados': mensaje_resultados,
            })

        elif accion == 'top_observaciones':
            resultados = observation_v3.especies_mas_observadas(limit=10)
            return render(request, 'page_3.html', {'cargado': cargado, 'resultados': resultados, 'request': request})
        
        elif accion == "recomendar_especies":
            nombre_recomendacion = request.POST.get("nombre", "").strip()
            if nombre_recomendacion:
                recomendaciones =  recomendar_especies(nombre_recomendacion, top_n=5)
                if isinstance(recomendaciones, str):
                    mensaje_resultados = recomendaciones
                    recomendaciones = []
                else:
                    mensaje_resultados = f"Especies recomendadas para {nombre_recomendacion} (teniendo en cuenta valores como rango de observaciones, fecha de su última observación y nombres similares): "
            else:
                mensaje_resultados = "Debes introducir un nombre de especie para recomendar."
                recomendaciones = []
                resultados = []

            return render(request, 'page_3.html', {
                'resultados': resultados,
                'recomendaciones': recomendaciones,
                'mensaje_resultados': mensaje_resultados,
                'cargado': cargado,
            })


    return render(request, 'page_3.html', {'cargado': cargado,'request': request})
