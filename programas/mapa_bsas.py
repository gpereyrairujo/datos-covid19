import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np


def mapa_municipios(datos_mapa, columna_datos, ruta_imagen, titulo='', subtitulo='', leyenda_pie='', rotulos=True, leyenda_escala=True, escala_log=True, maximo_escala_log=3, maximo_escala_lineal=75, ancho_pugadas=7, alto_pulgadas=5, paleta='Blues'):
    columna_municipio = 'Municipio'
    # calcular logaritmo para usar esos valores para la escala de color del mapa
    if(escala_log):
        columna_datos_log = 'datos_log'
        datos_mapa[columna_datos_log] = np.log10(datos_mapa[columna_datos])
    # paleta de colores, bordes, texto
    paleta_colores = plt.cm.get_cmap(paleta)
    paleta_colores.set_under('white')           # valores por debajo del mínimo (ceros)
    color_fondo = 'white'
    color_bordes = 'darkred'
    grosor_bordes = 0.1
    tamanio_rotulos=7
    tamanio_titulo=9
    tamanio_subtitulo=8
    tamanio_leyenda=5
    # figura, tamaño, ejes
    fig, ax = plt.subplots(1, figsize=(ancho_pugadas, alto_pulgadas))       # crear figura y asignar tamaño
    plt.axis('equal')                                                       # mantener proporción latitud y longitud
    ax.set_axis_off()                                                       # quitar ejes
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.margins(0.05,0.05)                                                  # margen alrededor del mapa
    fig.patch.set_facecolor(color_fondo)                                    # color del fondo
    # datos para el mapa
    if(escala_log):
        columna=columna_datos_log
        maximo_escala=maximo_escala_log
    else:
        columna=columna_datos
        maximo_escala=maximo_escala_lineal
    ax = datos_mapa.plot(
        column=columna,                                   # valores a usar para la escala de colores
        cmap=paleta_colores, vmin=0, vmax=maximo_escala,        # escala de colores entre valores log 0 y 3 (entre 1 y 1000)
        edgecolor=color_bordes, linewidth=grosor_bordes,            # bordes
        ax=ax)
    # rótulos para cada municipio
    if(rotulos):
        for idx, fila in datos_mapa.iterrows():
            if(fila[columna_datos]>0):
                plt.text(
                    fila['Longitud'], fila['Latitud'],                                 # ubicación
                    fila[columna_municipio]+'\n'+str(int(fila[columna_datos])),              # texto
                    {'color':'black', 'fontsize':tamanio_rotulos, 'ha':'center', 'va':'center'},     # formato
                    bbox=dict(boxstyle="round", facecolor='lightgrey', edgecolor='white', alpha=0.5, linewidth=grosor_bordes)           # cuadro de texto
                )
    # leyendas
    izquierda, derecha = plt.xlim()     # límites del mapa en x
    abajo, arriba = plt.ylim()          # límites del mapa en y
    pos_y_subtitulo = arriba + (abajo-arriba)/100 * 4
    plt.text(izquierda, arriba, titulo, {'color': paleta_colores(0.5), 'fontsize': tamanio_titulo, 'ha': 'left', 'fontweight': 'bold'})
    plt.text(izquierda, pos_y_subtitulo, subtitulo, {'color': paleta_colores(0.5), 'fontsize': tamanio_subtitulo, 'ha': 'left', 'fontweight': 'bold'})
    plt.text(izquierda, abajo, leyenda_pie, {'color': 'black', 'fontsize': tamanio_leyenda})
    # leyenda rangos de colores
    if(leyenda_escala):
        if(escala_log):
            cantidad_rotulos=maximo_escala_log+1
        else:
            cantidad_rotulos=4
        for i in range(cantidad_rotulos):
            if(escala_log):
                valor = 10**i
                color = paleta_colores(i / (cantidad_rotulos-1))
            else:
                valor = maximo_escala_lineal / (cantidad_rotulos) * (i+1)
                color = paleta_colores(valor / maximo_escala_lineal)
            posicion_y = abajo - (cantidad_rotulos-i) * (abajo-arriba)/20
            posicion_x = derecha - (derecha-izquierda)/30
            plt.text(
                posicion_x, posicion_y,
                str(int(valor)),
                {'color':'black', 'fontsize':tamanio_rotulos, 'ha':'right', 'va':'center'},
                bbox=dict(boxstyle="round", facecolor=color, edgecolor=color_bordes, linewidth=0.1))
    # guardar mapa
    plt.savefig(ruta_imagen, facecolor=fig.get_facecolor(), bbox_inches = 'tight', pad_inches = 0.1, dpi=150)



# mapas

ruta_mapa_base = '../mapas/kml_municipios/municipios.shp'
ruta_casos_municipios = '../csv/datos_minsal_acumulados_municipios_bsas.csv'
ruta_casos_diarios_municipios = '../csv/datos_minsal_diarios_municipios_bsas.csv'
ruta_evolucion_casos_municipios = '../csv/datos_minsal_evolucion_municipios_bsas.csv'
ruta_evolucion_positividad_municipios = '../csv/datos_minsal_positividad_municipios_bsas.csv'
ruta_movilidad_diarios_municipios = '../csv/datos_movilidad_diarios_municipios_bsas.csv'
ruta_municipios_rsviii = '../csv/municipios_rsviii.csv'
carpeta_destino_mapas = '../mapas/'

# leer datos mapa base
datos_mapa = gpd.read_file(ruta_mapa_base, encoding='utf-8')
# dejar sólo pcia de bs as (código comienza con 06)
datos_mapa = datos_mapa.loc[datos_mapa['IN1'].str[:2]=='06']
# corrección de errores
datos_mapa.loc[datos_mapa['NAM']=='General las  Heras', 'NAM'] = 'General Las Heras'
datos_mapa.loc[datos_mapa['NAM']=='General la Madrid', 'NAM'] = 'General La Madrid'

# leer datos de casos municipios
datos_casos_municipios = pd.read_csv(ruta_casos_municipios)
# unir la tabla de casos de municipios de la pcia de bs as y los datos del mapa base
datos_mapa = datos_mapa.merge(datos_casos_municipios, left_on='NAM', right_on='Municipio', how='left')
# calcular casos totales
datos_mapa['Total']=datos_mapa['Activo']+datos_mapa['Fallecido']+datos_mapa['Recuperado']
# fecha de última actualización
ultima_actualizacion = datos_mapa.loc[1, 'ultima_actualizacion']


# mapa 1: provincia bs as
titulo = 'Casos confirmados'
leyenda = 'github.com/gpereyrairujo/datos-covid19\nelaborado en base a datos abiertos del Ministerio de Salud'
ruta_imagen = carpeta_destino_mapas + 'mapa_casos_provincia.png'
# dibujar mapa
mapa_municipios(datos_mapa, 'Total', ruta_imagen, titulo, ultima_actualizacion, leyenda, rotulos=False, leyenda_escala=True, maximo_escala_log=3, ancho_pugadas=4.3, alto_pulgadas=5)


# mapa 2: region centro-sudeste
titulo = 'Casos confirmados totales'
leyenda = 'github.com/gpereyrairujo/datos-covid19 - elaborado en base a datos abiertos del Ministerio de Salud'
ruta_imagen = carpeta_destino_mapas + 'mapa_casos_region.png'
# filtrar por latitud y longitud
datos_mapa = datos_mapa.loc[(datos_mapa['Latitud']<-35.7) & (datos_mapa['Longitud']>-60.8)]
# dibujar mapa
mapa_municipios(datos_mapa, 'Total', ruta_imagen, titulo, ultima_actualizacion, leyenda, rotulos=True, leyenda_escala=True, maximo_escala_log=3, ancho_pugadas=7, alto_pulgadas=5)



# leer tabla de casos diarios por municipio
datos_evolucion_casos_municipios = pd.read_csv(ruta_evolucion_casos_municipios)
datos_evolucion_casos_municipios = datos_evolucion_casos_municipios.set_index('fecha_apertura')
# leer listado de municipios región sanitaria viii
datos_municipios_rsviii = pd.read_csv(ruta_municipios_rsviii)
# hacer gráfico
fig, ax = plt.subplots(1, figsize=(7, 5))
# filtrar municipios
#municipios_rsviii = datos_municipios_rsviii['Municipio']
municipios_rsviii = datos_mapa['Municipio']
municipios_con_datos = datos_evolucion_casos_municipios.columns
municipios_rsviii_con_datos = [m for m in municipios_rsviii if m in municipios_con_datos]
datos_evolucion_casos_municipios = datos_evolucion_casos_municipios[municipios_rsviii_con_datos]
# graficar
datos_evolucion_casos_municipios.plot(ax=ax)
#plt.show(block=True)


# calular casos últimos días
ultimos_dias = 7
casos_ultimos_dias = datos_evolucion_casos_municipios.diff(periods=ultimos_dias)
# crear nueva tabla de datos
casos_ultimos_dias = casos_ultimos_dias.iloc[-1].to_frame().reset_index()
# renombrar columnas
casos_ultimos_dias.columns = ['Municip', 'casos_ultimos_dias']
# unir los datos de casos de los últimos días a la tabla de datos del mapa anterior
datos_mapa_ultimos_dias = datos_mapa.merge(casos_ultimos_dias, left_on='Municipio', right_on='Municip', how='left')
# rellenar con 0 los municipios sin datos
datos_mapa_ultimos_dias = datos_mapa_ultimos_dias.fillna(0)
print(datos_mapa_ultimos_dias)


# mapa 3: casos últimos días region centro-sudeste
titulo = 'Casos confirmados últimos ' + str(ultimos_dias) + ' días'
leyenda = 'github.com/gpereyrairujo/datos-covid19 - elaborado en base a datos abiertos del Ministerio de Salud'
ruta_imagen = carpeta_destino_mapas + 'mapa_casos_region_ultimos_dias.png'
# dibujar mapa
mapa_municipios(datos_mapa_ultimos_dias, 'casos_ultimos_dias', ruta_imagen, titulo, ultima_actualizacion, leyenda, rotulos=True, leyenda_escala=True, maximo_escala_log=3, ancho_pugadas=7, alto_pulgadas=5, paleta='Reds')





# leer tabla de movilidad diaria por municipio
datos_movilidad_diarios_municipios = pd.read_csv(ruta_movilidad_diarios_municipios)
datos_movilidad_diarios_municipios = datos_movilidad_diarios_municipios.set_index('ds')
# filtrar municipios
municipios_rsviii = datos_mapa['Municipio']
municipios_con_datos = datos_movilidad_diarios_municipios.columns
municipios_rsviii_con_datos = [m for m in municipios_rsviii if m in municipios_con_datos]
datos_movilidad_diarios_municipios = datos_movilidad_diarios_municipios[municipios_rsviii_con_datos]

# calular movilidad promedio últimos días
ultimos_dias_movilidad = 7
movilidad_ultimos_dias = datos_movilidad_diarios_municipios.rolling(ultimos_dias).mean()
# crear nueva tabla de datos
movilidad_ultimos_dias = movilidad_ultimos_dias.iloc[-1].to_frame().reset_index()
# renombrar columnas
movilidad_ultimos_dias.columns = ['Municip', 'movilidad_ultimos_dias']
# convertir a "disminución de la movilidad" = 0 a 100%
movilidad_ultimos_dias['movilidad_ultimos_dias'] = movilidad_ultimos_dias['movilidad_ultimos_dias'] * -100
# unir los datos de disminución movilidad de los últimos días a la tabla de datos del mapa anterior
datos_mapa_movilidad = datos_mapa.merge(movilidad_ultimos_dias, left_on='Municipio', right_on='Municip', how='left')
# rellenar con 0 los municipios sin datos
#datos_mapa_movilidad = datos_mapa_movilidad.fillna(0)
print(datos_mapa_movilidad)

# mapa 4: movilidad últimos días region centro-sudeste
titulo = 'Disminución de la movilidad (% promedio ' + str(ultimos_dias_movilidad) + ' días)'
leyenda = 'github.com/gpereyrairujo/datos-covid19 - elaborado en base a datos abiertos de humdata.org'
ruta_imagen = carpeta_destino_mapas + 'mapa_movilidad_region_ultimos_dias.png'
# dibujar mapa
mapa_municipios(
    datos_mapa_movilidad, 'movilidad_ultimos_dias', 
    ruta_imagen, 
    titulo, ultima_actualizacion, leyenda, 
    rotulos=True, leyenda_escala=True, 
    escala_log=False, maximo_escala_lineal=60, 
    ancho_pugadas=7, alto_pulgadas=5, 
    paleta='summer')





# leer tabla de evolución de positividad por municipio
datos_evolucion_positividad_municipios = pd.read_csv(ruta_evolucion_positividad_municipios)
datos_evolucion_positividad_municipios = datos_evolucion_positividad_municipios.set_index('fecha_apertura')
# leer listado de municipios región sanitaria viii
#datos_municipios_rsviii = pd.read_csv(ruta_municipios_rsviii)
# filtrar municipios
#municipios_rsviii = datos_municipios_rsviii['Municipio']
municipios_rsviii = datos_mapa['Municipio']
municipios_con_datos_positividad = datos_evolucion_positividad_municipios.columns
municipios_rsviii_con_datos_positividad = [m for m in municipios_rsviii if m in municipios_con_datos_positividad]
datos_evolucion_positividad_municipios = datos_evolucion_positividad_municipios[municipios_rsviii_con_datos_positividad]
# graficar
#datos_evolucion_positividad_municipios.plot(ax=ax)
#plt.show(block=True)

# crear nueva tabla de datos
positividad_ultimo_periodo = datos_evolucion_positividad_municipios.iloc[-1].to_frame().reset_index()
# renombrar columnas
positividad_ultimo_periodo.columns = ['Munic', 'positividad_ultimo_periodo']
# convertir a %
positividad_ultimo_periodo['positividad_ultimo_periodo'] = positividad_ultimo_periodo['positividad_ultimo_periodo'] * 100
# unir los datos de positividad de los últimos días a la tabla de datos del mapa anterior
datos_mapa_positividad = datos_mapa.merge(positividad_ultimo_periodo, left_on='Municipio', right_on='Munic', how='left')
# rellenar con 0 los municipios sin datos
datos_mapa_positividad = datos_mapa_positividad.fillna(0)
print(datos_mapa_positividad)


# mapa 5: positividad últimos días region centro-sudeste
ultimos_dias_positividad = 7
titulo = 'Positividad de casos (% promedio ' + str(ultimos_dias_positividad) + ' días)'
leyenda = 'github.com/gpereyrairujo/datos-covid19 - elaborado en base a datos abiertos del Ministerio de Salud'
ruta_imagen = carpeta_destino_mapas + 'mapa_positividad_region_ultimos_dias.png'
# dibujar mapa
mapa_municipios(
    datos_mapa_positividad, 'positividad_ultimo_periodo', 
    ruta_imagen, 
    titulo, ultima_actualizacion, leyenda, 
    rotulos=True, leyenda_escala=True, 
    escala_log=False, maximo_escala_lineal=60, 
    ancho_pugadas=7, alto_pulgadas=5, 
    paleta='RdPu')

plt.show(block=True)

