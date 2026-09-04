# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Cálculo de áreas y longitudes según el tipo de CRS de la capa."""

from __future__ import annotations

from qgis.core import Qgis, QgsDistanceArea, QgsUnitTypes


class GeometryMeasurementCalculator:
    """Calcula medidas métricas preservando el criterio cartográfico de QGIS.

    Para CRS proyectados se mantienen las medidas planimétricas de la geometría,
    equivalentes a ``area(@geometry)`` y ``length(@geometry)`` cuando las unidades
    del CRS son métricas.

    Para CRS geográficos se utiliza ``QgsDistanceArea`` con el elipsoide del
    proyecto. Si el proyecto está configurado como planimétrico, se intenta usar
    el elipsoide definido por el CRS de origen para evitar devolver grados o
    grados cuadrados etiquetados incorrectamente como metros.
    """

    def __init__(self, source_crs, project) -> None:
        self._source_crs = source_crs
        self._project = project
        self._is_geographic = bool(source_crs.isGeographic())
        self._distance_area = None

        if self._is_geographic:
            self._distance_area = QgsDistanceArea()
            self._distance_area.setSourceCrs(
                source_crs,
                project.transformContext(),
            )
            self._configure_ellipsoid()

    @property
    def is_geographic(self) -> bool:
        """Indica si las coordenadas de origen pertenecen a un CRS geográfico."""
        return self._is_geographic

    def _configure_ellipsoid(self) -> None:
        """Configura un elipsoide válido para las mediciones geográficas."""
        project_ellipsoid = str(self._project.ellipsoid() or "").strip()
        ellipsoid_candidates = []

        if project_ellipsoid and project_ellipsoid.upper() != "NONE":
            ellipsoid_candidates.append(project_ellipsoid)

        source_ellipsoid = str(self._source_crs.ellipsoidAcronym() or "").strip()
        if source_ellipsoid and source_ellipsoid not in ellipsoid_candidates:
            ellipsoid_candidates.append(source_ellipsoid)

        for ellipsoid in ellipsoid_candidates:
            if self._distance_area.setEllipsoid(ellipsoid):
                break

        if not self._distance_area.willUseEllipsoid():
            raise ValueError(
                "No se pudo configurar un elipsoide válido para calcular "
                "áreas y longitudes de la capa geográfica."
            )

    def measure_area(self, geometry) -> float:
        """Devuelve el área en metros cuadrados."""
        if not self._is_geographic:
            measured_area = float(geometry.area())
            source_area_unit = QgsUnitTypes.distanceToAreaUnit(self._source_crs.mapUnits())
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                source_area_unit,
                Qgis.AreaUnit.SquareMeters,
            )
            return measured_area * conversion_factor

        measured_area = float(self._distance_area.measureArea(geometry))
        conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
            self._distance_area.areaUnits(),
            Qgis.AreaUnit.SquareMeters,
        )
        return measured_area * conversion_factor

    def measure_length(self, geometry) -> float:
        """Devuelve la longitud en metros."""
        if not self._is_geographic:
            measured_length = float(geometry.length())
            conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
                self._source_crs.mapUnits(),
                Qgis.DistanceUnit.Meters,
            )
            return measured_length * conversion_factor

        measured_length = float(self._distance_area.measureLength(geometry))
        conversion_factor = QgsUnitTypes.fromUnitToUnitFactor(
            self._distance_area.lengthUnits(),
            Qgis.DistanceUnit.Meters,
        )
        return measured_length * conversion_factor
