# Auditoría de publicación — Ver Coordenadas 1.0.0

Este documento registra las verificaciones previas a la publicación del complemento en el repositorio oficial de plugins de QGIS.

## Paso 7 — Pruebas de publicación y seguridad

### 7.1 Auditoría del contenido del paquete

Estado: **completado**.

El paquete candidato debe contener únicamente la carpeta raíz `ver_coordenadas/` con los siguientes archivos:

```text
ver_coordenadas/
├── __init__.py
├── plugin.py
├── geometry.py
├── measurements.py
├── formatter.py
├── dialog.py
├── warning.py
├── metadata.txt
├── LICENSE
└── icon.png
```

Comprobaciones realizadas:

- `metadata.txt` está dentro de la carpeta del plugin.
- `__init__.py` está dentro de la carpeta del plugin.
- `LICENSE` está dentro de la carpeta del plugin.
- `icon.png` está dentro de la carpeta del plugin.
- No se detectaron `__pycache__`, `*.pyc`, `*.pyo`, `.DS_Store`, `Thumbs.db`, `Desktop.ini`, ZIP anidados, ejecutables, DLL, bibliotecas compartidas ni proyectos temporales de QGIS.
- `.gitignore` excluye cachés de Python, entornos virtuales, archivos de IDE/SO y artefactos de build/release.
- El ZIP final no debe incluir `tests/`, `screenshots/`, `.github/`, documentación de desarrollo ni archivos del repositorio externos a `ver_coordenadas/`.

### 7.2 Auditoría de seguridad orientada al validador de QGIS

Estado: **completado a nivel estático del código fuente**.

Se revisaron los módulos Python incluidos en `ver_coordenadas/` buscando patrones asociados a los controles automáticos del repositorio oficial de QGIS.

Resultados:

- No se utiliza `subprocess`, `os.system` ni ejecución de shell.
- No se utiliza `eval()`, el built-in `exec()`, `pickle` ni `marshal`.
- No se utilizan `requests`, `urllib`, sockets ni otros accesos de red.
- El plugin no realiza descargas ni llamadas a servicios externos.
- No se detectaron contraseñas, tokens, claves API ni cabeceras de autorización embebidas.
- No se detectaron escrituras, borrados o cambios de permisos arbitrarios sobre archivos.
- `QSettings` se usa únicamente para recordar la preferencia de formato del usuario.
- `Path(__file__).with_name("icon.png")` se usa únicamente para localizar el icono distribuido con el plugin.
- La llamada `coordinates_dialog.exec()` corresponde al método modal de `QDialog`; no es uso del built-in Python `exec()`.
- No existen dependencias Python externas: el código utiliza PyQGIS, `qgis.PyQt` y biblioteca estándar.
- El único recurso no textual del paquete es `icon.png`, que es un recurso gráfico y no un binario ejecutable.

### Herramientas del escaneo oficial

El repositorio oficial de QGIS ejecuta automáticamente controles con Bandit, detect-secrets, Flake8 y análisis de archivos al subir cada versión. La auditoría local de este paso busca anticipar esos controles, pero el resultado definitivo será el escaneo realizado por el repositorio oficial al cargar el ZIP.

### 7.3 Validación formal de `metadata.txt`

Estado: **completado**.

Comprobaciones realizadas:

- `name`, `description`, `version`, `qgisMinimumVersion`, `author`, `email` y `about` están presentes.
- La descripción corta y el campo `about` están redactados en inglés para la publicación pública.
- `repository`, `homepage` y `tracker` apuntan al repositorio público y a su sistema de Issues.
- `category=Vector` es coherente con la función del complemento.
- `tags` utiliza términos en inglés.
- `icon=icon.png` apunta a un recurso presente dentro del paquete.
- `experimental=False` y `deprecated=False`.
- `qgisMinimumVersion=4.2`.
- Se declaró explícitamente `qgisMaximumVersion=4.99` para identificar la versión como compatible con la línea QGIS 4.x en el repositorio oficial.
- `version=1.0.0` y el changelog corresponden a la primera versión pública.
- `LICENSE` está incluido como archivo independiente dentro de la carpeta del plugin.

### 7.4 Construcción del ZIP candidato de publicación

Estado: **completado**.

Se agregó `scripts/build_release.ps1` para construir de forma reproducible el ZIP candidato desde la copia local actualizada del repositorio.

La primera ejecución local generó un archivo de 49.083 bytes con SHA-256:

`98854926C41B5BD4299FF39D761FAC8FD71397AD8AF94E52A3C57E66D231CC70`

La inspección inmediata del ZIP detectó que `Compress-Archive` había almacenado las rutas internas con barra invertida (`ver_coordenadas\\archivo`) por haberse construido en Windows. Aunque el contenido era correcto, ese formato de ruta no es suficientemente portable para un paquete destinado a Windows, Linux y macOS.

Se corrigió `scripts/build_release.ps1` para construir el ZIP mediante `System.IO.Compression.ZipArchive`, crear explícitamente las entradas con rutas `ver_coordenadas/archivo` y fallar si aparece cualquier barra invertida dentro del archivo ZIP.

El script mantiene además estas garantías:

- toma únicamente los diez archivos aprobados de `ver_coordenadas/`;
- construye una única carpeta raíz `ver_coordenadas/` dentro del ZIP;
- excluye automáticamente archivos de desarrollo, cachés y cualquier contenido no incluido en el manifiesto;
- valida que no falten archivos obligatorios;
- falla si detecta entradas inesperadas;
- muestra el contenido final del ZIP;
- informa tamaño y SHA-256 del artefacto.

Nombre previsto del candidato: `dist/ver_coordenadas-1.0.0.zip`.

La segunda ejecución local, realizada con el script corregido, generó el candidato definitivo para inspección:

- Archivo: `ver_coordenadas-1.0.0.zip`
- Tamaño: 49.083 bytes.
- SHA-256: `CA183AFFE65BC2771E688C57FC2793B88B9D70B6F973681D941BDAAB26F569B8`
- Las rutas internas utilizan exclusivamente `/`.

### 7.5 Inspección del ZIP

Estado: **completado**.

Se inspeccionó directamente el artefacto generado en 7.4.

Resultados:

- Integridad ZIP: OK.
- El SHA-256 y el tamaño coinciden con los informados por el script de construcción.
- Contiene exactamente los diez archivos aprobados, sin entradas adicionales.
- Todas las entradas están bajo una única carpeta raíz `ver_coordenadas/`.
- No existen rutas absolutas, secuencias `../` ni barras invertidas.
- Los siete módulos Python incluidos compilan sintácticamente sin errores.
- `metadata.txt` se puede interpretar correctamente y declara:
  - `version=1.0.0`
  - `qgisMinimumVersion=4.2`
  - `qgisMaximumVersion=4.99`
  - `category=Vector`
  - `experimental=False`
  - `deprecated=False`
- `icon.png` es un PNG válido de 256 × 256 px.
- `LICENSE` contiene la GNU General Public License Version 2.

### 7.6 Instalación limpia desde el ZIP candidato en QGIS 4.2

Estado: **completado**.

Se realizó una instalación limpia en QGIS 4.2 utilizando exactamente el ZIP candidato generado e inspeccionado en las fases 7.4 y 7.5:

- Archivo: `ver_coordenadas-1.0.0.zip`
- SHA-256: `CA183AFFE65BC2771E688C57FC2793B88B9D70B6F973681D941BDAAB26F569B8`

La versión anterior del complemento fue retirada antes de instalar el candidato desde ZIP.

Pruebas de humo realizadas sobre el paquete instalado:

- `SMOKE-01` Carga del plugin: OK.
- `SMOKE-02` Icono de la acción: OK.
- `SMOKE-03` Polygon proyectado: OK.
- `SMOKE-04` LineString proyectado: OK.
- `SMOKE-05` CRS geográfico y aviso correspondiente: OK.
- `SMOKE-06` Cambio entre formatos de coordenadas: OK.
- `SMOKE-07` Copia automática al portapapeles: OK.
- `SMOKE-08` Persistencia del último formato seleccionado: OK.
- `SMOKE-09` Capa Point no soportada: OK.
- `SMOKE-10` Ciclo desactivar/activar sin acciones duplicadas: OK.

Resultado: **10/10 pruebas de humo superadas**.

### 7.7 Revisión final previa a subir

Estado: **completado**.

Se realizó la revisión final del estado del repositorio, la documentación, los metadatos, las pruebas y el ZIP candidato antes de iniciar el proceso de publicación en el repositorio oficial de plugins de QGIS.

Checklist final:

- Nombre de carpeta del plugin: `ver_coordenadas`, válido para el repositorio oficial.
- `metadata.txt`, `__init__.py` y `LICENSE` presentes en la raíz de la carpeta del plugin.
- `version=1.0.0`.
- Compatibilidad declarada: QGIS 4.2 a 4.99.
- Descripción corta en inglés y campo `about` con descripción detallada de la funcionalidad.
- Repositorio, página principal y tracker configurados hacia el repositorio público de GitHub.
- Licencia: GPL-2.0-or-later.
- Sin dependencias Python externas.
- Sin binarios ejecutables ni bibliotecas compiladas.
- Tamaño del ZIP candidato: 49.083 bytes, ampliamente por debajo del límite del repositorio oficial.
- Auditoría estática de seguridad completada sin hallazgos críticos conocidos.
- Suite automatizada final: 69 pruebas, 0 fallos, 0 errores, 0 expected failures y 0 unexpected successes.
- Verificación manual QGIS 4.2 completada.
- Instalación limpia desde el ZIP candidato completada.
- Pruebas de humo del ZIP instalado: 10/10 OK.
- Icono final incluido y verificado.
- Declaración de asistencia de inteligencia artificial documentada en el README y revisada institucionalmente.
- El ZIP candidato que debe conservarse sin modificaciones para el siguiente paso es:
  - `ver_coordenadas-1.0.0.zip`
  - SHA-256: `CA183AFFE65BC2771E688C57FC2793B88B9D70B6F973681D941BDAAB26F569B8`

Observación: el repositorio oficial ejecutará sus propios controles automáticos al subir el ZIP. La aprobación final depende de superar esa validación y, para usuarios sin permisos de aprobación, de la revisión del equipo de QGIS.

## Resultado del Paso 7

**Paso 7 — Pruebas de publicación y seguridad: COMPLETADO.**

El complemento y su ZIP candidato quedan listos para avanzar al **Paso 8 — OSGEO ID y preparación de la subida al repositorio oficial de QGIS**.
