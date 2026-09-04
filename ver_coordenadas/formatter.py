# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Formateo de coordenadas, áreas y longitudes como texto plano."""

from __future__ import annotations

from enum import Enum

from .geometry import CoordinateGroup, CoordinatePoint, GroupKind


class OutputMode(str, Enum):
    """Modos disponibles para presentar las coordenadas."""

    GAUSS_KRUGER = "gauss_kruger"
    GIS_NORMAL = "gis_normal"
    GEOGRAPHIC_DMS = "geographic_dms"
    GEOGRAPHIC_DMM = "geographic_dmm"
    GEOGRAPHIC_DD = "geographic_dd"


GEOGRAPHIC_OUTPUT_MODES = {
    OutputMode.GEOGRAPHIC_DMS,
    OutputMode.GEOGRAPHIC_DMM,
    OutputMode.GEOGRAPHIC_DD,
}


def format_coordinate_value(coordinate_value: float) -> str:
    """Formatea una coordenada proyectada con miles '.', decimal ',' y dos decimales."""
    standard_format = f"{coordinate_value:,.2f}"
    return standard_format.replace(",", "_").replace(".", ",").replace("_", ".")


def format_area_square_meters(area_square_meters: float) -> str:
    """Redondea el área y la expresa en hectáreas y metros cuadrados."""
    rounded_square_meters = round(area_square_meters)

    if rounded_square_meters < 10_000:
        return f"{rounded_square_meters} m²"

    hectares, remaining_square_meters = divmod(rounded_square_meters, 10_000)
    return f"{hectares} ha {remaining_square_meters:04d} m²"


def format_length_meters(length_meters: float) -> str:
    """Redondea la longitud y la expresa en kilómetros y metros."""
    rounded_meters = round(length_meters)

    if rounded_meters < 1_000:
        return f"{rounded_meters} m"

    kilometers, remaining_meters = divmod(rounded_meters, 1_000)
    return f"{kilometers} km {remaining_meters:03d} m"


def _display_xy(point: CoordinatePoint, mode: OutputMode) -> tuple[float, float]:
    """Devuelve X/Y en el orden de presentación elegido para CRS proyectados."""
    if mode == OutputMode.GIS_NORMAL:
        return point.x_value, point.y_value

    # Convención usada por defecto en la Secretaría para Gauss-Krüger:
    # X presentada = Y de QGIS (norte); Y presentada = X de QGIS (este).
    return point.y_value, point.x_value


def _hemisphere(value: float, positive: str, negative: str) -> str:
    """Devuelve la letra de hemisferio según el signo de una coordenada angular."""
    return positive if value >= 0 else negative


def _decimal_degrees_to_dms(value: float) -> tuple[int, int, float]:
    """Convierte grados decimales a grados, minutos y segundos con acarreo seguro."""
    absolute_value = abs(value)
    degrees = int(absolute_value)
    minutes_decimal = (absolute_value - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = round((minutes_decimal - minutes) * 60, 2)

    if seconds >= 60:
        seconds = 0.0
        minutes += 1
    if minutes >= 60:
        minutes = 0
        degrees += 1

    return degrees, minutes, seconds


def _decimal_degrees_to_dmm(value: float) -> tuple[int, float]:
    """Convierte grados decimales a grados y minutos decimales con acarreo seguro."""
    absolute_value = abs(value)
    degrees = int(absolute_value)
    decimal_minutes = round((absolute_value - degrees) * 60, 6)

    if decimal_minutes >= 60:
        decimal_minutes = 0.0
        degrees += 1

    return degrees, decimal_minutes


def _format_geographic_point(point: CoordinatePoint, mode: OutputMode) -> str:
    """Formatea latitud/longitud en DMS, DMM o grados decimales.

    QGIS almacena X como longitud y Y como latitud. Para lectura humana se
    presenta primero la latitud y luego la longitud.
    """
    longitude = point.x_value
    latitude = point.y_value
    latitude_hemisphere = _hemisphere(latitude, "N", "S")
    longitude_hemisphere = _hemisphere(longitude, "E", "W")

    if mode == OutputMode.GEOGRAPHIC_DMS:
        lat_deg, lat_min, lat_sec = _decimal_degrees_to_dms(latitude)
        lon_deg, lon_min, lon_sec = _decimal_degrees_to_dms(longitude)
        return (
            f'{lat_deg}°{lat_min:02d}\'{lat_sec:05.2f}"{latitude_hemisphere} '
            f'{lon_deg}°{lon_min:02d}\'{lon_sec:05.2f}"{longitude_hemisphere}'
        )

    if mode == OutputMode.GEOGRAPHIC_DMM:
        lat_deg, lat_minutes = _decimal_degrees_to_dmm(latitude)
        lon_deg, lon_minutes = _decimal_degrees_to_dmm(longitude)
        return (
            f"{lat_deg}° {lat_minutes:09.6f}'{latitude_hemisphere} "
            f"{lon_deg}° {lon_minutes:09.6f}'{longitude_hemisphere}"
        )

    if mode == OutputMode.GEOGRAPHIC_DD:
        return (
            f"{abs(latitude):.8f}°{latitude_hemisphere} "
            f"{abs(longitude):.8f}°{longitude_hemisphere}"
        )

    raise ValueError("El formato geográfico seleccionado no es válido.")


def _measurement_line(coordinate_group: CoordinateGroup) -> str:
    """Genera el texto de área o longitud correspondiente al tipo de grupo."""
    if coordinate_group.kind == GroupKind.POLYGON:
        return f"Área: {format_area_square_meters(coordinate_group.measurement)}"

    if coordinate_group.kind == GroupKind.HOLE:
        return f"Área del hueco: {format_area_square_meters(coordinate_group.measurement)}"

    return f"Longitud: {format_length_meters(coordinate_group.measurement)}"


def _total_measurement_line(coordinate_groups: list[CoordinateGroup]) -> str | None:
    """Calcula el total de multipartes sin volver a sumar las áreas de los huecos."""
    polygon_groups = [group for group in coordinate_groups if group.kind == GroupKind.POLYGON]
    line_groups = [group for group in coordinate_groups if group.kind == GroupKind.LINE]

    if len(polygon_groups) > 1:
        total_area = sum(group.measurement for group in polygon_groups)
        return f"Área total: {format_area_square_meters(total_area)}"

    if len(line_groups) > 1:
        total_length = sum(group.measurement for group in line_groups)
        return f"Longitud total: {format_length_meters(total_length)}"

    return None


def format_groups(
    coordinate_groups: list[CoordinateGroup],
    mode: OutputMode = OutputMode.GAUSS_KRUGER,
) -> str:
    """Genera texto plano con vértices, medida por parte y total de multipartes."""
    output_lines: list[str] = []
    vertex_number = 1
    geographic_mode = mode in GEOGRAPHIC_OUTPUT_MODES

    for group_index, coordinate_group in enumerate(coordinate_groups):
        if group_index > 0:
            output_lines.append("")

        output_lines.append(coordinate_group.title)

        for coordinate_point in coordinate_group.points:
            if geographic_mode:
                coordinate_text = _format_geographic_point(coordinate_point, mode)
                output_lines.append(f"{vertex_number}    {coordinate_text}")
            else:
                display_x, display_y = _display_xy(coordinate_point, mode)
                output_lines.append(
                    f"{vertex_number}    "
                    f"X: {format_coordinate_value(display_x)}    "
                    f"Y: {format_coordinate_value(display_y)}"
                )
            vertex_number += 1

        output_lines.append(_measurement_line(coordinate_group))

    total_line = _total_measurement_line(coordinate_groups)
    if total_line is not None:
        output_lines.extend(["", total_line])

    return "\n".join(output_lines)
