from spatial_utils import IMGS_DIR, fetch_all, get_connection, print_results, render_spatial_map


def task_7_1(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city,
               SDO_CONTAINS(s.geom, c.location) AS inside_texas
        FROM us_cities c, us_states s
        WHERE c.city = 'Austin' AND c.state_abrv = 'TX'
          AND s.state = 'Texas'
        """,
    )
    print_results("Zad. 7.1 — SDO_CONTAINS: Austin w Teksasie", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state = 'Texas'",
                "kind": "polygon",
                "name": "Teksas",
                "facecolor": "#f4c77a",
                "edgecolor": "#c88719",
                "alpha": 0.55,
                "label_features": True,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location), c.city || ', ' || c.state_abrv
                    FROM us_cities c
                    WHERE c.city = 'Austin' AND c.state_abrv = 'TX'
                """,
                "kind": "point",
                "name": "Austin",
                "color": "#0d47a1",
                "size": 12,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "7.1.png",
        title="Zadanie 7.1 — SDO_CONTAINS: Austin w Teksasie",
        subtitle="SDO_CONTAINS · punkt w wielokącie",
    )
    return rows


def task_7_2(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT s2.state
        FROM us_states s1, us_states s2
        WHERE s1.state = 'Arizona'
          AND s2.state <> 'Arizona'
          AND SDO_TOUCH(s1.geom, s2.geom) = 'TRUE'
        ORDER BY s2.state
        """,
    )
    print_results("Zad. 7.2 — SDO_TOUCH: sąsiedzi Arizony", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Arizona','California','Colorado','Nevada','New Mexico','Utah')
                """,
                "kind": "polygon",
                "name": "Stany (region)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.4,
                "label_features": False,
                "zorder": 1,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state = 'Arizona'",
                "kind": "polygon",
                "name": "Arizona",
                "facecolor": "#fff176",
                "edgecolor": "#f9a825",
                "alpha": 0.75,
                "label_features": True,
                "zorder": 2,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(s2.geom), s2.state
                    FROM us_states s1, us_states s2
                    WHERE s1.state = 'Arizona'
                      AND s2.state <> 'Arizona'
                      AND SDO_TOUCH(s1.geom, s2.geom) = 'TRUE'
                """,
                "kind": "polygon",
                "name": "Sąsiedzi (5)",
                "facecolor": "#80cbc4",
                "edgecolor": "#00695c",
                "alpha": 0.6,
                "label_features": True,
                "zorder": 3,
            },
        ],
        png_path=IMGS_DIR / "7.2.png",
        title="Zadanie 7.2 — SDO_TOUCH: sąsiedzi Arizony",
        subtitle="SDO_TOUCH · 5 stanów graniczących",
    )
    return rows


def task_7_3(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT name,
               ROUND(SDO_GEOM.SDO_AREA(geom, 0.005, 'unit=SQ_MILE'), 0) AS area_sq_mile
        FROM us_parks
        WHERE name IN ('Yellowstone NP', 'Yosemite NP')
        ORDER BY area_sq_mile DESC
        """,
    )
    print_results("Zad. 7.3 — SDO_AREA: Yellowstone vs Yosemite", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Wyoming','Montana','Idaho','California','Nevada')
                """,
                "kind": "polygon",
                "name": "Stany (region)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.3,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(p.geom),
                           p.name || ' (' ||
                           ROUND(SDO_GEOM.SDO_AREA(p.geom, 0.005, 'unit=SQ_MILE'), 0) || ' mi²)'
                    FROM us_parks p
                    WHERE p.name IN ('Yellowstone NP', 'Yosemite NP')
                """,
                "kind": "polygon",
                "name": "Parki narodowe",
                "facecolor": "#66bb6a",
                "edgecolor": "#1b5e20",
                "alpha": 0.75,
                "label_features": True,
                "zorder": 3,
            },
        ],
        png_path=IMGS_DIR / "7.3.png",
        title="Zadanie 7.3 — SDO_AREA: Yellowstone vs Yosemite",
        subtitle="SDO_GEOM.SDO_AREA · porównanie powierzchni",
    )
    return rows


def task_7_4(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT ROUND(SDO_GEOM.SDO_LENGTH(
                 SDO_GEOM.SDO_INTERSECTION(i.geom, s.geom),
                 0.005, 'unit=MILE'), 1) AS i80_len_in_ne
        FROM us_interstates i, us_states s
        WHERE i.interstate = 'I80' AND s.state = 'Nebraska'
        """,
    )
    print_results("Zad. 7.4 — SDO_INTERSECTION: I-80 w Nebraska", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Nebraska','Wyoming','Colorado','Iowa','Illinois','Kansas','Missouri')
                """,
                "kind": "polygon",
                "name": "Stany (region)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.35,
                "zorder": 1,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state = 'Nebraska'",
                "kind": "polygon",
                "name": "Nebraska",
                "facecolor": "#f4c77a",
                "edgecolor": "#c88719",
                "alpha": 0.55,
                "label_features": True,
                "zorder": 2,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(
                      SDO_GEOM.SDO_INTERSECTION(i.geom, s.geom)
                    ), 'I-80 w NE (' ||
                    ROUND(SDO_GEOM.SDO_LENGTH(
                      SDO_GEOM.SDO_INTERSECTION(i.geom, s.geom),
                      0.005, 'unit=MILE'), 1) || ' mi)'
                    FROM us_interstates i, us_states s
                    WHERE i.interstate = 'I80' AND s.state = 'Nebraska'
                """,
                "kind": "line",
                "name": "I-80 ∩ Nebraska",
                "color": "#d32f2f",
                "width": 4,
                "label_features": True,
                "zorder": 4,
            },
        ],
        png_path=IMGS_DIR / "7.4.png",
        title="Zadanie 7.4 — SDO_INTERSECTION: I-80 w Nebraska",
        subtitle="SDO_INTERSECTION + SDO_LENGTH · ~455.3 mi",
    )
    return rows


if __name__ == "__main__":
    conn = get_connection()
    try:
        r1 = task_7_1(conn)
        r2 = task_7_2(conn)
        r3 = task_7_3(conn)
        r4 = task_7_4(conn)
        print(f"\nPodsumowanie: 7.1={len(r1)}, 7.2={len(r2)}, 7.3={len(r3)}, 7.4={len(r4)}")
    finally:
        conn.close()
