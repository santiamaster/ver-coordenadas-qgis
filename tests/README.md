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

Los casos `CUR-01`, `CUR-02`, `CRS-07` y `CRS-08` forman parte de la batería normal de regresión. Verifican que la versión 1.0.0:

- rechace geometrías curvas de forma explícita;
- rechace CRS inválidos o unidades desconocidas antes de presentar medidas como metros o metros cuadrados.

El Nivel B fue verificado dentro de QGIS 4.2 como parte de la revisión técnica de la versión 1.0.0.

## Ejecución del Nivel C — integración Qt/QGIS

Las pruebas del diálogo y del ciclo de vida del plugin deben ejecutarse dentro de QGIS 4.2, donde ya existe una aplicación Qt/QGIS activa.

Desde la Consola Python de QGIS, con la raíz del repositorio agregada a `sys.path`, ejecutar:

```python
import unittest

suite = unittest.defaultTestLoader.loadTestsFromNames([
    "tests.test_dialog",
    "tests.test_plugin",
])

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
```

Resumen recomendado:

```python
print("Ejecutados:", result.testsRun)
print("Fallos:", len(result.failures))
print("Errores:", len(result.errors))
print("Expected failures:", len(result.expectedFailures))
print("Unexpected successes:", len(result.unexpectedSuccesses))
```

Después debe volver a ejecutarse la batería completa con `unittest` para comprobar que los niveles A, B y C conviven sin regresiones.

El Nivel C fue verificado dentro de QGIS 4.2. La ejecución conjunta de los niveles A, B y C completó 68 pruebas sin fallos ni errores.
