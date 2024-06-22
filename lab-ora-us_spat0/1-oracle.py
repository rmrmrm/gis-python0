import oracledb

cs = oracledb.makedsn("dbmanage.lab.ii.agh.edu.pl", 1521, sid="DBMANAGE")

un = "student"
pw = "stu638dent"

connection = oracledb.connect(user=un, password=pw, dsn=cs)

print(connection)

q = """ALTER SESSION SET CURRENT_SCHEMA = US_SPAT"""

cursor = connection.cursor()

cursor.execute(q)


cursor = connection.cursor()

q = """select id, state from us_states""";

for row in cursor.execute(q):
    print(row)