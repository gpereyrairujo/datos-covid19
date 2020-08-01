import pandas as pd
import numpy as np

# datos de entrada
# fuente de datos Ministerio de Salud: http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina
# chequear columnas con fechas, separador (, o ;), encoding (utf-8 o 16)
url_archivo_origen = 'https://sisa.msal.gov.ar/datos/descargas/covid-19/files/Covid19Casos.csv'
columnas_con_fechas = [8,9,11,13,15,22,24]
separador = ','
codificacion = 'utf-16'
# datos locales
carpeta_origen = '../csv/'
archivo_municipios = 'municipios_latitud_longitud.csv'
# dónde guardar los resultados
carpeta_destino = carpeta_origen
archivo_destino_datos_completos = 'datos_minsal_completos.csv'
archivo_destino_datos_completos_bsas = 'datos_minsal_completos_bsas.csv'
archivo_destino_datos_acumulados_por_municipio_bsas = 'datos_minsal_acumulados_municipios_bsas.csv'
archivo_destino_datos_diarios_por_municipio_bsas = 'datos_minsal_diarios_municipios_bsas.csv'
archivo_destino_datos_evolucion_por_municipio_bsas = 'datos_minsal_evolucion_municipios_bsas.csv'
archivo_destino_datos_positividad_por_municipio_bsas = 'datos_minsal_positividad_municipios_bsas.csv'


# 1. leer datos del repositorio online
datos = pd.read_csv(url_archivo_origen, sep=separador, encoding=codificacion, skipinitialspace=True, parse_dates=columnas_con_fechas, infer_datetime_format=True)


# 2. procesar datos
# dejar sólo casos confirmados
#datos = datos.loc[datos['clasificacion_resumen']=='Confirmado']
# agregar una clasificación simplificada de casos en Activo, Recuperado y Fallecido
datos.loc[datos['clasificacion']=='Caso confirmado - Fallecido', 'clasificacion_simple'] = 'Fallecido'
datos.loc[datos['clasificacion'].isin([
    'Caso confirmado - No activo (por laboratorio y tiempo de evolución)',
    'Caso confirmado - No Activo por criterio de laboratorio',
    'Caso confirmado - No activo (por tiempo de evolución)']), 'clasificacion_simple'] = 'Recuperado'
datos.loc[datos['clasificacion'].isin([
    'Caso confirmado - Activo ',
    'Caso confirmado - Activo Internado',
    'Caso confirmado - Activo con seguimiento negativo']), 'clasificacion_simple'] = 'Activo'
# crear nueva columna con edad en años a partir de la edad en años o meses
datos['edad_actual_anios'] = datos['edad']
datos.loc[datos['edad_años_meses']=='Meses','edad_actual_anios'] = 0
# estadísticas resumen y chequeo de datos
total_confirmados_1 =   datos.loc[datos['clasificacion_resumen']=='Confirmado', 'id_evento_caso'].count()
total_descartados =     datos.loc[datos['clasificacion_resumen']=='Descartado', 'id_evento_caso'].count()
total_sospechosos =     datos.loc[datos['clasificacion_resumen']=='Sospechoso', 'id_evento_caso'].count()
total_sin_clasificar =  datos.loc[datos['clasificacion_resumen']=='Sin Clasificar', 'id_evento_caso'].count()
total_casos =           total_confirmados_1 + total_descartados
positividad =           total_confirmados_1 / total_casos
total_activos =         datos.loc[datos['clasificacion_simple']=='Activo', 'id_evento_caso'].count()
total_recuperados =     datos.loc[datos['clasificacion_simple']=='Recuperado', 'id_evento_caso'].count()
total_fallecidos =      datos.loc[datos['clasificacion_simple']=='Fallecido', 'id_evento_caso'].count()
total_confirmados_2 =   total_activos + total_recuperados + total_fallecidos
edad_promedio_confirmados =     round(datos.loc[datos['clasificacion_resumen']=='Confirmado', 'edad_actual_anios'].mean(),1)
edad_promedio_activos =         round(datos.loc[datos['clasificacion_simple']=='Activo', 'edad_actual_anios'].mean(),1)
edad_promedio_recuperados =     round(datos.loc[datos['clasificacion_simple']=='Recuperado', 'edad_actual_anios'].mean(),1)
edad_promedio_fallecidos =      round(datos.loc[datos['clasificacion_simple']=='Fallecido', 'edad_actual_anios'].mean(),1)
fecha_apertura_min = datos['fecha_apertura'].min()
fecha_apertura_max = datos['fecha_apertura'].max()
fecha_ultima_actualizacion =  datos['ultima_actualizacion'].max()
inicio_casos =  fecha_apertura_min.strftime('%d/%m/%Y')
fin_casos =  fecha_apertura_max.strftime('%d/%m/%Y')
ultima_actualizacion =  fecha_ultima_actualizacion.strftime('%d/%m/%Y')
print('Activos:', total_activos)
print('Recuperados:', total_recuperados)
print('Fallecidos:', total_fallecidos)
print('Edad promedio confirmados:', edad_promedio_confirmados)
print('Edad promedio activos:', edad_promedio_activos)
print('Edad promedio recuperados:', edad_promedio_recuperados)
print('Edad promedio fallecidos:', edad_promedio_fallecidos)
print('Total casos:', total_casos)
print('Total confirmados (columna clasificacion_resumen):', total_confirmados_1)
print('Total confirmados (columna clasificacion):', total_confirmados_2)
print('Positividad:', positividad)
print('Inicio casos',inicio_casos)
print('Fin casos',fin_casos)
print('Datos correspondientes al día',ultima_actualizacion)


# 3. guardar listado completo de casos confirmados (archivo mucho más chico que el original completo)
datos_confirmados = datos.loc[datos['clasificacion_resumen']=='Confirmado']
ruta = carpeta_destino + archivo_destino_datos_completos
datos_confirmados.to_csv(ruta, index=False)


# 4. guardar listado completo de casos de municipios de la pcia de bs as
# filtrar base de datos y dejar sólo casos de Prov de Bs As
# (tomar los casos con residencia y también carga en la prov de bs as)
datos = datos.loc[datos['residencia_provincia_nombre']=='Buenos Aires']
datos = datos.loc[datos['carga_provincia_nombre']=='Buenos Aires']
# exportar los datos
ruta = carpeta_destino + archivo_destino_datos_completos_bsas
datos.to_csv(ruta, index=False)


# 5. armar tabla con total de casos confirmados activos, fallecidos y recuperados en cada municipio
datos.loc[datos['clasificacion_resumen']=='Confirmado', 'casos'] = 1
tabla_casos_acumulados = datos.pivot_table(
    index=['residencia_departamento_nombre'], columns='clasificacion_simple', values='casos',
    fill_value=0, aggfunc=np.sum
)
# leer listado de municipios con latitud y longitud
ruta = carpeta_origen + archivo_municipios
datos_municipios = pd.read_csv(ruta)
# unir la tabla con los datos de población y coordenadas de cada municipio y la tabla de casos
datos_municipios = pd.merge(datos_municipios, tabla_casos_acumulados, right_index=True, left_on='Municipio', how='left')
# completar datos faltantes (NaN) con ceros
datos_municipios = datos_municipios.fillna(0)
# agregar fecha de última actualización
datos_municipios['ultima_actualizacion'] = ultima_actualizacion
# exportar datos
ruta = carpeta_destino + archivo_destino_datos_acumulados_por_municipio_bsas
datos_municipios.to_csv(ruta, index=False)


# 6. armar tabla de casos *confirmados* diarios en cada municipio
datos.loc[datos['clasificacion_resumen']=='Confirmado', 'confirmados'] = 1
tabla_casos_confirmados_diarios = datos.pivot_table(
    index=['fecha_apertura'], columns='residencia_departamento_nombre', values='confirmados',
    fill_value=0, aggfunc=np.sum
)
# rellenar datos faltantes (días que no hubo casos) haciendo un 'resampling' con paso diario ('D')
tabla_casos_confirmados_diarios = tabla_casos_confirmados_diarios.resample('D').sum().fillna(0)
# exportar datos
ruta = carpeta_destino + archivo_destino_datos_diarios_por_municipio_bsas
tabla_casos_confirmados_diarios.to_csv(ruta, index=True)


# 7. armar tabla con la evolucion de casos diarios acumulados en cada municipio
tabla_evolucion_casos = tabla_casos_confirmados_diarios.cumsum()
# exportar datos
ruta = carpeta_destino + archivo_destino_datos_evolucion_por_municipio_bsas
tabla_evolucion_casos.to_csv(ruta, index=True)


# 8. calcular positividad por períodos de x días (los valores diarios podrían ser muy variables)
# armar tabla de casos *totales* (descartados y confirmados, sin incluir sospechosos) diarios en cada municipio
datos.loc[datos['clasificacion_resumen']=='Descartado', 'totales'] = 1
datos.loc[datos['clasificacion_resumen']=='Confirmado', 'totales'] = 1
tabla_casos_totales_diarios = datos.pivot_table(
    index=['fecha_apertura'], columns='residencia_departamento_nombre', values='totales',
    fill_value=0, aggfunc=np.sum
)
# rellenar datos faltantes (días que no hubo casos) haciendo un 'resampling' con paso diario ('D')
tabla_casos_totales_diarios = tabla_casos_totales_diarios.resample('D').sum().fillna(0)
# acumular datos por período de x días
periodo = 7
tabla_casos_totales_por_periodos        = tabla_casos_totales_diarios.rolling(periodo).sum()
tabla_casos_confirmados_por_periodos    = tabla_casos_confirmados_diarios.rolling(periodo).sum()
# calcular positividad
tabla_positividad_por_periodos = tabla_casos_confirmados_por_periodos.div(tabla_casos_totales_por_periodos)
# rellenar datos faltantes (días que no hubo casos) haciendo un 'resampling' con paso diario ('D')
tabla_positividad_por_periodos = tabla_positividad_por_periodos.resample('D').sum().fillna(0)
# exportar datos
ruta = carpeta_destino + archivo_destino_datos_positividad_por_municipio_bsas
tabla_positividad_por_periodos.to_csv(ruta, index=True)
