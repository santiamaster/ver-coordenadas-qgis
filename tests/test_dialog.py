import unittest

from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QApplication

from ver_coordenadas.dialog import CoordinatesDialog
from ver_coordenadas.formatter import OutputMode
from ver_coordenadas.geometry import CoordinateGroup, CoordinatePoint, GroupKind
from ver_coordenadas.warning import (
    GEOGRAPHIC_AREA_WARNING,
    GEOGRAPHIC_LENGTH_WARNING,
)


class FakeSettings:
    """Almacén mínimo compatible con QSettings para aislar preferencias por prueba."""

    def __init__(self, initial_values=None):
        self._values = dict(initial_values or {})

    def value(self, key, default_value=None, type=None):
        value = self._values.get(key, default_value)
        if type is not None:
            return type(value)
        return value

    def setValue(self, key, value):
        self._values[key] = value


class QgisGuiTestCase(unittest.TestCase):
    """Inicializa una aplicación QGIS con GUI cuando no existe una instancia activa."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._owns_qgis_app = QgsApplication.instance() is None
        cls._qgis_app = None

        if cls._owns_qgis_app:
            cls._qgis_app = QgsApplication([], True)
            cls._qgis_app.initQgis()

    @classmethod
    def tearDownClass(cls):
        if cls._owns_qgis_app and cls._qgis_app is not None:
            cls._qgis_app.exitQgis()
        super().tearDownClass()

    @staticmethod
    def _polygon_group():
        return CoordinateGroup(
            title="Polígono 1",
            points=(
                CoordinatePoint(-65.40, -24.78),
                CoordinatePoint(-65.39, -24.78),
                CoordinatePoint(-65.39, -24.79),
            ),
            kind=GroupKind.POLYGON,
            measurement=100.0,
        )

    @staticmethod
    def _line_group():
        return CoordinateGroup(
            title="Línea 1",
            points=(
                CoordinatePoint(-65.40, -24.78),
                CoordinatePoint(-65.39, -24.79),
            ),
            kind=GroupKind.LINE,
            measurement=150.0,
        )

    def _make_dialog(self, groups, geographic, settings=None):
        settings = settings or FakeSettings()
        dialog = CoordinatesDialog(
            coordinate_groups=groups,
            geographic_coordinates=geographic,
            settings_factory=lambda: settings,
        )
        self.addCleanup(dialog.deleteLater)
        return dialog, settings


class CoordinateSelectorTests(QgisGuiTestCase):
    def test_ui_01_projected_selector_contains_only_two_projected_modes(self):
        dialog, _ = self._make_dialog([self._line_group()], False)

        self.assertEqual(dialog._format_selector.count(), 2)
        self.assertEqual(
            [
                dialog._format_selector.itemData(index)
                for index in range(dialog._format_selector.count())
            ],
            [
                OutputMode.GAUSS_KRUGER.value,
                OutputMode.GIS_NORMAL.value,
            ],
        )

    def test_ui_02_geographic_selector_contains_only_dms_dmm_dd(self):
        dialog, _ = self._make_dialog([self._line_group()], True)

        self.assertEqual(dialog._format_selector.count(), 3)
        self.assertEqual(
            [
                dialog._format_selector.itemData(index)
                for index in range(dialog._format_selector.count())
            ],
            [
                OutputMode.GEOGRAPHIC_DMS.value,
                OutputMode.GEOGRAPHIC_DMM.value,
                OutputMode.GEOGRAPHIC_DD.value,
            ],
        )

    def test_ui_03_projected_preference_is_restored(self):
        settings = FakeSettings()
        first_dialog, _ = self._make_dialog(
            [self._line_group()],
            False,
            settings,
        )
        traditional_index = first_dialog._format_selector.findData(
            OutputMode.GIS_NORMAL.value
        )
        first_dialog._format_selector.setCurrentIndex(traditional_index)

        second_dialog, _ = self._make_dialog(
            [self._line_group()],
            False,
            settings,
        )

        self.assertEqual(
            second_dialog._format_selector.currentData(),
            OutputMode.GIS_NORMAL.value,
        )

    def test_ui_04_geographic_preference_is_independent_from_projected(self):
        settings = FakeSettings()

        projected_dialog, _ = self._make_dialog(
            [self._line_group()],
            False,
            settings,
        )
        projected_dialog._format_selector.setCurrentIndex(
            projected_dialog._format_selector.findData(OutputMode.GIS_NORMAL.value)
        )

        geographic_dialog, _ = self._make_dialog(
            [self._line_group()],
            True,
            settings,
        )
        geographic_dialog._format_selector.setCurrentIndex(
            geographic_dialog._format_selector.findData(OutputMode.GEOGRAPHIC_DD.value)
        )

        reopened_projected, _ = self._make_dialog(
            [self._line_group()],
            False,
            settings,
        )
        reopened_geographic, _ = self._make_dialog(
            [self._line_group()],
            True,
            settings,
        )

        self.assertEqual(
            reopened_projected._format_selector.currentData(),
            OutputMode.GIS_NORMAL.value,
        )
        self.assertEqual(
            reopened_geographic._format_selector.currentData(),
            OutputMode.GEOGRAPHIC_DD.value,
        )

    def test_ui_05_invalid_saved_preference_falls_back_to_default(self):
        settings = FakeSettings(
            {"VerCoordenadas/output_mode": "obsolete_mode"}
        )

        dialog, _ = self._make_dialog(
            [self._line_group()],
            False,
            settings,
        )

        self.assertEqual(
            dialog._format_selector.currentData(),
            OutputMode.GAUSS_KRUGER.value,
        )


class ClipboardTests(QgisGuiTestCase):
    def test_ui_06_opening_dialog_copies_current_output_to_clipboard(self):
        dialog, _ = self._make_dialog([self._line_group()], False)

        self.assertEqual(
            QApplication.clipboard().text(),
            dialog._coordinates_text.toPlainText(),
        )

    def test_ui_07_changing_format_updates_clipboard(self):
        dialog, _ = self._make_dialog([self._line_group()], False)
        initial_text = QApplication.clipboard().text()

        traditional_index = dialog._format_selector.findData(
            OutputMode.GIS_NORMAL.value
        )
        dialog._format_selector.setCurrentIndex(traditional_index)

        updated_text = QApplication.clipboard().text()
        self.assertEqual(updated_text, dialog._coordinates_text.toPlainText())
        self.assertNotEqual(updated_text, initial_text)


class DialogWarningTests(QgisGuiTestCase):
    def test_ui_09_projected_dialog_has_no_warning_text(self):
        dialog, _ = self._make_dialog([self._polygon_group()], False)

        self.assertEqual(dialog._measurement_warning.text(), "")
        self.assertTrue(dialog._measurement_warning.isHidden())

    def test_ui_10_geographic_polygon_has_surface_warning(self):
        dialog, _ = self._make_dialog([self._polygon_group()], True)

        self.assertEqual(
            dialog._measurement_warning.text(),
            GEOGRAPHIC_AREA_WARNING,
        )
        self.assertFalse(dialog._measurement_warning.isHidden())

    def test_ui_11_geographic_line_has_length_warning(self):
        dialog, _ = self._make_dialog([self._line_group()], True)

        self.assertEqual(
            dialog._measurement_warning.text(),
            GEOGRAPHIC_LENGTH_WARNING,
        )
        self.assertFalse(dialog._measurement_warning.isHidden())

    def test_ui_12_multipart_dialog_uses_one_warning_label(self):
        groups = [
            self._polygon_group(),
            CoordinateGroup(
                title="Polígono 2",
                points=(
                    CoordinatePoint(-65.38, -24.77),
                    CoordinatePoint(-65.37, -24.77),
                    CoordinatePoint(-65.37, -24.78),
                ),
                kind=GroupKind.POLYGON,
                measurement=200.0,
            ),
        ]

        dialog, _ = self._make_dialog(groups, True)

        self.assertEqual(
            dialog._measurement_warning.text(),
            GEOGRAPHIC_AREA_WARNING,
        )
        self.assertEqual(
            dialog.findChildren(type(dialog._measurement_warning)).count(
                dialog._measurement_warning
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
