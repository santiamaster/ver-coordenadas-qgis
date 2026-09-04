# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Integración principal del plugin con la interfaz de QGIS."""

from __future__ import annotations

from qgis.core import Qgis, QgsFeature, QgsMapLayer, QgsProject
from qgis.gui import QgsGui, QgsMapLayerAction, QgsMapLayerActionContext
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox

from .dialog import CoordinatesDialog
from .geometry import GroupKind, extract_coordinate_groups
from .measurements import GeometryMeasurementCalculator


class SupportedGeometryAction(QgsMapLayerAction):
    """Acción de QGIS disponible únicamente para capas vectoriales de línea o polígono."""

    def __init__(self, parent) -> None:
        super().__init__(
            "Ver coordenadas",
            parent,
            Qgis.LayerType.Vector,
            Qgis.MapLayerActionTarget.SingleFeature,
            QIcon(),
            Qgis.MapLayerActionFlag.EnableOnlyWhenHasGeometry,
        )

    def canRunUsingLayer(
        self,
        layer: QgsMapLayer | None,
        context: QgsMapLayerActionContext | None = None,
    ) -> bool:
        """Limita la acción a capas de geometría lineal o poligonal."""
        del context
        if layer is None:
            return False

        geometry_type = layer.geometryType()
        return geometry_type in (
            Qgis.GeometryType.Line,
            Qgis.GeometryType.Polygon,
        )


class VerCoordenadasPlugin:
    """Registra la acción contextual y coordina extracción, medición y visualización."""

    def __init__(self, iface) -> None:
        self.iface = iface
        self._map_layer_action: SupportedGeometryAction | None = None

    def initGui(self) -> None:
        """Registra 'Ver coordenadas' en el sistema de acciones de capas de QGIS."""
        self._map_layer_action = SupportedGeometryAction(self.iface.mainWindow())
        self._map_layer_action.triggeredForFeatureV2.connect(self._show_feature_coordinates)
        QgsGui.mapLayerActionRegistry().addMapLayerAction(self._map_layer_action)

    def unload(self) -> None:
        """Elimina del registro la acción creada por el plugin al desactivarlo."""
        if self._map_layer_action is None:
            return

        QgsGui.mapLayerActionRegistry().removeMapLayerAction(self._map_layer_action)
        self._map_layer_action.deleteLater()
        self._map_layer_action = None

    def _show_feature_coordinates(
        self,
        layer: QgsMapLayer,
        feature: QgsFeature,
        context: QgsMapLayerActionContext,
    ) -> None:
        """Extrae coordenadas y medidas de la entidad elegida y abre la ventana."""
        del context

        try:
            measurement_calculator = GeometryMeasurementCalculator(
                source_crs=layer.crs(),
                project=QgsProject.instance(),
            )

            def measure_geometry(group_kind: GroupKind, geometry) -> float:
                """Aplica área o longitud según la parte geométrica recibida."""
                if group_kind in (GroupKind.POLYGON, GroupKind.HOLE):
                    return measurement_calculator.measure_area(geometry)
                return measurement_calculator.measure_length(geometry)

            coordinate_groups = extract_coordinate_groups(
                feature.geometry(),
                measurement_function=measure_geometry,
            )
        except (TypeError, ValueError) as error:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Ver coordenadas",
                str(error),
            )
            return
        except Exception as error:  # QGIS puede propagar errores de transformación del CRS.
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Ver coordenadas",
                f"No se pudieron calcular las coordenadas o medidas:\n{error}",
            )
            return

        coordinates_dialog = CoordinatesDialog(
            coordinate_groups=coordinate_groups,
            geographic_coordinates=measurement_calculator.is_geographic,
            parent=self.iface.mainWindow(),
        )
        coordinates_dialog.exec()
