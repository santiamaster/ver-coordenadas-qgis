# Ver Coordenadas
# Copyright (C) 2026 Secretaría de Minería de Salta
# Desarrollado y mantenido por: Carlos Daniel Santiápichi Mastrolinardo
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Este programa es software libre: puede redistribuirlo y/o modificarlo
# bajo los términos de la GNU General Public License publicada por la
# Free Software Foundation, versión 2 de la Licencia o, a su elección,
# cualquier versión posterior.

"""Punto de entrada del plugin Ver Coordenadas para QGIS."""


def classFactory(iface):
    """Crea la instancia principal del plugin cuando QGIS lo carga."""
    from .plugin import VerCoordenadasPlugin

    return VerCoordenadasPlugin(iface)
