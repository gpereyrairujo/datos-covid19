import pandas as pd
import matplotlib.pyplot as plt

# variables de entrada
carpeta_origen = './'
archivo_origen = 'covid_19_casos.csv'
columnas_con_fechas = [8,10,12,14,16,21]
carpeta_destino = carpeta_origen
archivo_destino = 'datos_minsal_parametros_internacion.csv'

# leer datos
ruta = carpeta_origen + archivo_origen
datos = pd.read_csv(ruta, sep=';', skipinitialspace=True, parse_dates=columnas_con_fechas, infer_datetime_format=True)

# procesar datos

# dejar sólo casos confirmados
datos = datos.loc[datos['clasificacion_resumen']=='Confirmado']
# dejar sólo casos con fecha de inicio de síntomas conocida
datos = datos[datos.fis.notnull()]
# dejar sólo casos con dato de sexo
datos = datos.loc[datos['sexo'].isin(['F','M'])]
# dejar sólo casos resueltos
datos = datos.loc[datos['clasificacion'].isin([
    'Caso confirmado - No activo (por laboratorio y tiempo de evolución)',
    'Caso confirmado - No Activo por criterio de laboratorio',
    'Caso confirmado - No activo (por tiempo de evolución)',
    'Caso confirmado - Fallecido'])]

print('casos resueltos:', datos['id_evento_caso'].count())
print('fallecidos:', datos.loc[datos['fallecido']=='SI', 'id_evento_caso'].count())
print('dados de alta:', datos.loc[datos['fallecido']!='SI', 'id_evento_caso'].count())
print('edad promedio casos resueltos:', datos['edad_actual_anios'].mean())
print('edad promedio fallecidos:', datos.loc[datos['fallecido']=='SI', 'edad_actual_anios'].mean())
print('edad promedio dados de alta:', datos.loc[datos['fallecido']!='SI', 'edad_actual_anios'].mean())

# crear nueva columna para 'internacion'
datos['internacion'] = 'NO'
datos.loc[datos.fecha_internacion.notnull(),'internacion'] = 'SI'

# rellenar datos faltantes:
# si fallecido no es SI, entonces es NO
datos.loc[datos['fallecido']!='SI', 'fallecido'] = 'NO'
# si asist_resp_mecanica no es SI, entonces es NO
datos.loc[datos['asist_resp_mecanica']!='SI', 'asist_resp_mecanica'] = 'NO'
# si cuidado_intensivo no es SI, entonces es NO
datos.loc[datos['cuidado_intensivo']!='SI', 'cuidado_intensivo'] = 'NO'

# corrección de datos:
# si tuvo asistencia respiratoria, entonces cuidado_intensivo=SI
datos.loc[datos['asist_resp_mecanica']=='SI', 'cuidado_intensivo'] = 'SI'
# si tiene fecha_cui_intensivo, entonces cuidado_intensivo=SI
datos.loc[datos.fecha_cui_intensivo.notnull(),'cuidado_intensivo'] = 'SI'
# si cuidado_intensivo=SI, entonces internacion=SI
datos.loc[datos['cuidado_intensivo']=='SI', 'internacion'] = 'SI'
# si cuidado_intensivo=SI pero no tiene fecha_internacion, entonces fecha_internacion = fecha_cui_intensivo
datos.loc[datos.fecha_cui_intensivo.notnull() & datos.fecha_internacion.isnull(), 'fecha_internacion'] = datos['fecha_cui_intensivo']

# cálculo de duraciones:
# días de inicio de síntomas a internación
datos.loc[datos['internacion']=='SI', 'dias_fis_a_internacion'] = (datos['fecha_internacion']-datos['fis']).dt.days
# días de inicio de síntomas a cuidado intensivo
datos.loc[datos['cuidado_intensivo']=='SI', 'dias_fis_a_cuidado_intensivo'] = (datos['fecha_cui_intensivo']-datos['fis']).dt.days
# días de inicio de síntomas a fallecimiento
datos.loc[datos['fallecido']=='SI', 'dias_fis_a_fallecimiento'] = (datos['fecha_fallecimiento']-datos['fis']).dt.days
# días de internación a cuidado intensivo
datos.loc[datos['cuidado_intensivo']=='SI', 'dias_internacion_a_cuidado_intensivo'] = (datos['fecha_cui_intensivo']-datos['fecha_internacion']).dt.days
# días de internación a fallecimiento
datos.loc[(datos['fallecido']=='SI') & (datos['internacion']=='SI'), 'dias_internacion_a_fallecimiento'] = (datos['fecha_fallecimiento']-datos['fecha_internacion']).dt.days
# días de cuidado intensivo a fallecimiento
datos.loc[(datos['fallecido']=='SI') & (datos['cuidado_intensivo']=='SI'), 'dias_cuidado_intensivo_a_fallecimiento'] = (datos['fecha_fallecimiento']-datos['fecha_cui_intensivo']).dt.days



# comparación de días trasncurridos entre distintos estados

dias_fis_a_internacion = datos.loc[datos['internacion']=='SI', 'dias_fis_a_internacion'].values
dias_fis_a_cuidado_intensivo = datos.loc[datos['cuidado_intensivo']=='SI', 'dias_fis_a_cuidado_intensivo'].values
dias_fis_a_fallecimiento = datos.loc[datos['fallecido']=='SI', 'dias_fis_a_fallecimiento'].values
dias_internacion_a_cuidado_intensivo = datos.loc[datos['cuidado_intensivo']=='SI', 'dias_internacion_a_cuidado_intensivo'].values
dias_internacion_a_fallecimiento = datos.loc[(datos['fallecido']=='SI') & (datos['internacion']=='SI'), 'dias_internacion_a_fallecimiento'].values
dias_cuidado_intensivo_a_fallecimiento = datos.loc[(datos['fallecido']=='SI') & (datos['cuidado_intensivo']=='SI'), 'dias_cuidado_intensivo_a_fallecimiento'].values

fig1, ax1 = plt.subplots()
ax1.set_title('Días transcurridos entre distintos estados')
datos_grafico = [
    dias_fis_a_internacion, 
    dias_fis_a_cuidado_intensivo, 
    dias_fis_a_fallecimiento, 
    dias_internacion_a_cuidado_intensivo, 
    dias_internacion_a_fallecimiento, 
    dias_cuidado_intensivo_a_fallecimiento]
etiquetas = [
    'fis-intern', 
    'fis-uci', 
    'fis-fallec',
    'intern-uci',
    'intern-fallec',
    'uci-fallec']
ax1.violinplot(datos_grafico, vert=False, showmeans=True)
plt.setp(ax1, yticks=[y+1 for y in range(len(etiquetas))], yticklabels=etiquetas)
plt.show()


# comparación de días desde inicio de síntomas a fallecimiento dependiendo de no internación, internación o uci

dias_fis_fallecimiento_no_internados = datos.loc[(datos['fallecido']=='SI') & (datos['internacion']=='NO'), 'dias_fis_a_fallecimiento'].values
dias_fis_fallecimiento_internados_no_uci = datos.loc[(datos['fallecido']=='SI') & (datos['internacion']=='SI') & (datos['cuidado_intensivo']=='NO'), 'dias_fis_a_fallecimiento'].values
dias_fis_fallecimiento_uci = datos.loc[(datos['fallecido']=='SI') & (datos['cuidado_intensivo']=='SI'), 'dias_fis_a_fallecimiento'].values

fig1, ax1 = plt.subplots()
ax1.set_title('Días desde inicio de síntomas a fallecimiento')
datos_grafico = [
    dias_fis_fallecimiento_no_internados, 
    dias_fis_fallecimiento_internados_no_uci, 
    dias_fis_fallecimiento_uci]
etiquetas = [
    'no int', 
    'int no uci', 
    'uci']
ax1.violinplot(datos_grafico, vert=False, showmeans=True)
plt.setp(ax1, yticks=[y+1 for y in range(len(etiquetas))], yticklabels=etiquetas)
plt.show()


# clasificación modelo neherlab: leves, severos, críticos y letales
# letales:
datos.loc[datos['fallecido']=='SI', 'severidad'] = 'letal'
# críticos:
datos.loc[(datos['fallecido']=='NO') & (datos['cuidado_intensivo']=='SI'), 'severidad'] = 'critico'
# severos:
datos.loc[(datos['fallecido']=='NO') & (datos['cuidado_intensivo']=='NO') & (datos['internacion']=='SI'), 'severidad'] = 'severo'
# leves:
datos.loc[(datos['fallecido']=='NO') & (datos['cuidado_intensivo']=='NO') & (datos['internacion']=='NO'), 'severidad'] = 'leve'

print('- - -')
print('casos letales:', datos.loc[datos['severidad']=='letal', 'id_evento_caso'].count())
print('casos críticos no letales:', datos.loc[datos['severidad']=='critico', 'id_evento_caso'].count())
print('casos severos no críticos:', datos.loc[datos['severidad']=='severo', 'id_evento_caso'].count())
print('casos leves:', datos.loc[datos['severidad']=='leve', 'id_evento_caso'].count())
print('edad promedio casos letales:', datos.loc[datos['severidad']=='letal', 'edad_actual_anios'].mean())
print('edad promedio casos críticos:', datos.loc[datos['severidad']=='critico', 'edad_actual_anios'].mean())
print('edad promedio casos severos:', datos.loc[datos['severidad']=='severo', 'edad_actual_anios'].mean())
print('edad promedio casos leves:', datos.loc[datos['severidad']=='leve', 'edad_actual_anios'].mean())
print('- - -')

# agregar días de internación y/o uci a fallecidos sin internación y/o sin uci
# fallecido no internado: fis a internacion=fis a fall, intern a uci=0, uci a fallec=0
datos.loc[(datos['fallecido']=='SI') & (datos.dias_fis_a_internacion.isnull()), 'dias_cuidado_intensivo_a_fallecimiento'] = 0
datos.loc[(datos['fallecido']=='SI') & (datos.dias_fis_a_internacion.isnull()), 'dias_internacion_a_cuidado_intensivo'] = 0
datos.loc[(datos['fallecido']=='SI') & (datos.dias_fis_a_internacion.isnull()), 'dias_fis_a_internacion'] = datos['dias_fis_a_fallecimiento']
# fallecido internado sin uci: intern a uci=intern a fallec, uci a fallec=0
datos.loc[(datos['fallecido']=='SI') & (datos.dias_internacion_a_cuidado_intensivo.isnull()), 'dias_cuidado_intensivo_a_fallecimiento'] = 0
datos.loc[(datos['fallecido']=='SI') & (datos.dias_internacion_a_cuidado_intensivo.isnull()), 'dias_internacion_a_cuidado_intensivo'] = datos['dias_internacion_a_fallecimiento']

# recalcular fechas
dias_fis_a_internacion = datos.loc[datos.dias_fis_a_internacion.notnull(), 'dias_fis_a_internacion'].values
dias_internacion_a_cuidado_intensivo = datos.loc[datos.dias_internacion_a_cuidado_intensivo.notnull(), 'dias_internacion_a_cuidado_intensivo'].values
dias_cuidado_intensivo_a_fallecimiento = datos.loc[datos.dias_cuidado_intensivo_a_fallecimiento.notnull(), 'dias_cuidado_intensivo_a_fallecimiento'].values

print(len(dias_fis_a_internacion))
print(len(dias_internacion_a_cuidado_intensivo))
print(len(dias_cuidado_intensivo_a_fallecimiento))

fig1, ax1 = plt.subplots()
ax1.set_title('Duración etapas modelo neherlab')
datos_grafico = [
    dias_fis_a_internacion, 
    dias_internacion_a_cuidado_intensivo, 
    dias_cuidado_intensivo_a_fallecimiento]
etiquetas = [
    'días sin int sev', 
    'días int crít', 
    'días uci fall']
ax1.violinplot(datos_grafico, vert=False, showmeans=True)
plt.setp(ax1, yticks=[y+1 for y in range(len(etiquetas))], yticklabels=etiquetas)
plt.show()

# FALTAN FECHAS DE ALTA




# seleccionar columnas para exportar
columnas_origen = [
    'id_evento_caso',
    'edad_actual_anios',
    'sexo',
    'internacion',
    'cuidado_intensivo',
    'asist_resp_mecanica',
    'fallecido',
    'fis',
    'fecha_apertura',
    'fecha_diagnostico',
    'fecha_internacion',
    'fecha_cui_intensivo',
    'fecha_fallecimiento',
    'dias_fis_a_internacion',
    'dias_fis_a_cuidado_intensivo',
    'dias_fis_a_fallecimiento',
    'dias_internacion_a_cuidado_intensivo',
    'dias_cuidado_intensivo_a_fallecimiento',
    'severidad',
    'provincia_residencia',
#    'departamento_residencia'
]
datos = datos[columnas_origen]

ruta = carpeta_destino + archivo_destino
datos.to_csv(ruta, index=False)