import locale
from locale import atof, atoi
import datetime
from lxml import html
import json
from jsoncomment import JsonComment
import requests

year = 2017
file_name = 'PASO_2017_ultimo_provisorio'


def main():
    locale.setlocale(locale.LC_NUMERIC, 'es_AR.utf8')  # used to convert string to int or float correctly
    data = {}
    main_url = 'http://www.resultados.gob.ar/escrutinio/dat99/'

    # Get the json with the info to get cities's links
    js = requests.get(
        'http://www.resultados.gob.ar/javascript/mun.js').text  # can't use relative url because a bug in requests
    string_json = js[js.find('['):js.rfind(';')]  # crop the js to obtain the json (is inside a global variable)
    parser = JsonComment(json)  # needed because the json have trailing commas inside
    municipios_json = parser.loads(string_json)

    # Get the provinces ids and names (id is necessary to obtain the cities's links)
    main_page = requests.get(main_url + 'DDN99999P.htm')
    main_page_root = html.fromstring(main_page.content)
    provincias = {}  # provincias = {provincia_id: provincia_name, ...}
    for elem in main_page_root.cssselect('#interiorindicesmunicipios > .indices > li'):
        provincia_id = elem.cssselect('span')[0].get('id')[1:]
        for a_elem in elem.cssselect('a'):
            if not a_elem.get('class') or 'linkmuninojs' not in a_elem.get('class'):
                provincias[provincia_id] = a_elem.text

    # Get the cities's names and links
    municipios = []  # municipios = [(provincia_name, municipio_name, municipio_link), ...]
    for provincia_obj in municipios_json:
        provincia_id = provincia_obj['cod']
        provincia_name = provincias[provincia_id]
        data[provincia_name] = {}
        for municipio_obj in provincia_obj['mun']:
            municipio_id = municipio_obj['cod']
            municipio_name = municipio_obj['nom']
            # according to general.js, toggleMunicipios function:
            municipio_link = main_url + '../dat' + provincia_id + '/DDN' + provincia_id + municipio_id + 'A.htm'
            municipios.append((provincia_name, municipio_name, municipio_link))

    # Get the categories for each city
    categorias = []  # categorias = [(provincia_name, municipio_name, categoria_name, categoria_link), ...]
    for provincia_name, municipio_name, municipio_link in municipios:
        municipio_page_root = html.fromstring(requests.get(municipio_link).content)
        for categoria_elem in municipio_page_root.cssselect('#menubotones > ul > li'):
            categoria_name = categoria_elem.cssselect('a')[0].text
            if 'act' in categoria_elem.get('class'):
                # When you get the municipio_page, you get one of the categoria_page
                # So instead of add it to categorias array, you can call get_data_from_ciudad_categoria with the
                # municipio_page_root and don't need to visit the link twice
                get_data_from_ciudad_categoria(data, provincia_name, municipio_name, categoria_name,
                                               municipio_page_root)
            else:
                categoria_link = municipio_link[:municipio_link.rfind('/') + 1] + \
                                 categoria_elem.cssselect('a')[0].get('href')
                categorias.append((provincia_name, municipio_name, categoria_name, categoria_link))

    # Get the data for every category of every city
    for provincia_name, municipio_name, categoria_name, categoria_link in categorias:
        get_data_from_ciudad_categoria_link(data, provincia_name, municipio_name, categoria_name, categoria_link)

    save_data_to_json_file(data)


def get_data_from_ciudad_categoria_link(data, provincia_name, municipio_name, categoria_name, categoria_link):
    get_data_from_ciudad_categoria(data, provincia_name, municipio_name, categoria_name,
                                   html.fromstring(requests.get(categoria_link).content))


def get_data_from_ciudad_categoria(data, provincia_name, municipio_name, categoria_name, categoria_page_root):
    date_time_string = categoria_page_root.cssselect('#fechacorta > p')[0].text.split(' ')
    (hour, minute) = date_time_string[3].split(':')
    (day, month) = date_time_string[5].split('/')
    date_time = datetime.datetime(year, int(month), int(day), int(hour), int(minute))

    for mesa_elem in categoria_page_root.cssselect('.mesasEscrutadas > p'):
        if mesa_elem.text.startswith('Mesas totales: '):
            mesas_totales = atoi(mesa_elem.cssselect('span')[0].text)
        elif mesa_elem.text.startswith('Mesas escrutadas: '):
            mesas_escrutadas = atoi(mesa_elem.text.split(' ')[2])
    votos_emitidos = atoi(categoria_page_root.cssselect('#tablavotos > tbody > .electores > .vot')[0].text)
    for participacion_elem in categoria_page_root.cssselect('.participacion > p'):
        if participacion_elem.text.startswith('Participación sobre escrutado:'):
            porcentaje_votos_emitidos = atof(participacion_elem.cssselect('span')[0].text[:-1])/100
            porcentaje_votos_no_emitidos = 1-porcentaje_votos_emitidos
            votos_no_emitidos = round(porcentaje_votos_no_emitidos*votos_emitidos/porcentaje_votos_emitidos)
    votos_en_blanco = atoi(categoria_page_root.cssselect('#tablavotos > tbody > .blan > .vot')[0].text)
    votos_nulos = atoi(categoria_page_root.cssselect('#tablavotos > tbody > .nulos > .vot')[0].text)
    votos_rec_imp_com = atoi(categoria_page_root.cssselect('#tablavotos > tbody > .recimp > .vot')[0].text)
    info_general = {'mesas_totales': mesas_totales, 'mesas_escrutadas': mesas_escrutadas,
                    'votos_emitidos': votos_emitidos, 'votos_no_emitidos': votos_no_emitidos,
                    'votos_en_blanco': votos_en_blanco, 'votos_nulos': votos_nulos,
                    'votos_rec_imp_com': votos_rec_imp_com}

    info_por_partido = {}
    listas_partido_actual = None
    for agrup_elem in categoria_page_root.cssselect('#tablaagrupaciones > tbody > tr'):
        nombre_partido_lista = agrup_elem.cssselect('.denom')[0].text
        votos_partido_lista = atoi(agrup_elem.cssselect('.vot')[0].text)
        if 'agrup' in agrup_elem.get('class'):
            # Info de un partido:
            info_partido_actual = {'votos_totales': votos_partido_lista, 'listas': {}}
            info_por_partido[nombre_partido_lista] = info_partido_actual
            listas_partido_actual = info_partido_actual['listas']
        elif 'lista' in agrup_elem.get('class'):
            listas_partido_actual[nombre_partido_lista] = votos_partido_lista

    if municipio_name.startswith('Sección'):
        mun = 'secciones'
    else:
        mun = 'municipios'
    if categoria_name not in data[provincia_name]:
        data[provincia_name][categoria_name] = {'secciones': {}, 'municipios': {}}
    info = {date_time.isoformat(): {'info_general': info_general, 'info_por_partido': info_por_partido}}
    data[provincia_name][categoria_name][mun][municipio_name] = info


def save_data_to_json_file(data):
    with open('data/' + file_name + '.json', 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
