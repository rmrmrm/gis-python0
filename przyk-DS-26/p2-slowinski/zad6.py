from spatial_utils import IMGS_DIR, fetch_all, get_connection, print_results, render_spatial_map

SQL_NY = """
SELECT sdo_util.to_wktgeometry(location), 'New York City' AS label
FROM us_cities WHERE city = 'New York' AND state_abrv = 'NY'
"""

SQL_6A_PARKS = """
SELECT sdo_util.to_wktgeometry(name_geom), label FROM (
  SELECT p2.geom AS name_geom,
         p2.name || ' (' || ROUND(SDO_GEOM.SDO_DISTANCE(c2.location, p2.geom, 0.005, 'unit=MILE'), 1) || ' mi)' AS label
  FROM us_parks p2, us_cities c2
  WHERE c2.city = 'New York' AND c2.state_abrv = 'NY'
    AND p2.name LIKE '% NP'
  ORDER BY SDO_GEOM.SDO_DISTANCE(c2.location, p2.geom, 0.005, 'unit=MILE')
) WHERE ROWNUM <= 3
"""


def task_6_main(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city, c.state_abrv
        FROM us_interstates i, us_cities c
        WHERE i.interstate = 'I4'
          AND sdo_nn(c.location, i.geom, 'sdo_num_res=5') = 'TRUE'
        ORDER BY c.city
        """,
    )
    print_results("Zad. 6 — 5 miast najbliżej I-4", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state_abrv = 'FL'",
                "kind": "polygon",
                "name": "Floryda",
                "facecolor": "#f4c77a",
                "edgecolor": "#c88719",
                "alpha": 0.4,
                "zorder": 1,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), 'I-4' FROM us_interstates WHERE interstate = 'I4'",
                "kind": "line",
                "name": "Autostrada I-4",
                "color": "#d32f2f",
                "width": 4,
                "label_features": True,
                "zorder": 3,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location), c.city || ', ' || c.state_abrv
                    FROM us_interstates i, us_cities c
                    WHERE i.interstate = 'I4'
                      AND sdo_nn(c.location, i.geom, 'sdo_num_res=5') = 'TRUE'
                """,
                "kind": "point",
                "name": "5 miast (SDO_NN)",
                "color": "#0d47a1",
                "size": 10,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "6.1.png",
        title="Zadanie 6 — 5 miast najbliższych autostradzie I-4",
        subtitle="SDO_NN (sdo_num_res=5)",
    )
    return rows


def task_6a(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT name, dist_mile FROM (
          SELECT p.name,
                 ROUND(SDO_GEOM.SDO_DISTANCE(c.location, p.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
          FROM us_parks p, us_cities c
          WHERE c.city = 'New York' AND c.state_abrv = 'NY'
            AND p.name LIKE '% NP'
          ORDER BY dist_mile
        ) WHERE ROWNUM <= 3
        """,
    )
    print_results("Zad. 6a — 3 parki narodowe najbliżej NYC + odległości", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('New York','New Jersey','Pennsylvania','Connecticut','Massachusetts',
                                    'Vermont','New Hampshire','Maine','Maryland','Virginia','West Virginia',
                                    'North Carolina','Tennessee','Kentucky','Ohio')
                """,
                "kind": "polygon",
                "name": "Stany (wschód USA)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.35,
                "zorder": 1,
            },
            {
                "sql": SQL_6A_PARKS,
                "kind": "polygon",
                "name": "Parki narodowe (3)",
                "facecolor": "#66bb6a",
                "edgecolor": "#1b5e20",
                "alpha": 0.75,
                "label_features": False,
                "zorder": 3,
            },
            {
                "sql": SQL_NY,
                "kind": "point",
                "name": "New York City",
                "color": "#212121",
                "size": 12,
                "label_features": True,
                "zorder": 6,
            },
        ],
        connect=[
            {
                "from_sql": SQL_NY,
                "to_sql": SQL_6A_PARKS,
                "color": "#616161",
            }
        ],
        png_path=IMGS_DIR / "6a.png",
        title="Zadanie 6a — 3 parki narodowe najbliżej Nowego Jorku",
        subtitle="SDO_NN + SDO_DISTANCE · Shenandoah (255.9 mi), Acadia (354.8 mi), Great Smoky Mts (601.2 mi)",
    )
    return rows


def task_6b(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT city, state_abrv, pop90, dist_mile FROM (
          SELECT c.city, c.state_abrv, c.pop90,
                 ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) AS dist_mile
          FROM us_cities c, us_interstates i
          WHERE i.interstate = 'I170'
            AND c.pop90 > 300000
            AND SDO_NN(c.location, i.geom, 'sdo_num_res=100') = 'TRUE'
          ORDER BY dist_mile
        ) WHERE ROWNUM <= 5
        """,
    )
    print_results("Zad. 6b — 5 dużych miast przy I-170", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(geom), state
                    FROM us_states
                    WHERE state IN ('Missouri','Illinois','Indiana','Ohio','Kentucky','Tennessee',
                                    'Arkansas','Mississippi','Alabama','Kansas','Oklahoma','Iowa','Wisconsin')
                """,
                "kind": "polygon",
                "name": "Stany (region)",
                "facecolor": "#e8dcc8",
                "edgecolor": "#b0a090",
                "alpha": 0.3,
                "zorder": 1,
            },
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), 'I-170' FROM us_interstates WHERE interstate = 'I170'",
                "kind": "line",
                "name": "Autostrada I-170",
                "color": "#d32f2f",
                "width": 4,
                "label_features": True,
                "zorder": 3,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location),
                           c.city || ', ' || c.state_abrv || ' · ' ||
                           ROUND(SDO_GEOM.SDO_DISTANCE(c.location, i.geom, 0.005, 'unit=MILE'), 1) || ' mi'
                    FROM us_cities c, us_interstates i
                    WHERE i.interstate = 'I170' AND c.pop90 > 300000
                      AND c.city IN (
                        SELECT city FROM (
                          SELECT c2.city
                          FROM us_cities c2, us_interstates i2
                          WHERE i2.interstate = 'I170' AND c2.pop90 > 300000
                          ORDER BY SDO_GEOM.SDO_DISTANCE(c2.location, i2.geom, 0.005, 'unit=MILE')
                        ) WHERE ROWNUM <= 5
                      )
                """,
                "kind": "point",
                "name": "Miasta >300k (5)",
                "color": "#6a1b9a",
                "size": 10,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "6b.png",
        title="Zadanie 6b — 5 najbliższych dużych miast przy I-170",
        subtitle="SDO_NN + POP90 > 300 000 · St Louis, Kansas City, Indianapolis, Memphis, Chicago",
    )
    return rows


def task_6c(conn):
    cols, rows = fetch_all(
        conn,
        """
        SELECT c.city,
               ROUND(SDO_GEOM.SDO_LENGTH(
                 SDO_GEOM.SDO_BUFFER(c.location, 20, 0.005, 'unit=MILE'), 0.005, 'unit=MILE'
               ), 1) AS buffer_perimeter_mile
        FROM us_cities c
        WHERE c.city = 'Denver' AND c.state_abrv = 'CO'
        """,
    )
    print_results("Zad. 6c — SDO_BUFFER wokół Denver (20 mi)", cols, rows)

    render_spatial_map(
        conn,
        layers=[
            {
                "sql": "SELECT sdo_util.to_wktgeometry(geom), state FROM us_states WHERE state_abrv = 'CO'",
                "kind": "polygon",
                "name": "Kolorado",
                "facecolor": "#f4c77a",
                "edgecolor": "#c88719",
                "alpha": 0.35,
                "zorder": 1,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(
                      SDO_GEOM.SDO_BUFFER(c.location, 20, 0.005, 'unit=MILE')
                    ), 'Bufor 20 mi'
                    FROM us_cities c
                    WHERE c.city = 'Denver' AND c.state_abrv = 'CO'
                """,
                "kind": "polygon",
                "name": "SDO_BUFFER 20 mil",
                "facecolor": "#26c6da",
                "edgecolor": "#00838f",
                "alpha": 0.35,
                "label_features": True,
                "zorder": 2,
            },
            {
                "sql": """
                    SELECT sdo_util.to_wktgeometry(c.location), 'Denver, CO'
                    FROM us_cities c
                    WHERE c.city = 'Denver' AND c.state_abrv = 'CO'
                """,
                "kind": "point",
                "name": "Denver",
                "color": "#212121",
                "size": 12,
                "label_features": True,
                "zorder": 5,
            },
        ],
        png_path=IMGS_DIR / "6c.png",
        title="Zadanie 6c — SDO_BUFFER wokół Denver (promień 20 mil)",
        subtitle="Obwód bufora ≈ 125.7 mi · SDO_GEOM.SDO_BUFFER",
    )
    return rows


if __name__ == "__main__":
    conn = get_connection()
    try:
        r6 = task_6_main(conn)
        r6a = task_6a(conn)
        r6b = task_6b(conn)
        r6c = task_6c(conn)
        print(f"\nPodsumowanie: 6={len(r6)}, 6a={len(r6a)}, 6b={len(r6b)}, 6c={len(r6c)}")
    finally:
        conn.close()
