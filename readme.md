# AnalizandoLasElecciones
La idea del proyecto es por un lado tener un script que recorra la pagina oficial de las elecciones de Argentina (http://www.resultados.gob.ar/escrutinio/dat99/DDN99999P.htm) y guardar todos esos datos de una forma mas conveniente
Por otro lado, es generar, a partir de esta informacion, datos de interes, como por ejemplo extrapolar la informacion actual, en donde no fueron escrutadas la totalidad de las mesas, partiendo de la suposicion de que las mesas que faltan escrutar en una ciudad, se comportan de la misma forma que la totalidad de las mesas ya escrutadas de esa ciudad. De esta forma, hacemos una estimacion de como podria dar el escrutinio cuando todas las mesas sean escrutadas.
Los codigos fuentes los voy a subir en cuanto los acomode un poco, asi pueden utilizarlos como ustedes quieran. Por lo pronto subo los datos en crudo para que el que quiera pueda jugar con ellos. Estos estan guardados en una estructura en python con la siguiente forma:

	datos = {
		'provincia1': {
			'Senadores Nacionales': Secciones_y_municipios(
				'secciones': {
					'seccion1': Info_seccion_municipio(
						'info_general': Info_general(
							'mesas_totales': int,
							'mesas_escrutadas': int,
							'votos_emitidos': int,
							'votos_no_emitidos': int,
							'votos_en_blanco': int,
							'votos_nulos': int,
							'votos_rec_imp_com': int
						),
						'info_por_partido': {
							'partido1': Info_partido(
								'votos_totales': int,
								'listas': {
									'lista1_votos': int,
									... (otras listas)
								}
							),
							... (otros partidos)
						}
					),
					... (otras secciones)
				}, 
				'municipios': {
					'municipio1': Info_seccion_municipio(
						... (misma info que para secciones)
					),
					... (otros municipios)
				}
			),
			... (diputados nac, diputados prov)
		},
		... (otras provincias)
	}

Aclaracion: {} es un diccionario y lo que empieza en mayusculas y tiene () es una namedtuple

Esta estructura con todos los datos fue guardada en un archivo utilizando el modulo pickle. Para poder utilizarla dentro de un codigo de python, se puede utilizar el siguiente metodo:

	def load_obj_from_file(name):
	    with open('data/' + name + '.pkl', 'rb') as f:
	        return pickle.load(f)
