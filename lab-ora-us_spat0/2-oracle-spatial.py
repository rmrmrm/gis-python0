import oracledb
import folium
import geojson

from shapely.wkt import dumps, loads

cs = oracledb.makedsn("dbmanage.lab.ii.agh.edu.pl", 1521, sid="DBMANAGE")

un = "student"
pw = "stu638dent"

connection = oracledb.connect(user=un, password=pw, dsn=cs)

print(connection)

q = """ALTER SESSION SET CURRENT_SCHEMA = US_SPAT"""

cursor = connection.cursor()

cursor.execute(q)


def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == oracledb.CLOB:
        return cursor.var(oracledb.LONG_STRING, arraysize = cursor.arraysize)

connection.outputtypehandler = OutputTypeHandler


cursor = connection.cursor()

q = """select id, state from us_states""";

for row in cursor.execute(q):
    print(row)


m = folium.Map()

q = """SELECT  sdo_util.to_wktgeometry(geom)
       FROM us_states 
       WHERE state='Hawaii' or state = 'Texas'"""

r = loads(cursor.execute(q).fetchall())

st = {'fillColor': 'blue', 'color': 'red'}

l = []

for row in r:
    g = geojson.Feature(geometry=row[0], properties={})
    l.append(g)


feature_collection = geojson.FeatureCollection(l)

folium.GeoJson(feature_collection, style_function=lambda x:st).add_to(m)

m.show_in_browser()