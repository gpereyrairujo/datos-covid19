import pandas as pd
import numpy as np
import wget
import os
from ruamel.std.zipfile import delete_from_zip_file

# datos de entrada
# datos de movilidad
# fuente de datos: https://data.humdata.org/dataset/movement-range-maps
url = 'https://data.humdata.org/dataset/c3429f0e-651b-4788-bb2f-4adbf222c90e/resource/31ca909c-10d9-458a-8720-88b54b3e3627/download/'
carpeta_origen = '../csv/'
archivo_movilidad = 'datos_movilidad.zip'
columnas_con_fechas = [0]
separador = '\t'            # separado por tabulaciones
codificacion = 'utf-8'
# datos locales
carpeta_origen = '../csv/'
archivo_municipios = 'municipios_latitud_longitud.csv'
# dónde guardar los resultados
carpeta_destino = carpeta_origen
archivo_destino_datos_argentina = 'datos_movilidad_argentina.csv'
archivo_destino_datos_argentina_bsas = 'datos_movilidad_argentina_bsas.csv'
archivo_destino_datos_diarios_por_municipio_bsas = 'datos_movilidad_diarios_municipios_bsas.csv'


# 1. leer datos de movilidad
# archivo donde se descargarán los datos
ruta = carpeta_origen + archivo_movilidad
# si el archivo ya existe, borrarlo
if os.path.exists(ruta):
    os.remove(ruta)
# descargar archivo zip original
wget.download(url, ruta)
# eliminar el archivo .txt del archivo zip
delete_from_zip_file(ruta, file_names=['README.txt']) 
# leer los datos 
datos = pd.read_csv(ruta, sep=separador, encoding=codificacion, skipinitialspace=True, parse_dates=columnas_con_fechas, infer_datetime_format=True)


# 2. filtrar datos de argentina
# dejar sólo datos de argentina
datos = datos.loc[datos['country']=='ARG']
# exportar los datos
ruta = carpeta_destino + archivo_destino_datos_argentina
datos.to_csv(ruta, index=False)


# 3. filtrar datos pcia de buenos aires
# leer listado de municipios con latitud y longitud
ruta = carpeta_origen + archivo_municipios
datos_municipios = pd.read_csv(ruta)
# agregar columna con nombres de municipios modificados (sin acentos)
datos_municipios['Municipio-'] = datos_municipios['Municipio']
datos['polygon_name-'] = datos['polygon_name']
letras_a_reemplazar = 'áéíóúñÁÉÍÓÚÑ'
for letra in letras_a_reemplazar:
    datos_municipios['Municipio-'] = datos_municipios['Municipio-'].str.replace(letra, '-')
    datos['polygon_name-'] = datos['polygon_name-'].str.replace(letra, '-')
# nombres de municipios con números
datos_municipios['Municipio-'] = datos_municipios['Municipio-'].str.replace("25", 'Veinticinco')
datos_municipios['Municipio-'] = datos_municipios['Municipio-'].str.replace("9", 'Nueve')
# unir la tabla con los datos de población y coordenadas de cada municipio y la tabla de datos de movilidad
datos_municipios = pd.merge(datos_municipios, datos, right_on='polygon_name-', left_on='Municipio-', how='left')
# exportar los datos
ruta = carpeta_destino + archivo_destino_datos_argentina_bsas
datos_municipios.to_csv(ruta, index=False)


# 4. armar tabla con los datos diarios de movilidad para cada municipio
datos['casos'] = 1
tabla_movilidad = datos_municipios.pivot_table(
    index=['ds'], columns='Municipio', values='all_day_bing_tiles_visited_relative_change', aggfunc=np.mean
)
# exportar los datos
ruta = carpeta_destino + archivo_destino_datos_diarios_por_municipio_bsas
tabla_movilidad.to_csv(ruta, index=True)

