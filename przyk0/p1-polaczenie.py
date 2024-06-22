import oracledb

from shapely.wkb import loads
import geopandas as gpd


# ---------------------------------------
# połączenie wykorzystujące service name
# ---------------------------------------


# RMHP LAB VM dom z dom M1
# un = "us_spat"
# pw = "st7839a67"
# cs = "192.168.113.198:11521/orcl"


# RMHP dock dom z dom M1
# un = "us_spat"
# pw = "us_spat"
# cs = "192.168.113.198:1521/FREEPDB1"


#  GABI LAB VM z dom M1 (wymagany port forwarding)
# un = "us_spat"
# pw = "st7839a67"
# cs = "127.0.0.1:41521/orcl"


# GABI dock z dom M1  (wymagany port forwarding)
# un = "us_spat"
# pw = "us_spat"
# cs = "127.0.0.1:11521/FREEPDB1"


# ---------------------------------------
# połączenie wykorzystujące sid
# dbmanage.lab.ii.agh.edu.pl
# ---------------------------------------
un = "student"
pw = "stu638dent"
cs = oracledb.makedsn("dbmanage.lab.ii.agh.edu.pl", 1521, sid="DBMANAGE")



connection = oracledb.connect(user=un, password=pw, dsn=cs)

print(connection)

q = """ALTER SESSION SET CURRENT_SCHEMA = US_SPAT"""

cursor = connection.cursor()

cursor.execute(q)




# cursor = connection.cursor()
# for row in cursor.execute("select state from us_states"):
#     print(row)
#
# cursor = connection.cursor()
# for row in cursor.execute("select * from us_states"):
#     print(row)

cursor = connection.cursor()

def OutputTypeHandler(cursor, name, defaultType, size, precision, scale):
    if defaultType == oracledb.CLOB:
        return cursor.var(oracledb.LONG_STRING, arraysize = cursor.arraysize)

connection.outputtypehandler = OutputTypeHandler


r = cursor.execute("""
        SELECT geom
        FROM us_states""").fetchone()

print(r)

r = cursor.execute("""
        SELECT sdo_util.to_wktgeometry(geom)
        FROM us_states""").fetchone()

print(r)

cursor.execute("""
        SELECT state, sdo_util.to_wktgeometry(geom) g
        FROM us_states""")

gdf = gpd.GeoDataFrame(cursor.fetchall(), columns=['state', 'g'])
del gdf['g']


print()
print(gdf)



