import unittest

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    QgsProject,
)

from ver_coordenadas.measurements import GeometryMeasurementCalculator


class QgisTestCase(unittest.TestCase):
    """Inicializa QGIS Core solo cuando la suite corre fuera de una instancia activa."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._owns_qgis_app = QgsApplication.instance() is None
        cls._qgis_app = None
        if cls._owns_qgis_app:
            cls._qgis_app = QgsApplication([], False)
            cls._qgis_app.initQgis()

    @classmethod
    def tearDownClass(cls):
        if cls._owns_qgis_app and cls._qgis_app is not None:
            cls._qgis_app.exitQgis()
        super().tearDownClass()


class ProjectedMeasurementTests(QgisTestCase):
    def test_crs_01_projected_metric_length_and_area_are_metric(self):
        crs = QgsCoordinateReferenceSystem("EPSG:22183")
        self.assertTrue(crs.isValid())
        project = QgsProject()

        calculator = GeometryMeasurementCalculator(crs, project)
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 3 4)")
        polygon = QgsGeometry.fromWkt(
            "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"
        )

        self.assertAlmostEqual(calculator.measure_length(line), 5.0, places=6)
        self.assertAlmostEqual(calculator.measure_area(polygon), 100.0, places=6)

    def test_crs_02_projected_feet_are_converted_to_meters(self):
        crs = QgsCoordinateReferenceSystem("EPSG:2277")
        self.assertTrue(crs.isValid())
        self.assertFalse(crs.isGeographic())
        project = QgsProject()

        calculator = GeometryMeasurementCalculator(crs, project)
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 1000 0)")

        measured_meters = calculator.measure_length(line)

        self.assertGreater(measured_meters, 304.7)
        self.assertLess(measured_meters, 304.9)


class GeographicMeasurementTests(QgisTestCase):
    def test_crs_03_epsg_4326_uses_ellipsoidal_length(self):
        crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.assertTrue(crs.isValid())
        project = QgsProject()
        project.setEllipsoid("WGS84")

        calculator = GeometryMeasurementCalculator(crs, project)
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 1 0)")

        measured_meters = calculator.measure_length(line)

        self.assertTrue(calculator.is_geographic)
        self.assertGreater(measured_meters, 111_000)
        self.assertLess(measured_meters, 112_000)

    def test_crs_04_project_ellipsoid_produces_valid_geographic_area(self):
        crs = QgsCoordinateReferenceSystem("EPSG:4326")
        project = QgsProject()
        project.setEllipsoid("WGS84")

        calculator = GeometryMeasurementCalculator(crs, project)
        polygon = QgsGeometry.fromWkt(
            "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
        )

        measured_square_meters = calculator.measure_area(polygon)

        self.assertGreater(measured_square_meters, 12_000_000_000)
        self.assertLess(measured_square_meters, 13_000_000_000)

    def test_crs_05_project_without_ellipsoid_falls_back_to_source_crs(self):
        crs = QgsCoordinateReferenceSystem("EPSG:4326")
        project = QgsProject()
        project.setEllipsoid("NONE")

        calculator = GeometryMeasurementCalculator(crs, project)
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 1 0)")

        measured_meters = calculator.measure_length(line)

        self.assertGreater(measured_meters, 111_000)
        self.assertLess(measured_meters, 112_000)


class InvalidCrsRegressionTests(QgisTestCase):
    @unittest.expectedFailure
    def test_crs_07_invalid_crs_should_be_rejected_before_reporting_metric_units(self):
        crs = QgsCoordinateReferenceSystem()
        self.assertFalse(crs.isValid())
        project = QgsProject()
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 3 4)")

        with self.assertRaisesRegex(ValueError, "CRS"):
            calculator = GeometryMeasurementCalculator(crs, project)
            calculator.measure_length(line)

    @unittest.expectedFailure
    def test_crs_08_unknown_projected_units_should_be_rejected(self):
        class UnknownUnitCrs:
            def isGeographic(self):
                return False

            def isValid(self):
                return True

            def mapUnits(self):
                return Qgis.DistanceUnit.Unknown

        project = QgsProject()
        line = QgsGeometry.fromWkt("LINESTRING (0 0, 3 4)")

        with self.assertRaisesRegex(ValueError, "unidad"):
            calculator = GeometryMeasurementCalculator(UnknownUnitCrs(), project)
            calculator.measure_length(line)


if __name__ == "__main__":
    unittest.main()
