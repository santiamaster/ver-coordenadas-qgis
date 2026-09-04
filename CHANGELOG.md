# Historial de cambios

Todos los cambios relevantes de **Ver Coordenadas** se documentarán en este archivo.

## 1.0.0

Candidata a primera versión pública.

- Agrega la acción contextual **Ver coordenadas** para entidades vectoriales lineales y poligonales.
- Soporta geometrías Polygon, MultiPolygon, LineString y MultiLineString.
- Lista los vértices con numeración continua y omite los vértices de cierre duplicados de los polígonos.
- Identifica los huecos de los polígonos y muestra sus áreas individuales.
- Muestra áreas netas por polígono, áreas totales en geometrías multipartes, longitudes de líneas y longitudes totales en geometrías multipartes.
- Soporta la presentación de coordenadas proyectadas en orden Gauss-Krüger `(norte, este)` o tradicional `(este, norte)`.
- Soporta coordenadas geográficas en formatos DMS, DMM y grados decimales.
- Utiliza mediciones elipsoidales para CRS geográficos mediante `QgsDistanceArea`.
- Muestra advertencias adaptativas para mediciones de superficie y longitud sobre CRS geográficos.
- Copia automáticamente las coordenadas y las medidas al portapapeles.
