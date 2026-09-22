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

Estado: **preparado; pendiente de ejecución local y verificación del artefacto**.

Se agregó `scripts/build_release.ps1` para construir de forma reproducible el ZIP candidato desde la copia local actualizada del repositorio.

El script:

- toma únicamente los diez archivos aprobados de `ver_coordenadas/`;
- construye una única carpeta raíz `ver_coordenadas/` dentro del ZIP;
- excluye automáticamente archivos de desarrollo, cachés y cualquier contenido no incluido en el manifiesto;
- valida que no falten archivos obligatorios;
- falla si detecta entradas inesperadas;
- muestra el contenido final del ZIP;
- informa tamaño y SHA-256 del artefacto.

Nombre previsto del candidato: `dist/ver_coordenadas-1.0.0.zip`.

### Próximo subpaso

Ejecutar el script sobre una copia local sincronizada, conservar su salida y utilizar el ZIP resultante para **7.5 — Inspección del ZIP**.
