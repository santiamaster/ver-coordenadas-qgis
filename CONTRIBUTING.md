# Contribuir a Ver Coordenadas

Gracias por el interés en colaborar con **Ver Coordenadas**.

Este documento está dirigido a desarrolladores que quieran estudiar el código, proponer mejoras, corregir errores o enviar cambios al proyecto.

## Requisitos

- **QGIS 4.2 o superior**.
- Python incluido con la instalación de QGIS.
- PyQGIS.
- Qt6 a través de `qgis.PyQt`.

El complemento no requiere dependencias externas de Python.

## Estructura del código

El código principal se encuentra en la carpeta `ver_coordenadas/`.

- `__init__.py`: punto de entrada del complemento para QGIS.
- `plugin.py`: registra y elimina la acción contextual **Ver coordenadas** y coordina la ejecución sobre entidades.
- `geometry.py`: extrae polígonos, líneas, multipartes, huecos y vértices.
- `formatter.py`: aplica los formatos de coordenadas y presenta áreas y longitudes.
- `measurements.py`: resuelve las mediciones proyectadas y geográficas, incluyendo `QgsDistanceArea` cuando corresponde.
- `dialog.py`: contiene la interfaz de usuario del complemento.
- `warning.py`: define los avisos mostrados para mediciones realizadas sobre CRS geográficos.
- `metadata.txt`: contiene los metadatos requeridos por QGIS.

Las capturas de documentación se encuentran en `screenshots/` y la documentación de pruebas se organiza en `tests/`.

## Obtener el código fuente

Puede clonar el repositorio con Git:

```bash
git clone https://github.com/santiamaster/ver-coordenadas-qgis.git
cd ver-coordenadas-qgis
```

También puede crear un fork desde GitHub si desea enviar cambios mediante Pull Request.

## Instalar una copia de desarrollo en QGIS

QGIS carga los complementos desde la carpeta de plugins del perfil activo.

Para trabajar con el código fuente:

1. Localice la carpeta de plugins del perfil de QGIS que utiliza para desarrollo.
2. Copie o enlace la carpeta `ver_coordenadas/` del repositorio dentro de esa carpeta de plugins.
3. Inicie o reinicie QGIS.
4. Abra **Complementos → Administrar e instalar complementos**.
5. Active **Ver Coordenadas**.

Durante el desarrollo conviene utilizar un perfil de QGIS separado del entorno de trabajo habitual.

## Flujo recomendado para contribuir

1. Cree un fork del repositorio si no tiene permisos directos de escritura.
2. Cree una rama específica para el cambio.

Ejemplos:

```bash
git checkout -b fix/descripcion-del-error
```

```bash
git checkout -b feature/nombre-de-la-mejora
```

3. Realice cambios pequeños y enfocados.
4. Pruebe el comportamiento modificado en QGIS 4.2 o superior.
5. Actualice la documentación cuando el cambio afecte el uso del complemento.
6. Envíe un Pull Request hacia la rama `main` explicando qué problema resuelve y cómo fue probado.

## Criterios de desarrollo

Al contribuir, procure respetar estas reglas:

- Mantener compatibilidad con **QGIS 4.2 o superior** salvo que un cambio de versión sea previamente discutido.
- Importar Qt mediante `qgis.PyQt`; no utilizar `PyQt6` directamente.
- Evitar dependencias externas cuando PyQGIS, Qt o la biblioteca estándar de Python resuelvan el problema.
- Mantener nombres de variables, clases y funciones descriptivos.
- Mantener separadas las responsabilidades de geometría, medición, formato e interfaz.
- No incorporar credenciales, direcciones internas, datos sensibles ni configuraciones específicas de una organización.
- Actualizar `CHANGELOG.md` cuando un cambio vaya a formar parte de una nueva versión.
- Mantener los encabezados de copyright y la licencia del proyecto.

## Licencia de las contribuciones

Al enviar una contribución al proyecto, acepta que su aporte se distribuya bajo la misma licencia del repositorio:

**GNU General Public License v2.0 o posterior (GPL-2.0-or-later)**.

Consulte el archivo [`LICENSE`](LICENSE) para conocer los términos completos.

## Pruebas

La carpeta `tests/` contiene la matriz formal y la batería automatizada del complemento.

La versión 1.0.0 dispone de pruebas para:

- formatos de coordenadas proyectadas;
- DMS, DMM y DD;
- Polygon y MultiPolygon;
- huecos;
- LineString y MultiLineString;
- áreas y longitudes proyectadas;
- mediciones geográficas;
- advertencias adaptativas;
- ciclo de vida de la acción del plugin;
- portapapeles y preferencias;
- rechazo de geometrías curvas;
- validación de CRS inválidos y unidades desconocidas.

La matriz completa se encuentra en `tests/TEST_MATRIX.md`. La batería automatizada se ejecuta con `unittest`; los niveles que dependen de PyQGIS/Qt deben verificarse dentro de un entorno real de QGIS 4.2 o superior.

Además de las pruebas automatizadas, los cambios que afecten al comportamiento visible del complemento deben validarse manualmente en QGIS.

## Reportar errores y proponer mejoras

Para errores o solicitudes de funcionalidad utilice los formularios de Issues:

https://github.com/santiamaster/ver-coordenadas-qgis/issues/new/choose

Antes de abrir un Pull Request para una modificación grande, es recomendable crear primero un Issue para discutir el alcance y evitar trabajo duplicado.
