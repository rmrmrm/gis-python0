-- Lab 10 - zadania 1-4
-- Jan Dworak, Miłosz Słowiński

ALTER SESSION SET CURRENT_SCHEMA = US_SPAT;

SELECT id, state, geom FROM us_states;

SELECT id, interstate, geom FROM us_interstates;

SELECT id, city, state_abrv, location FROM us_cities;

SELECT id, name, geom FROM us_rivers;

SELECT id, county, state_abrv, geom FROM us_counties;

SELECT id, name, geom FROM us_parks;

SELECT sdo_geometry (2003, 8307, null,
  sdo_elem_info_array (1,1003,3),
  sdo_ordinate_array ( -117.0, 40.0, -90., 44.0)) g
FROM dual;

SELECT state, geom FROM us_states
WHERE sdo_filter (geom,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE';

SELECT state, geom FROM us_states
WHERE sdo_anyinteract (geom,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE';

SELECT state, geom FROM us_states
WHERE sdo_anyinteract (geom,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0))
) = 'TRUE'
UNION ALL
SELECT 'RECT' AS state,
  sdo_geometry (2003, 8307, null,
    sdo_elem_info_array (1,1003,3),
    sdo_ordinate_array ( -117.0, 40.0, -90., 44.0)) AS geom
FROM dual;

SELECT p.name, p.geom
FROM us_parks p, us_states s
WHERE s.state = 'Wyoming'
  AND SDO_INSIDE (p.geom, s.geom) = 'TRUE';

SELECT pp.name, pp.geom FROM us_parks pp
WHERE id IN (
  SELECT p.id
  FROM us_parks p, us_states s
  WHERE s.state = 'Wyoming'
    AND SDO_INSIDE (p.geom, s.geom) = 'TRUE'
);

SELECT state, geom FROM us_states
WHERE state = 'Wyoming';

SELECT p.name, p.geom
FROM us_parks p, us_states s
WHERE s.state = 'Wyoming'
  AND SDO_ANYINTERACT (p.geom, s.geom) = 'TRUE';

SELECT pp.name, pp.geom FROM us_parks pp
WHERE id IN (
  SELECT p.id
  FROM us_parks p, us_states s
  WHERE s.state = 'Wyoming'
    AND SDO_ANYINTERACT (p.geom, s.geom) = 'TRUE'
);

SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
  AND SDO_RELATE (c.geom, s.geom, 'mask=INSIDE+COVEREDBY') = 'TRUE';

SELECT cc.county, cc.state_abrv, cc.geom FROM us_counties cc
WHERE id IN (
  SELECT c.id FROM us_counties c, us_states s
  WHERE s.state = 'New Hampshire'
    AND SDO_RELATE (c.geom, s.geom, 'mask=INSIDE+COVEREDBY') = 'TRUE'
);

SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
  AND SDO_RELATE (c.geom, s.geom, 'mask=INSIDE') = 'TRUE';

SELECT c.county, c.state_abrv, c.geom
FROM us_counties c, us_states s
WHERE s.state = 'New Hampshire'
  AND SDO_RELATE (c.geom, s.geom, 'mask=COVEREDBY') = 'TRUE';
