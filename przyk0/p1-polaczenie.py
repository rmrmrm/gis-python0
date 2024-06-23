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

# GABI LAB VM z GABI
un = "us_spat"
pw = "st7839a67"
cs = "192.168.164.136:1521/orcl"

# GABI dock z GABI
# un = "us_spat"
# pw = "us_spat"
# cs = "127.0.0.1:1521/FREEPDB1"


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


q = """select id, state from us_states""";

for row in cursor.execute(q):
    print(row)


