import unittest

from qgis.core import QgsApplication, QgsVectorLayer
from qgis.gui import QgsGui

from ver_coordenadas.plugin import SupportedGeometryAction, VerCoordenadasPlugin


class FakeIface:
    """Interfaz mínima requerida por VerCoordenadasPlugin para registrar acciones."""

    def mainWindow(self):
        return None


class QgisGuiTestCase(unittest.TestCase):
    """Inicializa QGIS con GUI cuando las pruebas corren fuera de QGIS Desktop."""

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
    def _layer(geometry_type):
        return QgsVectorLayer(
            f"{geometry_type}?crs=EPSG:4326",
            f"test_{geometry_type.lower()}",
            "memory",
        )


class SupportedGeometryActionTests(QgisGuiTestCase):
    def setUp(self):
        super().setUp()
        self.action = SupportedGeometryAction(None)
        self.addCleanup(self.action.deleteLater)

    def test_act_01_action_is_available_for_polygon_layer(self):
        layer = self._layer("Polygon")
        self.assertTrue(layer.isValid())
        self.assertTrue(self.action.canRunUsingLayer(layer))

    def test_act_02_action_is_available_for_line_layer(self):
        layer = self._layer("LineString")
        self.assertTrue(layer.isValid())
        self.assertTrue(self.action.canRunUsingLayer(layer))

    def test_act_03_action_is_not_available_for_point_layer(self):
        layer = self._layer("Point")
        self.assertTrue(layer.isValid())
        self.assertFalse(self.action.canRunUsingLayer(layer))

    def test_action_is_not_available_without_layer(self):
        self.assertFalse(self.action.canRunUsingLayer(None))


class PluginLifecycleTests(QgisGuiTestCase):
    def setUp(self):
        super().setUp()
        self.plugin = VerCoordenadasPlugin(FakeIface())
        self.addCleanup(self.plugin.unload)

    @staticmethod
    def _registered_ver_coordenadas_actions(layer):
        return [
            action
            for action in QgsGui.mapLayerActionRegistry().mapLayerActions(layer)
            if action.text() == "Ver coordenadas"
        ]

    def test_act_05_init_and_unload_register_and_remove_action(self):
        layer = self._layer("LineString")
        before = self._registered_ver_coordenadas_actions(layer)

        self.plugin.initGui()
        during = self._registered_ver_coordenadas_actions(layer)

        self.assertEqual(len(during), len(before) + 1)
        self.assertIsNotNone(self.plugin._map_layer_action)
        self.assertIn(self.plugin._map_layer_action, during)

        action = self.plugin._map_layer_action
        self.plugin.unload()
        after = self._registered_ver_coordenadas_actions(layer)

        self.assertEqual(len(after), len(before))
        self.assertNotIn(action, after)
        self.assertIsNone(self.plugin._map_layer_action)

    def test_act_06_repeated_enable_disable_cycles_do_not_leave_duplicates(self):
        layer = self._layer("Polygon")
        baseline = len(self._registered_ver_coordenadas_actions(layer))

        for _ in range(3):
            self.plugin.initGui()
            self.assertEqual(
                len(self._registered_ver_coordenadas_actions(layer)),
                baseline + 1,
            )
            self.plugin.unload()
            self.assertEqual(
                len(self._registered_ver_coordenadas_actions(layer)),
                baseline,
            )

        self.assertIsNone(self.plugin._map_layer_action)


if __name__ == "__main__":
    unittest.main()
