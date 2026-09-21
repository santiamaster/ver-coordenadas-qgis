# Matriz formal de pruebas — Ver Coordenadas 1.0.0

Esta matriz define los casos que deben verificarse antes de publicar la versión **1.0.0** del complemento.

## Prioridades

- **P0**: imprescindible; si falla, la versión no debe publicarse.
- **P1**: importante; debe quedar cubierto antes de publicar.
- **P2**: robustez y casos límite.
- **P3**: complementario o futuro.

## Matriz

| ID | Área | Caso | Resultado esperado | Tipo | Prioridad |
| --- | --- | --- | --- | --- | --- |
| FMT-01 | Formato proyectado | Número positivo `3456789.14` | `3.456.789,14` | Automática | P0 |
| FMT-02 | Formato proyectado | Número negativo | Conserva signo y formato español | Automática | P1 |
| FMT-03 | Gauss-Krüger | Punto QGIS X=3456789, Y=7324567 | Presenta X=7324567, Y=3456789 | Automática | P0 |
| FMT-04 | Tradicional | Mismo punto | Presenta X=3456789, Y=7324567 | Automática | P0 |
| FMT-05 | Área <1 ha | 735 m² | `735 m²` | Automática | P0 |
| FMT-06 | Área >=1 ha | 100735 m² | `10 ha 0735 m²` | Automática | P0 |
| FMT-07 | Longitud <1 km | 347 m | `347 m` | Automática | P0 |
| FMT-08 | Longitud >=1 km | 5005 m | `5 km 005 m` | Automática | P0 |
| GEO-01 | DMS | Coordenadas positivas | DMS con hemisferios N/E | Automática | P0 |
| GEO-02 | DMS | Coordenadas negativas | Hemisferios S/W, sin signo negativo | Automática | P0 |
| GEO-03 | DMS | Segundos redondean a 60 | Acarreo correcto a minutos | Automática | P1 |
| GEO-04 | DMS | Minutos redondean a 60 | Acarreo correcto a grados | Automática | P1 |
| GEO-05 | DMM | Valores positivos/negativos | 6 decimales y hemisferios correctos | Automática | P0 |
| GEO-06 | DMM | Minutos redondean a 60 | Acarreo correcto a grados | Automática | P1 |
| GEO-07 | DD | Valores negativos | Valor absoluto + S/W | Automática | P0 |
| GEO-08 | DD | Valor 0 | Presentación N/E actual documentada | Automática | P2 |
| POL-01 | Polygon | Cuadrado cerrado | Elimina solo vértice final duplicado | Automática QGIS | P0 |
| POL-02 | Polygon | Anillo sin cierre duplicado | No elimina vértice válido | Automática QGIS | P1 |
| POL-03 | Polygon + hueco | 1 exterior + 1 hueco | Exterior y hueco separados | Automática QGIS | P0 |
| POL-04 | Polygon + huecos | 2+ huecos | Huecos numerados correctamente | Automática QGIS | P1 |
| POL-05 | Área con hueco | Exterior 100, hueco 20 | Área principal 80; hueco 20 | Automática QGIS | P0 |
| POL-06 | MultiPolygon | 2 partes | `Polígono 1`, `Polígono 2` | Automática QGIS | P0 |
| POL-07 | MultiPolygon | Partes con huecos | Total suma solo áreas netas | Automática QGIS | P0 |
| POL-08 | Numeración | MultiPolygon + huecos | Numeración continua | Automática | P0 |
| LIN-01 | LineString | Línea simple | Conserva todos los extremos | Automática QGIS | P0 |
| LIN-02 | MultiLineString | 2 partes | `Línea 1`, `Línea 2` | Automática QGIS | P0 |
| LIN-03 | MultiLineString | Varias partes | Total = suma de partes | Automática QGIS | P0 |
| LIN-04 | Numeración | MultiLineString | Numeración continua | Automática | P0 |
| CRS-01 | Proyectado métrico | CRS métrico válido | Longitud/área correcta en m/m² | Automática QGIS + manual | P0 |
| CRS-02 | Proyectado no métrico | CRS en pies | Convierte correctamente a m/m² | Automática QGIS | P1 |
| CRS-03 | Geográfico | EPSG:4326 | Usa `QgsDistanceArea` | Automática QGIS | P0 |
| CRS-04 | Geográfico | Proyecto con elipsoide | Usa elipsoide del proyecto | Automática QGIS | P1 |
| CRS-05 | Geográfico | Proyecto sin elipsoide útil | Usa elipsoide del CRS como fallback | Automática QGIS | P0 |
| CRS-06 | Geográfico | Sin elipsoide válido | Error claro y controlado | Automática QGIS | P1 |
| CRS-07 | CRS inválido | CRS no válido | No etiqueta medidas desconocidas como m/m² | Automática QGIS | P0 |
| CRS-08 | Unidades desconocidas | Unidad `Unknown` | Falla de forma controlada | Automática QGIS | P0 |
| UI-01 | Selector | CRS proyectado | Solo Gauss-Krüger + tradicional | Manual/Qt | P0 |
| UI-02 | Selector | CRS geográfico | Solo DMS + DMM + DD | Manual/Qt | P0 |
| UI-03 | Preferencia | Formato proyectado | Se recuerda al reabrir | Manual/Qt | P1 |
| UI-04 | Preferencia | Formato geográfico | Se recuerda de forma independiente | Manual/Qt | P1 |
| UI-05 | Preferencia inválida | Valor no reconocido | Vuelve al valor por defecto | Automática Qt | P1 |
| UI-06 | Portapapeles | Abrir diálogo | Copia automática | Manual/Qt | P0 |
| UI-07 | Portapapeles | Cambiar formato | Portapapeles se actualiza | Manual/Qt | P1 |
| UI-08 | Ventana | Coordenadas largas | Scroll funciona y no hay wrap | Manual | P1 |
| UI-09 | Advertencia | CRS proyectado | No se muestra aviso | Automática/Manual | P0 |
| UI-10 | Advertencia | Polígono geográfico | Aviso de superficie | Automática/Manual | P0 |
| UI-11 | Advertencia | Línea geográfica | Aviso de longitud | Automática/Manual | P0 |
| UI-12 | Advertencia | Multipartes | Aviso aparece una sola vez | Manual | P1 |
| ACT-01 | Acción QGIS | Capa Polygon | Acción disponible | Manual | P0 |
| ACT-02 | Acción QGIS | Capa LineString | Acción disponible | Manual | P0 |
| ACT-03 | Acción QGIS | Capa Point | Acción no disponible | Manual | P0 |
| ACT-04 | Acción QGIS | Feature sin geometría | No se ejecuta o informa error controlado | Manual | P1 |
| ACT-05 | Ciclo plugin | Activar/desactivar | Acción se registra y elimina correctamente | Manual | P0 |
| ACT-06 | Ciclo plugin | Repetir activación/desactivación | No quedan acciones duplicadas | Manual | P1 |
| ERR-01 | Geometría nula | `None` | Mensaje/error controlado | Automática | P0 |
| ERR-02 | Geometría vacía | `isEmpty()` | Mensaje/error controlado | Automática QGIS | P0 |
| ERR-03 | Geometría Point | No soportada | `ValueError` claro | Automática QGIS | P0 |
| ERR-04 | Geometría degenerada | Sin vértices utilizables | Error controlado | Automática QGIS | P2 |
| CUR-01 | Curvas | CircularString | Rechazar o documentar segmentización | Automática QGIS | P1 |
| CUR-02 | Curvas | CurvePolygon | Rechazar o documentar segmentización | Automática QGIS | P1 |
| CUR-03 | Curvas multipartes | MultiCurve/MultiSurface | Comportamiento explícito y consistente | Automática QGIS | P2 |
| DIM-01 | Dimensión Z | LineStringZ | XY correctas; Z ignorada explícitamente | Automática QGIS | P1 |
| DIM-02 | Dimensión Z | PolygonZ | XY/área correctas según criterio definido | Automática QGIS | P1 |
| DIM-03 | Dimensión M | Geometría M | M no altera salida XY | Automática QGIS | P2 |
| NUM-01 | Valores extremos | Coordenadas proyectadas grandes | Formato correcto | Automática | P2 |
| NUM-02 | Valores extremos | Cerca de cero | Sin errores de formato | Automática | P2 |
| NUM-03 | Límites geográficos | Lat 90 / lon 180 | Formato válido | Automática | P1 |
| NUM-04 | Datos anómalos | Ángulos fuera de rango | Comportamiento definido | Automática | P2 |
| SEC-01 | Dependencias | Código completo | Sin red, shell ni dependencias externas | Estática | P0 |
| SEC-02 | Datos sensibles | Código/repositorio | Sin credenciales ni rutas internas | Estática | P0 |
| META-01 | Metadata | `metadata.txt` | Campos obligatorios válidos | Estática | P0 |
| META-02 | Icono | `icon.png` | Existe en el directorio del plugin | Estática | P0 |
| META-03 | Licencia | Paquete final | `LICENSE` dentro del plugin | Empaquetado | P0 |

## Decisiones pendientes

### CRS inválido o unidades desconocidas

El complemento no debe presentar una medida como metros o metros cuadrados si no puede demostrar que la conversión es válida. La batería de pruebas deberá fijar este comportamiento antes de modificar el código.

### Geometrías curvas

La versión 1.0.0 declara soporte para Polygon, MultiPolygon, LineString y MultiLineString. Las geometrías curvas deberán probarse expresamente para decidir entre:

1. rechazarlas con un mensaje claro en 1.0.0; o
2. documentar y aceptar la segmentización realizada por QGIS.

La opción preferida para 1.0.0 es rechazarlas de forma explícita y considerar soporte de curvas como una mejora futura.

## Capas de automatización

### Nivel A — lógica sin interfaz

- `formatter.py`
- `warning.py`

### Nivel B — PyQGIS

- `geometry.py`
- `measurements.py`

### Nivel C — integración Qt/QGIS

- `dialog.py`
- `plugin.py`

La prueba manual final dentro de QGIS 4.2 sigue siendo obligatoria aunque todas las pruebas automatizadas resulten correctas.

## Estado

- [x] Matriz definida.
- [x] Pruebas Nivel A implementadas.
- [x] Pruebas Nivel B implementadas.
- [x] Pruebas Nivel C implementadas.
- [x] Pruebas manuales finales ejecutadas.
- [x] Hallazgos corregidos y regresiones verificadas.

## Verificación del Nivel B

Ejecutada manualmente dentro de QGIS 4.2 el 2026-09-21.

- Pruebas del Nivel B: 25 ejecutadas.
- Suite completa disponible: 51 ejecutadas.
- Fallos: 0.
- Errores: 0.
- Expected failures: 4.
- Unexpected successes: 0.

Los cuatro `expected failure` corresponden a los hallazgos conocidos que se corregirán en la fase 6.4:

- `CUR-01`: CircularString debe rechazarse en 1.0.0.
- `CUR-02`: CurvePolygon debe rechazarse en 1.0.0.
- `CRS-07`: CRS inválido debe rechazarse antes de informar unidades métricas.
- `CRS-08`: unidades proyectadas desconocidas deben rechazarse antes de informar unidades métricas.

## Verificación del Nivel C

Ejecutada manualmente dentro de QGIS 4.2 el 2026-09-21.

- Pruebas del Nivel C: 17 ejecutadas.
- Fallos: 0.
- Errores: 0.
- Expected failures: 0.
- Unexpected successes: 0.

## Verificación conjunta A + B + C

Ejecutada manualmente dentro de QGIS 4.2 el 2026-09-21.

- Total de pruebas: 68.
- Fallos: 0.
- Errores: 0.
- Expected failures: 4.
- Unexpected successes: 0.

Los cuatro `expected failure` siguen correspondiendo únicamente a `CUR-01`, `CUR-02`, `CRS-07` y `CRS-08`, ya identificados para corrección en la fase 6.4.

## Verificación de la fase 6.4

Ejecutada manualmente dentro de QGIS 4.2 el 2026-09-21 después de corregir los hallazgos de geometrías curvas y validación de CRS.

- Total de pruebas: 68.
- Fallos: 0.
- Errores: 0.
- Expected failures: 0.
- Unexpected successes: 0.

Los casos `CUR-01`, `CUR-02`, `CRS-07` y `CRS-08` pasan ahora como pruebas normales.

## Verificación manual final — fase 6.5

Ejecutada manualmente dentro de QGIS 4.2 el 2026-09-21 sobre el flujo de uso real del complemento.

- `MAN-01` Polígono proyectado: OK.
- `MAN-02` Línea proyectada: OK.
- `MAN-03` Polígono con hueco: OK.
- `MAN-04` Geometrías multipartes: OK.
- `MAN-05` Polígono EPSG:4326: OK.
- `MAN-06` Línea EPSG:4326: OK.
- `MAN-07` Preferencias proyectadas/geográficas independientes: OK.
- `MAN-08` Capa Point no soportada: OK.
- `MAN-09` Rechazo explícito de geometrías curvas: OK.
- `MAN-10` Rechazo de CRS inválido: OK.

Observaciones verificadas durante la prueba manual:

- La numeración de vértices se mantiene continua entre partes y huecos.
- Las áreas netas y áreas de huecos se presentan por separado, con total multipartes coherente.
- Los formatos geográficos DMS muestran hemisferios `S/W` sin signo negativo.
- Las longitudes de líneas se presentan en metros o kilómetros según corresponda.
- Las preferencias de formato se recuerdan de forma independiente para CRS proyectados y geográficos.
- Las geometrías curvas muestran el mensaje: `Las geometrías curvas no están soportadas en Ver Coordenadas 1.0.0.`
- Un CRS inválido muestra el mensaje: `El CRS de la capa no es válido; no se pueden calcular medidas confiables.`
