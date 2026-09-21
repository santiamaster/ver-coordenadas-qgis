import sys
import types
import unittest

# Stubs mínimos para poder importar las estructuras de geometry.py fuera de QGIS.
qgis_module = types.ModuleType("qgis")
qgis_core_module = types.ModuleType("qgis.core")
qgis_core_module.Qgis = type("Qgis", (), {})
qgis_core_module.QgsGeometry = type("QgsGeometry", (), {})
qgis_core_module.QgsPointXY = type("QgsPointXY", (), {})
sys.modules.setdefault("qgis", qgis_module)
sys.modules.setdefault("qgis.core", qgis_core_module)

from ver_coordenadas.formatter import (
    OutputMode,
    format_area_square_meters,
    format_coordinate_value,
    format_groups,
    format_length_meters,
)
from ver_coordenadas.geometry import CoordinateGroup, CoordinatePoint, GroupKind


class ProjectedFormattingTests(unittest.TestCase):
    def test_fmt_01_positive_projected_coordinate_uses_spanish_separators(self):
        self.assertEqual(format_coordinate_value(3456789.14), "3.456.789,14")

    def test_fmt_02_negative_projected_coordinate_keeps_sign(self):
        self.assertEqual(format_coordinate_value(-3456789.14), "-3.456.789,14")

    def test_fmt_03_gauss_kruger_displays_north_then_east(self):
        group = CoordinateGroup(
            title="Línea 1",
            points=(CoordinatePoint(3456789.0, 7324567.0),),
            kind=GroupKind.LINE,
            measurement=0.0,
        )
        result = format_groups([group], OutputMode.GAUSS_KRUGER)
        self.assertIn("X: 7.324.567,00    Y: 3.456.789,00", result)

    def test_fmt_04_traditional_displays_east_then_north(self):
        group = CoordinateGroup(
            title="Línea 1",
            points=(CoordinatePoint(3456789.0, 7324567.0),),
            kind=GroupKind.LINE,
            measurement=0.0,
        )
        result = format_groups([group], OutputMode.GIS_NORMAL)
        self.assertIn("X: 3.456.789,00    Y: 7.324.567,00", result)

    def test_fmt_05_area_under_one_hectare(self):
        self.assertEqual(format_area_square_meters(735), "735 m²")

    def test_fmt_06_area_at_least_one_hectare(self):
        self.assertEqual(format_area_square_meters(100735), "10 ha 0735 m²")

    def test_fmt_07_length_under_one_kilometer(self):
        self.assertEqual(format_length_meters(347), "347 m")

    def test_fmt_08_length_at_least_one_kilometer(self):
        self.assertEqual(format_length_meters(5005), "5 km 005 m")


class GeographicFormattingTests(unittest.TestCase):
    @staticmethod
    def _line_group(longitude, latitude):
        return CoordinateGroup(
            title="Línea 1",
            points=(CoordinatePoint(longitude, latitude),),
            kind=GroupKind.LINE,
            measurement=0.0,
        )

    def test_geo_01_dms_positive_coordinates_use_north_east(self):
        result = format_groups(
            [self._line_group(2.17402777, 41.40338888)],
            OutputMode.GEOGRAPHIC_DMS,
        )
        self.assertIn('41°24\'12.20"N 2°10\'26.50"E', result)

    def test_geo_02_dms_negative_coordinates_use_south_west_without_minus(self):
        result = format_groups(
            [self._line_group(-65.41000000, -24.79000000)],
            OutputMode.GEOGRAPHIC_DMS,
        )
        coordinate_line = result.splitlines()[1]
        self.assertIn("S", coordinate_line)
        self.assertIn("W", coordinate_line)
        self.assertNotIn("-", coordinate_line)

    def test_geo_03_dms_seconds_carry_to_minutes(self):
        latitude = 10 + 5 / 60 + 59.999 / 3600
        result = format_groups(
            [self._line_group(0.0, latitude)],
            OutputMode.GEOGRAPHIC_DMS,
        )
        self.assertIn('10°06\'00.00"N', result)

    def test_geo_04_dms_minutes_carry_to_degrees(self):
        latitude = 10 + 59 / 60 + 59.999 / 3600
        result = format_groups(
            [self._line_group(0.0, latitude)],
            OutputMode.GEOGRAPHIC_DMS,
        )
        self.assertIn('11°00\'00.00"N', result)

    def test_geo_05_dmm_formats_six_decimals_and_hemispheres(self):
        result = format_groups(
            [self._line_group(-2.17402777, -41.40338888)],
            OutputMode.GEOGRAPHIC_DMM,
        )
        self.assertIn("41° 24.203333'S", result)
        self.assertIn("2° 10.441666'W", result)

    def test_geo_06_dmm_minutes_carry_to_degrees(self):
        latitude = 10 + 59.9999999 / 60
        result = format_groups(
            [self._line_group(0.0, latitude)],
            OutputMode.GEOGRAPHIC_DMM,
        )
        self.assertIn("11° 00.000000'N", result)

    def test_geo_07_decimal_degrees_use_absolute_values_and_hemispheres(self):
        result = format_groups(
            [self._line_group(-2.17402777, -41.40338888)],
            OutputMode.GEOGRAPHIC_DD,
        )
        self.assertIn("41.40338888°S 2.17402777°W", result)
        self.assertNotIn("-", result.splitlines()[1])

    def test_geo_08_zero_coordinates_use_north_east(self):
        result = format_groups(
            [self._line_group(0.0, 0.0)],
            OutputMode.GEOGRAPHIC_DD,
        )
        self.assertIn("0.00000000°N 0.00000000°E", result)

    def test_num_03_geographic_limits_format_correctly(self):
        result = format_groups(
            [self._line_group(180.0, 90.0)],
            OutputMode.GEOGRAPHIC_DMS,
        )
        self.assertIn('90°00\'00.00"N 180°00\'00.00"E', result)


class GroupOutputTests(unittest.TestCase):
    def test_pol_08_vertex_numbering_is_continuous_across_polygon_and_hole(self):
        groups = [
            CoordinateGroup(
                "Polígono 1",
                (CoordinatePoint(1, 2), CoordinatePoint(3, 4)),
                GroupKind.POLYGON,
                100.0,
            ),
            CoordinateGroup(
                "Polígono 1 - Hueco 1",
                (CoordinatePoint(5, 6), CoordinatePoint(7, 8)),
                GroupKind.HOLE,
                10.0,
            ),
        ]
        result = format_groups(groups, OutputMode.GIS_NORMAL)
        lines = result.splitlines()
        numbered = [
            line.strip().split()[0]
            for line in lines
            if line and line[0].isdigit()
        ]
        self.assertEqual(numbered, ["1", "2", "3", "4"])

    def test_lin_04_vertex_numbering_is_continuous_across_lines(self):
        groups = [
            CoordinateGroup(
                "Línea 1",
                (CoordinatePoint(1, 2),),
                GroupKind.LINE,
                100.0,
            ),
            CoordinateGroup(
                "Línea 2",
                (CoordinatePoint(3, 4),),
                GroupKind.LINE,
                200.0,
            ),
        ]
        result = format_groups(groups, OutputMode.GIS_NORMAL)
        self.assertIn("1    X:", result)
        self.assertIn("2    X:", result)
        self.assertIn("Longitud total: 300 m", result)

    def test_multipart_polygon_total_excludes_hole_measurements(self):
        groups = [
            CoordinateGroup(
                "Polígono 1",
                (CoordinatePoint(0, 0),),
                GroupKind.POLYGON,
                80.0,
            ),
            CoordinateGroup(
                "Polígono 1 - Hueco 1",
                (CoordinatePoint(1, 1),),
                GroupKind.HOLE,
                20.0,
            ),
            CoordinateGroup(
                "Polígono 2",
                (CoordinatePoint(2, 2),),
                GroupKind.POLYGON,
                50.0,
            ),
        ]
        result = format_groups(groups, OutputMode.GIS_NORMAL)
        self.assertIn("Área total: 130 m²", result)
        self.assertNotIn("Área total: 150 m²", result)


if __name__ == "__main__":
    unittest.main()
