# Ver Coordenadas

**Ver Coordenadas** es un complemento para QGIS que permite consultar y copiar rápidamente los vértices y las medidas de entidades vectoriales lineales y poligonales desde una acción contextual.

## Compatibilidad

- QGIS 4.2 o superior.
- Polygon y MultiPolygon.
- LineString y MultiLineString.

## Características principales

- Lista los vértices de la entidad seleccionada con numeración continua.
- Evita repetir el vértice de cierre de los anillos poligonales.
- Identifica los huecos de los polígonos.
- Calcula el área neta de cada polígono y el área individual de cada hueco.
- Calcula áreas totales para MultiPolygon.
- Calcula longitudes individuales y totales para geometrías lineales.
- Copia automáticamente coordenadas y medidas al portapapeles.

### CRS proyectados

Permite elegir entre:

- **Gauss-Krüger (norte, este)**, predeterminado.
- **Coordenadas tradicionales (este, norte)**.

Las medidas se obtienen de forma planimétrica y se presentan en metros, metros cuadrados, kilómetros y hectáreas según corresponda.

### CRS geográficos

Permite elegir entre:

- **Grados, minutos y segundos (DMS)**, predeterminado.
- **Grados y minutos decimales (DMM)**.
- **Grados decimales (DD)**.

Para CRS geográficos, el complemento utiliza `QgsDistanceArea` para realizar mediciones elipsoidales. La interfaz advierte que las superficies o longitudes mostradas son aproximadas y que, para una medición planimétrica de mayor precisión, debe utilizarse la geometría en un sistema de coordenadas plano.

## Estado de la versión

La funcionalidad de **1.0.0** está congelada y validada en QGIS 4.2. El repositorio se encuentra en preparación para la publicación oficial del complemento.

## Autoría

**Secretaría de Minería de Salta**  
Desarrollado y mantenido por: **Carlos Daniel Santiápichi Mastrolinardo**  
Contacto: **mineriayenergia@produccionsalta.gob.ar**

## Licencia

Este proyecto se distribuye bajo la **GNU General Public License v2.0 o posterior (GPL-2.0-or-later)**.

Consulte el archivo [`LICENSE`](LICENSE) para conocer los términos completos.
