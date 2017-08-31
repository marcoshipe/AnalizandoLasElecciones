import pickle
import locale
from locale import LC_NUMERIC, atof, atoi
from collections import namedtuple
from selenium import webdriver

Secciones_y_municipios = namedtuple('Secciones_y_municipios', ['secciones', 'municipios'])
Info_seccion_municipio = namedtuple('Info_seccion_municipio', ['info_general', 'info_por_partido'])
Info_general = namedtuple('Info_general', ['mesas_totales', 'mesas_escrutadas', 'votos_emitidos', 'votos_no_emitidos',
                                           'votos_en_blanco', 'votos_nulos', 'votos_rec_imp_com'])
Info_partido = namedtuple('Info_partido', ['votos_totales', 'listas'])


def obtener_datos_completos(file_name):
    locale.setlocale(LC_NUMERIC, 'es_AR.utf8')
    datos = {}
    driver = webdriver.Firefox()
    driver.get('http://www.resultados.gob.ar/escrutinio/dat99/DDN99999P.htm')
    assert 'Elecciones Argentinas del 13 de agosto - Diputados Nacionales' in driver.title

    # iterate over all provincias
    provincias_links = []
    for provincia_elem in driver.find_elements_by_css_selector('#interiorindicesmunicipios > .indices > li'):
        for a_elem in provincia_elem.find_elements_by_css_selector('a'):
            if a_elem.value_of_css_property('display') != 'none':
                datos[a_elem.text] = {}
                provincias_links.append(a_elem.get_attribute('href'))
    for provincia_link in provincias_links:
        driver.get(provincia_link)
        por_cada_provincia(driver, datos)

    save_obj_to_file(datos, file_name)
    driver.close()


def por_cada_provincia(driver, datos):
    # iterate over all municipios
    municipios_links = []
    for municipio_a_elem in driver.find_elements_by_css_selector('#interiorindicesmunicipios > ul > .act > .municipios '
                                                                 '> ul > li > a'):
        municipios_links.append(municipio_a_elem.get_attribute('href'))
    for municipio_link in municipios_links:
        driver.get(municipio_link)
        por_cada_ciudad(driver, datos)


def por_cada_ciudad(driver, datos):
    categorias_link = []
    (provincia, municipio) = driver.find_element_by_css_selector('#ambito > div > p').text.split(' - ')
    for categoria_a_elem in driver.find_elements_by_css_selector('#menubotones > ul > li > a'):
        categorias_link.append(categoria_a_elem.get_attribute('href'))
    for categoria_link in categorias_link:
        driver.get(categoria_link)
        # La categoria la trae como uppercase por una prop del css
        categoria = driver.find_element_by_css_selector('#titulo > p').text
        if categoria not in datos[provincia]:
            datos[provincia][categoria] = Secciones_y_municipios(secciones={}, municipios={})
        seccion_municipio_item = get_data_ciudad(driver)
        if municipio.startswith('Sección'):
            datos[provincia][categoria].secciones[municipio] = seccion_municipio_item
        else:
            datos[provincia][categoria].municipios[municipio] = seccion_municipio_item


def get_data_ciudad(driver):
    # info_general = {}
    for mesa_elem in driver.find_elements_by_css_selector('.mesasEscrutadas > p'):
        if mesa_elem.text.startswith('Mesas totales: '):
            mesas_totales = atoi(mesa_elem.text.split(' ')[2])
        elif mesa_elem.text.startswith('Mesas escrutadas: '):
            mesas_escrutadas = atoi(mesa_elem.text.split(' ')[2])
    votos_emitidos = atoi(driver.find_element_by_css_selector('#tablavotos > tbody > .electores > .vot').text)
    for participacion_elem in driver.find_elements_by_css_selector('.participacion > p'):
        if participacion_elem.text.startswith('Participación sobre escrutado:'):
            porcentaje_votos_emitidos = atof(participacion_elem.text.split(' ')[3][:-1])/100
            porcentaje_votos_no_emitidos = 1-porcentaje_votos_emitidos
            votos_no_emitidos = round(porcentaje_votos_no_emitidos*votos_emitidos/porcentaje_votos_emitidos)
    votos_en_blanco = atoi(driver.find_element_by_css_selector('#tablavotos > tbody > .blan > .vot').text)
    votos_nulos = atoi(driver.find_element_by_css_selector('#tablavotos > tbody > .nulos > .vot').text)
    votos_rec_imp_com = atoi(driver.find_element_by_css_selector('#tablavotos > tbody > .recimp > .vot').text)
    info_general = Info_general(mesas_totales=mesas_totales, mesas_escrutadas=mesas_escrutadas,
                                votos_emitidos=votos_emitidos, votos_no_emitidos=votos_no_emitidos,
                                votos_en_blanco=votos_en_blanco, votos_nulos=votos_nulos,
                                votos_rec_imp_com=votos_rec_imp_com)

    info_por_partido = {}
    listas_partido_actual = None
    for agrup_elem in driver.find_elements_by_css_selector('#tablaagrupaciones > tbody > tr'):
        nombre_partido_lista = agrup_elem.find_element_by_css_selector('.denom').text
        votos_partido_lista = atoi(agrup_elem.find_element_by_css_selector('.vot').text)
        if 'agrup' in agrup_elem.get_attribute('class'):
            # Info de un partido:
            info_partido_actual = Info_partido(votos_totales=votos_partido_lista, listas={})
            info_por_partido[nombre_partido_lista] = info_partido_actual
            listas_partido_actual = info_partido_actual.listas
        elif 'lista' in agrup_elem.get_attribute('class'):
            listas_partido_actual[nombre_partido_lista] = votos_partido_lista

    return Info_seccion_municipio(info_general=info_general, info_por_partido=info_por_partido)


def save_obj_to_file(obj, file_name):
    with open('data/' + file_name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    obtener_datos_completos('datos_pais_elecciones_paso_2017_final_aux')
