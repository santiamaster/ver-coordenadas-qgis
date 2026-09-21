import unittest

from qgis.core import QgsApplication, QgsGeometry, QgsPointXY

from ver_coordenadas.geometry import (
    GroupKind,
    _polygon_ring_without_closing_duplicate,
    extract_coordinate_groups,
)


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


class PolygonGeometryTests(QgisTestCase):
    def test_pol_01_closed_polygon_omits_duplicate_closing_vertex(self):
        geometry = QgsGeometry.fromWkt(
            "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].kind, GroupKind.POLYGON)
        self.assertEqual(len(groups[0].points), 4)
        self.assertEqual(
            [(point.x_value, point.y_value) for point in groups[0].points],
            [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)],
        )

    def test_pol_02_open_ring_helper_keeps_last_distinct_vertex(self):
        ring = [
            QgsPointXY(0, 0),
            QgsPointXY(10, 0),
            QgsPointXY(10, 10),
            QgsPointXY(0, 10),
        ]

        points = _polygon_ring_without_closing_duplicate(ring)

        self.assertEqual(len(points), 4)
        self.assertEqual((points[-1].x_value, points[-1].y_value), (0.0, 10.0))

    def test_pol_03_polygon_with_hole_creates_separate_groups(self):
        geometry = QgsGeometry.fromWkt(
            "POLYGON ("
            "(0 0, 10 0, 10 10, 0 10, 0 0),"
            "(2 2, 4 2, 4 4, 2 4, 2 2)"
            ")"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0].title, "Polígono 1")
        self.assertEqual(groups[0].kind, GroupKind.POLYGON)
        self.assertEqual(groups[1].title, "Polígono 1 - Hueco 1")
        self.assertEqual(groups[1].kind, GroupKind.HOLE)

    def test_pol_04_polygon_with_multiple_holes_numbers_them_in_order(self):
        geometry = QgsGeometry.fromWkt(
            "POLYGON ("
            "(0 0, 20 0, 20 20, 0 20, 0 0),"
            "(2 2, 4 2, 4 4, 2 4, 2 2),"
            "(10 10, 12 10, 12 12, 10 12, 10 10)"
            ")"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(
            [group.title for group in groups],
            ["Polígono 1", "Polígono 1 - Hueco 1", "Polígono 1 - Hueco 2"],
        )

    def test_pol_05_polygon_area_is_net_and_hole_area_is_individual(self):
        geometry = QgsGeometry.fromWkt(
            "POLYGON ("
            "(0 0, 10 0, 10 10, 0 10, 0 0),"
            "(2 2, 4 2, 4 4, 2 4, 2 2)"
            ")"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertAlmostEqual(groups[0].measurement, 96.0)
        self.assertAlmostEqual(groups[1].measurement, 4.0)

    def test_pol_06_multipolygon_creates_one_polygon_group_per_part(self):
        geometry = QgsGeometry.fromWkt(
            "MULTIPOLYGON ("
            "((0 0, 10 0, 10 10, 0 10, 0 0)),"
            "((20 0, 25 0, 25 5, 20 5, 20 0))"
            ")"
        )

        groups = extract_coordinate_groups(geometry)

        polygon_groups = [group for group in groups if group.kind == GroupKind.POLYGON]
        self.assertEqual([group.title for group in polygon_groups], ["Polígono 1", "Polígono 2"])
        self.assertEqual([group.measurement for group in polygon_groups], [100.0, 25.0])

    def test_pol_07_multipolygon_parts_keep_net_areas_when_holes_exist(self):
        geometry = QgsGeometry.fromWkt(
            "MULTIPOLYGON ("
            "((0 0, 10 0, 10 10, 0 10, 0 0),"
            "(2 2, 4 2, 4 4, 2 4, 2 2)),"
            "((20 0, 25 0, 25 5, 20 5, 20 0))"
            ")"
        )

        groups = extract_coordinate_groups(geometry)

        polygon_areas = [
            group.measurement for group in groups if group.kind == GroupKind.POLYGON
        ]
        hole_areas = [
            group.measurement for group in groups if group.kind == GroupKind.HOLE
        ]
        self.assertEqual(polygon_areas, [96.0, 25.0])
        self.assertEqual(hole_areas, [4.0])


class LineGeometryTests(QgisTestCase):
    def test_lin_01_linestring_keeps_both_endpoints(self):
        geometry = QgsGeometry.fromWkt("LINESTRING (0 0, 3 4)")

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].kind, GroupKind.LINE)
        self.assertEqual(
            [(point.x_value, point.y_value) for point in groups[0].points],
            [(0.0, 0.0), (3.0, 4.0)],
        )
        self.assertAlmostEqual(groups[0].measurement, 5.0)

    def test_lin_02_multilinestring_creates_one_group_per_part(self):
        geometry = QgsGeometry.fromWkt(
            "MULTILINESTRING ((0 0, 3 4), (10 0, 10 2))"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual([group.title for group in groups], ["Línea 1", "Línea 2"])
        self.assertEqual([group.kind for group in groups], [GroupKind.LINE, GroupKind.LINE])

    def test_lin_03_multilinestring_part_lengths_are_individual(self):
        geometry = QgsGeometry.fromWkt(
            "MULTILINESTRING ((0 0, 3 4), (10 0, 10 2))"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual([group.measurement for group in groups], [5.0, 2.0])


class ErrorHandlingTests(QgisTestCase):
    def test_err_01_none_geometry_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "geometría utilizable"):
            extract_coordinate_groups(None)

    def test_err_02_empty_geometry_is_rejected(self):
        geometry = QgsGeometry.fromWkt("LINESTRING EMPTY")

        with self.assertRaisesRegex(ValueError, "geometría utilizable"):
            extract_coordinate_groups(geometry)

    def test_err_03_point_geometry_is_rejected(self):
        geometry = QgsGeometry.fromWkt("POINT (1 2)")

        with self.assertRaisesRegex(ValueError, "polígonos y líneas"):
            extract_coordinate_groups(geometry)


class DimensionalGeometryTests(QgisTestCase):
    def test_dim_01_linestring_z_preserves_xy_and_ignores_z_in_output_model(self):
        geometry = QgsGeometry.fromWkt("LINESTRING Z (0 0 100, 3 4 200)")

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(
            [(point.x_value, point.y_value) for point in groups[0].points],
            [(0.0, 0.0), (3.0, 4.0)],
        )
        self.assertAlmostEqual(groups[0].measurement, 5.0)

    def test_dim_02_polygon_z_preserves_xy_and_planimetric_area(self):
        geometry = QgsGeometry.fromWkt(
            "POLYGON Z ((0 0 10, 10 0 20, 10 10 30, 0 10 40, 0 0 10))"
        )

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(len(groups[0].points), 4)
        self.assertAlmostEqual(groups[0].measurement, 100.0)

    def test_dim_03_linestring_m_ignores_m_in_output_model(self):
        geometry = QgsGeometry.fromWkt("LINESTRING M (0 0 5, 3 4 6)")

        groups = extract_coordinate_groups(geometry)

        self.assertEqual(
            [(point.x_value, point.y_value) for point in groups[0].points],
            [(0.0, 0.0), (3.0, 4.0)],
        )


class CurvedGeometryRegressionTests(QgisTestCase):
    def test_cur_01_circularstring_should_be_rejected_for_version_1_0_0(self):
        geometry = QgsGeometry.fromWkt("CIRCULARSTRING (0 0, 1 1, 2 0)")
        self.assertFalse(geometry.isNull())

        with self.assertRaisesRegex(ValueError, "curv"):
            extract_coordinate_groups(geometry)

    def test_cur_02_curvepolygon_should_be_rejected_for_version_1_0_0(self):
        geometry = QgsGeometry.fromWkt(
            "CURVEPOLYGON (CIRCULARSTRING (0 0, 2 2, 4 0, 2 -2, 0 0))"
        )
        self.assertFalse(geometry.isNull())

        with self.assertRaisesRegex(ValueError, "curv"):
            extract_coordinate_groups(geometry)


if __name__ == "__main__":
    unittest.main()
