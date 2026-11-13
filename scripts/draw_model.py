"""Small Draw.io authoring helpers for editable model diagrams."""

from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET


BLACK = "#000000"
WHITE = "#FFFFFF"
PORTS = {
    "left": (0, 0.5),
    "right": (1, 0.5),
    "top": (0.5, 0),
    "bottom": (0.5, 1),
    "center": (0.5, 0.5),
}


def _style(properties):
    return "".join(f"{key}={value};" for key, value in properties.items())


def _label(value):
    return escape(value, quote=False).replace("\n", "<br>")


class Page:
    def __init__(self, diagram, width, height):
        model = ET.SubElement(
            diagram, "mxGraphModel", grid="0", guides="1", connect="1",
            arrows="1", page="1", pageScale="1", pageWidth=str(width),
            pageHeight=str(height), background=WHITE,
        )
        self.root = ET.SubElement(model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.ids = {"0", "1"}
        self.vertices = set()

    def _cell(self, cell_id, **attributes):
        if cell_id in self.ids:
            raise ValueError(f"Duplicate cell id: {cell_id}")
        self.ids.add(cell_id)
        return ET.SubElement(self.root, "mxCell", id=cell_id, parent="1", **attributes)

    def _vertex(self, cell_id, value, x, y, width, height, **properties):
        styles = {
            "html": 1,
            "whiteSpace": "wrap",
            "fontFamily": "Arial",
            "fontSize": 15,
            "fontColor": BLACK,
            "align": "center",
            "verticalAlign": "middle",
            "spacing": 0,
        }
        styles.update(properties)
        cell = self._cell(cell_id, value=_label(value), vertex="1", style=_style(styles))
        ET.SubElement(
            cell, "mxGeometry", {"as": "geometry"},
            x=str(x), y=str(y), width=str(width), height=str(height),
        )
        self.vertices.add(cell_id)
        return cell_id

    def operator(self, cell_id, value, x, y, width=112, height=36, *, bold=False):
        return self._vertex(
            cell_id, value, x, y, width, height, shape="rectangle",
            rounded=0, fillColor=WHITE, strokeColor=BLACK, strokeWidth=1.35,
            fontStyle=int(bold),
        )

    def merge(self, cell_id, symbol, cx, cy, size=30):
        return self._vertex(
            cell_id, symbol, cx - size / 2, cy - size / 2, size, size,
            shape="ellipse", fillColor=WHITE, strokeColor=BLACK,
            strokeWidth=1.35, fontSize=22,
        )

    def junction(self, cell_id, cx, cy, size=6):
        return self._vertex(
            cell_id, "", cx - size / 2, cy - size / 2, size, size,
            shape="ellipse", fillColor=BLACK, strokeColor=BLACK,
        )

    def text(self, cell_id, value, x, y, width, height=20, *, size=13,
             bold=False, align="center"):
        return self._vertex(
            cell_id, value, x, y, width, height, shape="text",
            fillColor="none", strokeColor="none", fontSize=size,
            fontStyle=int(bold), align=align,
        )

    def divider(self, cell_id, x, y, width):
        return self._vertex(
            cell_id, "", x, y, width, 1, shape="line",
            strokeColor=BLACK, strokeWidth=1, dashed=1, dashPattern="7 6",
        )

    def edge(self, source, target, *, start="right", end="left", via=(),
             arrow=True, jump=False, dashed=False, cell_id=None):
        """Attach endpoints to cell ports and preserve explicit bend points."""
        for terminal in (source, target):
            if terminal not in self.vertices:
                raise ValueError(f"Unknown endpoint: {terminal}")
        exit_x, exit_y = PORTS[start] if isinstance(start, str) else start
        entry_x, entry_y = PORTS[end] if isinstance(end, str) else end
        properties = {
            "edgeStyle": "none",
            "rounded": 0,
            "html": 1,
            "endArrow": "block" if arrow else "none",
            "endSize": 6,
            "endFill": 1,
            "strokeColor": BLACK,
            "strokeWidth": 1.25,
            "exitX": exit_x,
            "exitY": exit_y,
            "exitPerimeter": 0,
            "entryX": entry_x,
            "entryY": entry_y,
            "entryPerimeter": 0,
        }
        if jump:
            properties.update(jumpStyle="arc", jumpSize=10)
        if dashed:
            properties["dashed"] = 1
        cell = self._cell(
            cell_id or f"{source}--{target}", edge="1", source=source,
            target=target, style=_style(properties),
        )
        geometry = ET.SubElement(cell, "mxGeometry", {"as": "geometry", "relative": "1"})
        if via:
            points = ET.SubElement(geometry, "Array", {"as": "points"})
            for x, y in via:
                ET.SubElement(points, "mxPoint", x=str(x), y=str(y))


class Drawio:
    def __init__(self):
        self.file = ET.Element("mxfile", host="app.diagrams.net", compressed="false")

    def page(self, name, width=1600, height=900):
        page_id = f"page-{len(self.file) + 1}"
        diagram = ET.SubElement(self.file, "diagram", id=page_id, name=name)
        return Page(diagram, width, height)

    def write(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(ET, "indent"):
            ET.indent(self.file, space="  ")
        ET.ElementTree(self.file).write(path, encoding="utf-8", xml_declaration=True)
