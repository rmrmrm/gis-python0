from spatial_utils import IMGS_DIR, fetch_all, get_connection, print_results, render_spatial_map


def task_5_main(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city, c.state_abrv
        FROM us_cities c
        WHERE ROWID IN (
          SELECT c.rowid FROM us_interstates i, us_cities c
          WHERE i.interstate = 'I4'
            AND sdo_within_distance(c.location, i.geom, 'distance=50 unit=mile') = 'TRUE'
        )
        ORDER BY c.city
        """,
    )
    print_results("Zad. 5 — miasta w 50 mi od I-4", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state_abrv = 'FL'",
                "kind": "polygon",
                "name": "Floryda",
                "facecolor": "#f4c77a",
                "edgecolor": "#c88719",
                "alpha": 0.45,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(SDO_GEOM.SDO_BUFFER(i.geom, 50, 0.005, 'unit=MILE')), 'Bufor 50 mi'
                    FROM us_interstates i WHERE i.interstate = 'I4'
                """,
                "kind": "polygon",
                "name": "Bufor 50 mil",
                "facecolor": "#80deea",
                "edgecolor": "#00838f",
                "alpha": 0.25,
                "zorder": 2,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), 'I-4' FROM us_interstates WHERE interstate = 'I4'",
                "kind": "line",
                "name": "Autostrada I-4",
                "color": "#d32f2f",
                "width": 4,
                "label_features": True,
                "zorder": 4,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location), c.city || ', ' || c.state_abrv
                    FROM us_cities c
                    WHERE ROWID IN (
                      SELECT c.rowid FROM us_interstates i, us_cities c
                      WHERE i.interstate = 'I4'
                        AND sdo_within_distance(c.location, i.geom, 'distance=50 unit=mile') = 'TRUE'
                    )
                """,
                "kind": "point",
                "name": "Miasta (≤50 mi)",
                "color": "#0d47a1",
                "size": 10,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "5.1.png",
        title="Zadanie 5 — Miasta w odległości 50 mil od autostrady I-4",
        subtitle="SDO_WITHIN_DISTANCE · warstwy: FL, bufor 50 mi, I-4, miasta",
    )
    return len(rows)


def task_5a(conn):
    cols, rows = fetch_all(conn, """
        SELECT i.interstate FROM us_interstates i, us_rivers r
        WHERE r.name = 'Mississippi' AND SDO_ANYINTERACT(i.geom, r.geom) = 'TRUE'
        ORDER BY i.interstate
    """)
    print_results("Zad. 5a — drogi przecinające Mississippi", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Louisiana','Mississippi','Arkansas','Tennessee','Missouri','Illinois','Iowa','Minnesota','Wisconsin')
                """,
                "kind": "polygon",
                "name": "Stany (kontekst)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.3,
                "zorder": 1,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), 'Mississippi' FROM us_rivers WHERE name = 'Mississippi'",
                "kind": "line",
                "name": "Rzeka Mississippi",
                "color": "#1565c0",
                "width": 3.5,
                "label_features": True,
                "zorder": 3,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(i.geom), i.interstate
                    FROM us_interstates i, us_rivers r
                    WHERE r.name = 'Mississippi' AND SDO_ANYINTERACT(i.geom, r.geom) = 'TRUE'
                """,
                "kind": "line",
                "name": "Autostrady (15)",
                "color": "#d32f2f",
                "width": 2.5,
                "label_features": False,
                "zorder": 4,
            },
        ],
        png_path=IMGS_DIR / "5a.png",
        title="Zadanie 5a — Drogi przecinające rzekę Mississippi",
        subtitle="SDO_ANYINTERACT · 15 autostrad (I10, I20, I40, I55, I90…)",
    )
    return len(rows)


def task_5b(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city, c.state_abrv,
               ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
        FROM us_interstates i, us_cities c
        WHERE i.interstate = 'I275'
          AND sdo_within_distance(c.location, i.geom, 'distance=30 unit=mile') = 'TRUE'
          AND SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE') > 15
        ORDER BY dist_mile
        """,
    )
    print_results("Zad. 5b — miasta 15–30 mi od I-275", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state_abrv IN ('MI', 'OH', 'KY', 'IN')
                """,
                "kind": "polygon",
                "name": "Stany (MI, OH, KY, IN)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.35,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(SDO_GEOM.SDO_INTERSECTION(i.geom, s.geom)), 'I-275'
                    FROM us_interstates i, us_states s
                    WHERE i.interstate = 'I275' AND s.state_abrv = 'MI'
                """,
                "kind": "line",
                "name": "Autostrada I-275",
                "color": "#d32f2f",
                "width": 4,
                "label_features": True,
                "zorder": 3,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location),
                           c.city || ' (' || ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) || ' mi)'
                    FROM us_interstates i, us_cities c
                    WHERE i.interstate = 'I275'
                      AND sdo_within_distance(c.location, i.geom, 'distance=30 unit=mile') = 'TRUE'
                      AND SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE') > 15
                """,
                "kind": "point",
                "name": "Miasta 15–30 mi",
                "color": "#2e7d32",
                "size": 10,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "5b.png",
        title="Zadanie 5b — Miasta w odległości 15–30 mil od I-275",
        subtitle="SDO_WITHIN_DISTANCE (30 mi) + SDO_DISTANCE > 15 mi",
    )
    return len(rows)


def task_5c(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city, c.state_abrv
        FROM us_cities c, us_parks p
        WHERE p.name = 'Yellowstone NP'
          AND sdo_within_distance(c.location, p.geom, 'distance=300 unit=mile') = 'TRUE'
        ORDER BY c.city
        """,
    )
    print_results("Zad. 5c — miasta w 300 mi od Yellowstone NP", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Wyoming','Montana','Idaho','Utah','Colorado')
                """,
                "kind": "polygon",
                "name": "Stany (region)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.35,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(SDO_GEOM.SDO_BUFFER(p.geom, 300, 0.005, 'unit=MILE')), '300 mi'
                    FROM us_parks p WHERE p.name = 'Yellowstone NP'
                """,
                "kind": "polygon",
                "name": "Bufor 300 mil",
                "facecolor": "#80deea",
                "edgecolor": "#00838f",
                "alpha": 0.2,
                "zorder": 2,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), 'Yellowstone NP' FROM us_parks WHERE name = 'Yellowstone NP'",
                "kind": "polygon",
                "name": "Yellowstone NP",
                "facecolor": "#66bb6a",
                "edgecolor": "#1b5e20",
                "alpha": 0.7,
                "label_features": True,
                "zorder": 3,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location), c.city || ', ' || c.state_abrv
                    FROM us_cities c, us_parks p
                    WHERE p.name = 'Yellowstone NP'
                      AND sdo_within_distance(c.location, p.geom, 'distance=300 unit=mile') = 'TRUE'
                """,
                "kind": "point",
                "name": "Miasta w zasięgu",
                "color": "#e65100",
                "size": 10,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "5c.png",
        title="Zadanie 5c — Miasta w promieniu 300 mil od Yellowstone NP",
        subtitle="SDO_WITHIN_DISTANCE · własny przykład",
    )
    return len(rows)


if __name__ == "__main__":
    conn = get_connection()
    try:
        n5 = task_5_main(conn)
        na = task_5a(conn)
        nb = task_5b(conn)
        nc = task_5c(conn)
        print(f"\nPodsumowanie: 5={n5}, 5a={na}, 5b={nb}, 5c={nc}")
    finally:
        conn.close()
