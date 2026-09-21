# Tests

Esta carpeta reúne la documentación de pruebas y alojará la batería automatizada del complemento **Ver Coordenadas**.

La matriz formal para la publicación 1.0.0 se encuentra en [`TEST_MATRIX.md`](TEST_MATRIX.md). Allí se definen los casos de prueba, resultados esperados, prioridades y el tipo de validación previsto para cada caso.

La implementación de las pruebas se organiza en tres niveles:

- **Nivel A**: lógica sin interfaz gráfica, principalmente `formatter.py` y `warning.py`.
- **Nivel B**: pruebas con PyQGIS para `geometry.py` y `measurements.py`.
- **Nivel C**: integración Qt/QGIS para `dialog.py` y `plugin.py`.

Además de la automatización, la versión 1.0.0 deberá superar una verificación manual final dentro de QGIS 4.2.

## Ejecución del Nivel A

Las pruebas del Nivel A usan `unittest` de la biblioteca estándar y stubs mínimos de `qgis.core`, por lo que pueden ejecutarse fuera de una instalación de QGIS:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Los niveles B y C requieren un entorno con PyQGIS/Qt disponible.

## Ejecución del Nivel B — PyQGIS

Las pruebas de geometría y mediciones requieren una instalación real de QGIS con PyQGIS disponible.

Desde un entorno de Python configurado por QGIS, situado en la raíz del repositorio:

```bash
python -m unittest tests.test_geometry tests.test_measurements -v
```

También puede ejecutarse toda la batería disponible con:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Los casos `CUR-01`, `CUR-02`, `CRS-07` y `CRS-08` están marcados temporalmente con `@unittest.expectedFailure`. Representan hallazgos conocidos de la auditoría 6.1 y fijan el comportamiento deseado para la fase 6.4:

- rechazar geometrías curvas en la versión 1.0.0;
- rechazar CRS inválidos o unidades desconocidas antes de presentar medidas como metros o metros cuadrados.

El Nivel B no se considerará verificado hasta ejecutar esta batería dentro de un entorno real de QGIS/PyQGIS.
