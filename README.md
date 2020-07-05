**Análisis y visualización de datos de casos de COVID-19**

![](mapas/mapa_casos_provincia.png?raw=true)
![](mapas/mapa_casos_region.png?raw=true)
![](mapas/mapa_casos_region_ultimos_dias.png?raw=true)

Carpeta `programas`

Programa | Función | Entradas | Salidas
--- | --- | --- | ---
datos_minsal.py | Descargar y procesar datos abiertos de casos en Argentina
mapa_bsas.py | Elaborar mapas de casos en municipios de Pcia. de Bs. As. |
datos_minsal_parametros_internacion.py | Calcular distintos parámetros útiles para modelado |

Carpeta `mapas`

Archivo | Datos | Código | Fuente de datos
--- | --- | --- | ---
mapa_casos_provincia.png | Mapa de casos confirmados por municipio de la Pcia. de Bs. As. | mapa_bsas.py | 1
mapa_casos_region.png | Mapa de casos confirmados en municipios del centro-sudeste de Bs. As. | mapa_bsas.py | 1
mapa_casos_region_ultimos_dias.png | Mapa de casos confirmados en municipios del centro-sudeste de Bs. As. en los últimos días | mapa_bsas.py | 1


Carpeta `datos`

Archivo | Datos | Código | Fuente de datos
--- | --- | --- | ---
datos_minsal_completos.csv | Datos completos de casos confirmados en Argentina | datos_minsal.py | 1
datos_minsal_completos_bsas.csv | Datos de casos confirmados en Pcia. de Bs.As. | datos_minsal.py | 1
datos_minsal_acumulados_municipios_bsas.csv | Datos de casos totals confirmados por municipio de la Pcia. de Bs.As. | datos_minsal.py | 1
datos_minsal_parametros_internacion.csv | datos de internación según severidad de los casos | datos_minsal_parametros_internacion.py | 1
municipios_latitud_longitud.csv | Municipios de la Pcia. de Bs. As., latitud y longitud | 
municipios_rsviii_poblacion.csv | Población por rango de edad de municipios de la Región Sanitaria VIII (PBA) | | 2
municipios_rsviii.csv | Municipios de la Región Sanitaria VIII (PBA) |
kml_municipios | Mapa de base de municipios en formato kml |


Fuentes de datos:
1. http://datos.salud.gob.ar/dataset/covid-19-casos-registrados-en-la-republica-argentina
2. http://www.estadistica.ec.gba.gov.ar/dpe/index.php/poblacion/proyecciones/municipios
