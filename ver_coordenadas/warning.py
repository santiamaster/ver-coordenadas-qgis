# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Textos y configuración visual de avisos para mediciones geográficas."""

GEOGRAPHIC_AREA_WARNING = (
    "Aviso: La superficie mostrada es una medición aproximada calculada sobre "
    "coordenadas geográficas. Realice el cálculo sobre la geometría en un "
    "sistema de coordenadas plano."
)

GEOGRAPHIC_LENGTH_WARNING = (
    "Aviso: La longitud mostrada es una medición aproximada calculada sobre "
    "coordenadas geográficas. Realice el cálculo sobre la geometría en un "
    "sistema de coordenadas plano."
)


def measurement_warning_text(
    geographic_coordinates: bool,
    has_polygon: bool,
    has_line: bool,
) -> str:
    """Devuelve el aviso correspondiente a la medición de una capa geográfica."""
    if not geographic_coordinates:
        return ""

    if has_polygon:
        return GEOGRAPHIC_AREA_WARNING

    if has_line:
        return GEOGRAPHIC_LENGTH_WARNING

    return ""


def configure_warning_label(label, warning_text: str) -> None:
    """Configura un QLabel para que el aviso se adapte al ancho de la ventana."""
    label.setText(warning_text)
    label.setWordWrap(True)
    label.setVisible(bool(warning_text))
