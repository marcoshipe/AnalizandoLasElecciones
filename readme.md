# AnalizandoLasElecciones
La idea del proyecto es por un lado tener un script que recorra la página oficial de las elecciones de Argentina (http://www.resultados.gob.ar/escrutinio/dat99/DDN99999P.htm) y guardar todos esos datos de una forma más conveniente para su análisis.

Por otro lado la idea  es generar, a partir de esta información, datos de interés, como por ejemplo extrapolar la información actual, en donde no fueron escrutadas la totalidad de las mesas, partiendo de la suposición de que las mesas que faltan escrutar en una ciudad, se comportan de la misma forma que la totalidad de las mesas ya escrutadas de esa ciudad. De esta forma, hacemos una estimación de cómo podría dar el escrutinio cuando todas las mesas sean escrutadas.

Ya subí el código del script para obtener los datos, el próximo paso es hacer que obtenga los datos en un menor tiempo (el actual es 4/5 min aprox), quizás usando hilos, así se pueden obtener todos los datos provisorios (que se actualizan cada 5 min) para las elecciones generales.

Próximamente voy a subir el script donde analizo un poco los datos, así pueden usarlo de ejemplo para hacer sus propios análisis.

Los datos fueron exportados en formato json así pueden ser analizados con cualquier lenguaje de programación y no solo con el lenguaje con el que fueron obtenidos (Python). La estructura de los datos es la siguiente:

    {
        'provincia1': {
            'categoria1':{
                'municipios': {
                    'municipio1': {
                        'fecha_hora1': {
                            'info_general': {
                                'mesas_totales': int,
                                'mesas_escrutadas': int,
                                'votos_emitidos': int,
                                'votos_no_emitidos': int,
                                'votos_en_blanco': int,
                                'votos_nulos': int,
                                'votos_rec_imp_com': int
                            },
                            'info_por_partido': {
                                'partido1': {
                                    'votos_totales': int,
                                    'listas': {
                                        'lista1_votos': int,
                                        ... (otras listas)
                                    }
                                },
                                ... (otros partidos)
                            }
                        },
                        ... (otras fecha_hora, que representa de cuando es el dato provicional obtenido)
                            (formato de fecha_hora (iso 8601): aaaa-mm-ddThh:mm:ss, ej 2017-08-14T01:30:00)
                    },
                    ... (otros municipios)
                },
                'secciones': {
                    'seccion1': {
                        ... (misma info que para municipios)
                    },
                    ... (otras secciones)
                }
            },
            ... (otras categorias. ej: diputados nac, diputados prov)
        },
        ... (otras provincias)
    }

Para poder cargar el json desde Python, se puede utilizar el siguiente método:

    def load_data_from_json_file():
        with open('data/' + file_name + '.json', 'r') as f:
            return json.load(f)

El cual retorna toda la estructura como un diccionario de diccionarios de diccionarios...