import time
from pathlib import Path

import folium
import geojson
import oracledb
from shapely import wkt
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon
from shapely.ops import unary_union

LAB_DIR = Path(__file__).resolve().parent
MAPS_DIR = LAB_DIR / "maps"
IMGS_DIR = LAB_DIR.parent / "imgs"

DSN = oracledb.makedsn("dbmanage.lab.ii.agh.edu.pl", 1521, sid="DBMANAGE")
USER = "student"
PASSWORD = "stu638dent"

MAP_BG = "#ddd6ee"
PALETTE = {
    "state": {"face": "#f4c77a", "edge": "#c88719", "alpha": 0.55},
    "state_light": {"face": "#e8dcc8", "edge": "#b0a090", "alpha": 0.35},
    "road": {"color": "#d32f2f", "width": 3.5},
    "river": {"color": "#1565c0", "width": 3.0},
    "city": {"color": "#0d47a1", "marker": "o", "size": 9},
    "city_alt": {"color": "#2e7d32", "marker": "o", "size": 9},
    "park": {"face": "#66bb6a", "edge": "#1b5e20", "alpha": 0.65},
    "buffer": {"face": "#26c6da", "edge": "#00838f", "alpha": 0.25},
    "highlight": {"face": "#fff176", "edge": "#f9a825", "alpha": 0.7},
    "rect": {"face": "#00e5ff", "edge": "#0097a7", "alpha": 0.35},
}


def output_type_handler(cursor, name, default_type, size, precision, scale):
    if default_type == oracledb.CLOB:
        return cursor.var(oracledb.LONG_STRING, arraysize=cursor.arraysize)


def get_connection():
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    conn.outputtypehandler = output_type_handler
    cur = conn.cursor()
    cur.execute("ALTER SESSION SET CURRENT_SCHEMA = US_SPAT")
    cur.close()
    return conn


def fetch_all(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or {})
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    return cols, rows


def fetch_wkt_rows(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    rows = [(row[0], row[1] if len(row) > 1 else "") for row in cur if row[0]]
    cur.close()
    return rows


def _iter_parts(geom):
    if geom is None or geom.is_empty:
        return
    if isinstance(geom, (Point, LineString, Polygon)):
        yield geom
    else:
        yield from geom.geoms


def _geom_center(geom):
    if isinstance(geom, Point):
        return geom.x, geom.y
    return geom.centroid.x, geom.centroid.y


def _line_midpoint(geom):
    if isinstance(geom, LineString):
        line = geom
    elif isinstance(geom, MultiLineString):
        line = max(geom.geoms, key=lambda g: g.length)
    else:
        return _geom_center(geom)
    mid = line.interpolate(0.5, normalized=True)
    return mid.x, mid.y


def _bounds_from_geoms(geoms, pad_ratio=0.08):
    all_geoms = [g for g in geoms if g and not g.is_empty]
    if not all_geoms:
        return (-125, 24, -66, 50)
    u = unary_union(all_geoms)
    minx, miny, maxx, maxy = u.bounds
    pad_x = max((maxx - minx) * pad_ratio, 0.5)
    pad_y = max((maxy - miny) * pad_ratio, 0.5)
    return minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y


def render_spatial_map(
    conn,
    layers: list[dict],
    png_path: Path,
    title: str,
    subtitle: str = "",
    connect: list[dict] | None = None,
):
    import matplotlib.pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch, Polygon as MplPolygon

    parsed_layers = []
    all_geoms = []

    for layer in layers:
        rows = fetch_wkt_rows(conn, layer["sql"])
        features = []
        for wkt_str, label in rows:
            geom = wkt.loads(wkt_str)
            features.append((geom, str(label)))
            all_geoms.append(geom)
        parsed_layers.append({**layer, "features": features})

    if connect:
        for spec in connect:
            from_rows = fetch_wkt_rows(conn, spec["from_sql"])
            to_rows = fetch_wkt_rows(conn, spec["to_sql"])
            if from_rows and to_rows:
                fgeom = wkt.loads(from_rows[0][0])
                parsed_layers.append({
                    "kind": "connector",
                    "features": [(fgeom, from_rows[0][1])],
                    "targets": [(wkt.loads(t[0]), t[1]) for t in to_rows],
                    "color": spec.get("color", "#555555"),
                })

    minx, miny, maxx, maxy = _bounds_from_geoms(all_geoms, pad_ratio=0.08)
    x_range = maxx - minx
    y_range = max(maxy - miny, 0.5)
    data_ratio = x_range / y_range

    max_plot_w = 9.0
    max_plot_h = 7.0
    min_plot_w = 3.5
    min_plot_h = 2.5

    if data_ratio >= 1:
        plot_w_in = max_plot_w
        plot_h_in = max(min(plot_w_in / data_ratio, max_plot_h), min_plot_h)
    else:
        plot_h_in = max_plot_h
        plot_w_in = max(min(plot_h_in * data_ratio, max_plot_w), min_plot_w)

    margin_top_in = 0.95
    margin_bottom_in = 0.55
    margin_left_in = 0.70
    margin_right_in = 0.30
    fig_w_in = margin_left_in + plot_w_in + margin_right_in
    fig_h_in = margin_bottom_in + plot_h_in + margin_top_in

    fig = plt.figure(figsize=(fig_w_in, fig_h_in), facecolor=MAP_BG)
    ax = fig.add_axes(
        [
            margin_left_in / fig_w_in,
            margin_bottom_in / fig_h_in,
            plot_w_in / fig_w_in,
            plot_h_in / fig_h_in,
        ],
        facecolor=MAP_BG,
    )

    legend_handles = []

    for layer in parsed_layers:
        kind = layer.get("kind", "polygon")
        name = layer.get("name", "")
        zorder = layer.get("zorder", 2)

        if kind == "connector":
            fx, fy = _geom_center(layer["features"][0][0])
            for tgeom, tlabel in layer["targets"]:
                tx, ty = _geom_center(tgeom)
                ax.plot([fx, tx], [fy, ty], "--", color=layer["color"], linewidth=1.2, alpha=0.55, zorder=1)
                ax.annotate(
                    tlabel,
                    (tx, ty),
                    xytext=(8, 8),
                    textcoords="offset points",
                    fontsize=8,
                    color="#1b5e20",
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.9, edgecolor="#1b5e20"),
                    zorder=10,
                )
                mid_x, mid_y = (fx + tx) / 2, (fy + ty) / 2
                dist = tlabel.split("(")[-1].rstrip(")") if "(" in tlabel else ""
                if dist:
                    ax.annotate(
                        dist,
                        (mid_x, mid_y),
                        fontsize=7,
                        color="#424242",
                        ha="center",
                        bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=0.75, edgecolor="none"),
                        zorder=6,
                    )
            continue

        if kind == "polygon":
            face = layer.get("facecolor", PALETTE["state"]["face"])
            edge = layer.get("edgecolor", PALETTE["state"]["edge"])
            alpha = layer.get("alpha", PALETTE["state"]["alpha"])
            patches = []
            for geom, label in layer["features"]:
                for part in _iter_parts(geom):
                    if isinstance(part, Polygon):
                        patches.append(MplPolygon(list(part.exterior.coords), closed=True))
                        if layer.get("label_features") and label:
                            cx, cy = part.centroid.x, part.centroid.y
                            ax.annotate(
                                label,
                                (cx, cy),
                                fontsize=8,
                                ha="center",
                                color=edge,
                                fontweight="bold",
                                zorder=8,
                            )
            if patches:
                pc = PatchCollection(
                    patches,
                    facecolor=face,
                    edgecolor=edge,
                    linewidth=1.2,
                    alpha=alpha,
                    zorder=zorder,
                )
                ax.add_collection(pc)
            legend_handles.append(Patch(facecolor=face, edgecolor=edge, alpha=alpha, label=name))

        elif kind == "line":
            color = layer.get("color", PALETTE["road"]["color"])
            width = layer.get("width", PALETTE["road"]["width"])
            for geom, label in layer["features"]:
                for part in _iter_parts(geom):
                    if isinstance(part, LineString):
                        xs, ys = part.xy
                        ax.plot(xs, ys, color=color, linewidth=width, solid_capstyle="round", zorder=zorder + 1)
                if layer.get("label_features") and label:
                    mx, my = _line_midpoint(geom)
                    ax.annotate(
                        label,
                        (mx, my),
                        fontsize=10,
                        fontweight="bold",
                        color=color,
                        ha="center",
                        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.85, edgecolor=color),
                        zorder=9,
                    )
            legend_handles.append(Line2D([0], [0], color=color, linewidth=width, label=name))

        elif kind == "point":
            color = layer.get("color", PALETTE["city"]["color"])
            size = layer.get("size", PALETTE["city"]["size"])
            marker = layer.get("marker", "o")
            for geom, label in layer["features"]:
                for part in _iter_parts(geom):
                    if isinstance(part, Point):
                        ax.scatter(
                            part.x,
                            part.y,
                            c=color,
                            s=size ** 2,
                            marker=marker,
                            edgecolors="white",
                            linewidths=1.2,
                            zorder=zorder + 2,
                        )
                        if layer.get("label_features") and label:
                            ax.annotate(
                                label,
                                (part.x, part.y),
                                xytext=(6, 6),
                                textcoords="offset points",
                                fontsize=9,
                                fontweight="bold",
                                color="#212121",
                                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.9, edgecolor=color),
                                zorder=10,
                            )
            legend_handles.append(
                Line2D(
                    [0], [0],
                    marker=marker,
                    color="w",
                    markerfacecolor=color,
                    markersize=size,
                    label=name,
                )
            )

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.grid(True, color="white", linewidth=0.8, alpha=0.9)
    ax.set_xlabel("Długość geograficzna (°)", fontsize=10)
    ax.set_ylabel("Szerokość geograficzna (°)", fontsize=10)

    ax_top = (margin_bottom_in + plot_h_in) / fig_h_in
    gap = 0.022
    if subtitle:
        fig.text(0.5, ax_top + gap + 0.055, title, ha="center", va="bottom", fontsize=13, fontweight="bold")
        fig.text(0.5, ax_top + gap, subtitle, ha="center", va="bottom", fontsize=9, color="#424242")
    else:
        fig.text(0.5, ax_top + gap + 0.02, title, ha="center", va="bottom", fontsize=13, fontweight="bold")

    if legend_handles:
        ax.legend(
            handles=legend_handles,
            loc="lower right",
            framealpha=0.92,
            fontsize=8,
            title="Warstwy",
            title_fontsize=8,
        )

    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=150, facecolor=MAP_BG, pad_inches=0.08)
    plt.close(fig)
    return True


def save_query_map_png(conn, layer_specs, png_path: Path, title: str = "", subtitle: str = ""):
    layers = []
    for spec in layer_specs:
        sql = spec["sql"]
        color = spec.get("color", "blue")
        if spec.get("kind") == "line" or spec.get("as_line"):
            layers.append({"sql": sql, "kind": "line", "color": color, "name": spec.get("name", ""), "label_features": spec.get("labels", False)})
        elif spec.get("kind") == "point" or spec.get("as_point"):
            layers.append({"sql": sql, "kind": "point", "color": color, "name": spec.get("name", ""), "label_features": spec.get("labels", True)})
        else:
            layers.append({
                "sql": sql,
                "kind": "polygon",
                "facecolor": color,
                "edgecolor": spec.get("edgecolor", color),
                "alpha": spec.get("alpha", 0.5),
                "name": spec.get("name", ""),
                "label_features": spec.get("labels", False),
            })
    return render_spatial_map(conn, layers, png_path, title, subtitle)


def make_map(center=(39, -98), zoom=4):
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    return folium.Map(location=list(center), zoom_start=zoom, tiles="OpenStreetMap")


def add_wkt_layer(m, sql, conn, style=None, name="layer", tooltip_field="label"):
    style = style or {"fillColor": "#3388ff", "color": "#3388ff", "weight": 2, "fillOpacity": 0.4}
    cur = conn.cursor()
    cur.execute(sql)
    features = []
    for row in cur:
        wkt_str = row[0]
        if not wkt_str:
            continue
        label = str(row[1]) if len(row) > 1 else name
        geom = wkt.loads(wkt_str)
        features.append(geojson.Feature(geometry=geom, properties={"label": label}))
    cur.close()
    if features:
        gj = folium.GeoJson(
            geojson.FeatureCollection(features),
            name=name,
            style_function=lambda x, s=style: s,
            tooltip=folium.GeoJsonTooltip(fields=["label"], aliases=[name + ":"]),
        )
        gj.add_to(m)
    folium.LayerControl().add_to(m)


def save_map(m, filename: str) -> Path:
    MAPS_DIR.mkdir(parents=True, exist_ok=True)
    path = MAPS_DIR / filename
    m.save(str(path))
    return path


def save_html_screenshot(html_path: Path, png_path: Path, wait_sec: float = 2.0):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        return False

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--allow-file-access-from-files")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(html_path.as_uri())
        time.sleep(wait_sec)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(png_path))
        return True
    except Exception:
        return False
    finally:
        driver.quit()


def print_results(title, cols, rows, limit=20):
    print(f"\n=== {title} ({len(rows)} rows) ===")
    print(" | ".join(cols))
    for row in rows[:limit]:
        print(" | ".join(str(v) for v in row))
    if len(rows) > limit:
        print(f"... and {len(rows) - limit} more")
