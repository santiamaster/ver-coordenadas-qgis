# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Funciones para extraer vértices y medidas de geometrías lineales y poligonales."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isclose
from typing import Any, Callable

from qgis.core import Qgis, QgsGeometry, QgsPointXY


class GroupKind(str, Enum):
    """Tipo de parte geométrica representada por un grupo de coordenadas."""

    POLYGON = "polygon"
    HOLE = "hole"
    LINE = "line"


@dataclass(frozen=True)
class CoordinatePoint:
    """Coordenada XY independiente del objeto de punto utilizado por QGIS."""

    x_value: float
    y_value: float

    def x(self) -> float:
        """Devuelve la coordenada X almacenada."""
        return self.x_value

    def y(self) -> float:
        """Devuelve la coordenada Y almacenada."""
        return self.y_value


@dataclass(frozen=True)
class CoordinateGroup:
    """Agrupa vértices y la medida de una parte geométrica para su presentación."""

    title: str
    points: tuple[CoordinatePoint, ...]
    kind: GroupKind
    measurement: float


def _to_coordinate_point(qgis_point: Any) -> CoordinatePoint:
    """Convierte un punto de QGIS en una estructura simple y reutilizable."""
    return CoordinatePoint(
        x_value=float(qgis_point.x()),
        y_value=float(qgis_point.y()),
    )


def _to_qgs_point_xy(qgis_point: Any) -> QgsPointXY:
    """Convierte cualquier punto compatible de QGIS en QgsPointXY."""
    return QgsPointXY(float(qgis_point.x()), float(qgis_point.y()))


def _same_xy(first_point: CoordinatePoint, second_point: CoordinatePoint) -> bool:
    """Indica si dos puntos representan la misma posición XY."""
    absolute_tolerance = 1e-9
    return isclose(
        first_point.x_value,
        second_point.x_value,
        rel_tol=0.0,
        abs_tol=absolute_tolerance,
    ) and isclose(
        first_point.y_value,
        second_point.y_value,
        rel_tol=0.0,
        abs_tol=absolute_tolerance,
    )


def _polygon_ring_without_closing_duplicate(qgis_ring: Any) -> tuple[CoordinatePoint, ...]:
    """Convierte un anillo y quita únicamente el vértice final repetido de cierre."""
    points = tuple(_to_coordinate_point(qgis_point) for qgis_point in qgis_ring)

    if len(points) >= 2 and _same_xy(points[0], points[-1]):
        return points[:-1]

    return points


def _polygon_ring_geometry(qgis_ring: Any) -> QgsGeometry:
    """Construye una geometría poligonal formada por un único anillo."""
    ring_points = [_to_qgs_point_xy(qgis_point) for qgis_point in qgis_ring]
    return QgsGeometry.fromPolygonXY([ring_points])


def _polygon_geometry(qgis_polygon_rings: Any) -> QgsGeometry:
    """Construye un polígono completo con anillo exterior y huecos interiores."""
    polygon_rings = [
        [_to_qgs_point_xy(qgis_point) for qgis_point in qgis_ring]
        for qgis_ring in qgis_polygon_rings
    ]
    return QgsGeometry.fromPolygonXY(polygon_rings)


def _line_geometry(qgis_line: Any) -> QgsGeometry:
    """Construye una geometría lineal a partir de una secuencia de puntos."""
    line_points = [_to_qgs_point_xy(qgis_point) for qgis_point in qgis_line]
    return QgsGeometry.fromPolylineXY(line_points)


def _default_measurement(group_kind: GroupKind, geometry: QgsGeometry) -> float:
    """Calcula la medida planimétrica usada por defecto en CRS proyectados."""
    if group_kind in (GroupKind.POLYGON, GroupKind.HOLE):
        return float(geometry.area())
    return float(geometry.length())


MeasurementFunction = Callable[[GroupKind, QgsGeometry], float]


def _extract_polygon_groups(
    geometry: Any,
    measurement_function: MeasurementFunction,
) -> list[CoordinateGroup]:
    """
    Extrae Polygon/MultiPolygon, incluyendo huecos y sus áreas individuales.

    El área de cada polígono es su área neta: anillo exterior menos todos sus
    huecos. Cada hueco también se informa por separado, pero no se vuelve a
    sumar ni restar cuando se calcula el área total del multipolígono.
    """
    if geometry.isMultipart():
        polygons = geometry.asMultiPolygon()
    else:
        polygons = [geometry.asPolygon()]

    groups: list[CoordinateGroup] = []

    for polygon_number, polygon_rings in enumerate(polygons, start=1):
        if not polygon_rings:
            continue

        exterior_qgis_ring = polygon_rings[0]
        exterior_points = _polygon_ring_without_closing_duplicate(exterior_qgis_ring)
        if exterior_points:
            groups.append(
                CoordinateGroup(
                    title=f"Polígono {polygon_number}",
                    points=exterior_points,
                    kind=GroupKind.POLYGON,
                    measurement=measurement_function(
                        GroupKind.POLYGON,
                        _polygon_geometry(polygon_rings),
                    ),
                )
            )

        for hole_number, interior_qgis_ring in enumerate(polygon_rings[1:], start=1):
            hole_points = _polygon_ring_without_closing_duplicate(interior_qgis_ring)
            if hole_points:
                groups.append(
                    CoordinateGroup(
                        title=f"Polígono {polygon_number} - Hueco {hole_number}",
                        points=hole_points,
                        kind=GroupKind.HOLE,
                        measurement=measurement_function(
                            GroupKind.HOLE,
                            _polygon_ring_geometry(interior_qgis_ring),
                        ),
                    )
                )

    return groups


def _extract_line_groups(
    geometry: Any,
    measurement_function: MeasurementFunction,
) -> list[CoordinateGroup]:
    """Extrae LineString/MultiLineString y calcula la longitud de cada parte."""
    if geometry.isMultipart():
        lines = geometry.asMultiPolyline()
    else:
        lines = [geometry.asPolyline()]

    groups: list[CoordinateGroup] = []

    for line_number, qgis_line in enumerate(lines, start=1):
        line_points = tuple(_to_coordinate_point(qgis_point) for qgis_point in qgis_line)
        if line_points:
            groups.append(
                CoordinateGroup(
                    title=f"Línea {line_number}",
                    points=line_points,
                    kind=GroupKind.LINE,
                    measurement=measurement_function(
                        GroupKind.LINE,
                        _line_geometry(qgis_line),
                    ),
                )
            )

    return groups


def extract_coordinate_groups(
    geometry: Any,
    measurement_function: MeasurementFunction = _default_measurement,
) -> list[CoordinateGroup]:
    """
    Extrae vértices y medidas de una geometría soportada.

    Soporta Polygon, MultiPolygon, LineString y MultiLineString. Los polígonos
    eliminan únicamente el punto final duplicado que cierra cada anillo. Los
    huecos se informan de forma independiente, con su propia área. Las líneas
    conservan todos sus extremos.

    Raises:
        ValueError: si la geometría es nula, vacía, no soportada o no produce
        vértices utilizables.
    """
    if geometry is None or geometry.isNull() or geometry.isEmpty():
        raise ValueError("La entidad no tiene una geometría utilizable.")

    geometry_type = geometry.type()

    if geometry_type == Qgis.GeometryType.Polygon:
        groups = _extract_polygon_groups(geometry, measurement_function)
    elif geometry_type == Qgis.GeometryType.Line:
        groups = _extract_line_groups(geometry, measurement_function)
    else:
        raise ValueError("El plugin admite únicamente geometrías de polígonos y líneas.")

    if not groups:
        raise ValueError("No se pudieron obtener vértices de la geometría.")

    return groups
