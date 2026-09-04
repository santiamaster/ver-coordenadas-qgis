# Changelog

All notable changes to **Ver Coordenadas** will be documented in this file.

## 1.0.0

Initial public release candidate.

- Adds the contextual **Ver coordenadas** action for line and polygon vector features.
- Supports Polygon, MultiPolygon, LineString and MultiLineString geometries.
- Lists vertices with continuous numbering and omits duplicated polygon closing vertices.
- Identifies polygon holes and reports their individual areas.
- Reports net polygon areas, multipart total areas, line lengths and multipart total lengths.
- Supports projected-coordinate display as Gauss-Krüger `(norte, este)` or traditional `(este, norte)` order.
- Supports geographic coordinates in DMS, DMM and decimal-degree formats.
- Uses ellipsoidal measurements for geographic CRS through `QgsDistanceArea`.
- Shows adaptive warnings for geographic area and length measurements.
- Copies coordinates and measurements automatically to the clipboard.
