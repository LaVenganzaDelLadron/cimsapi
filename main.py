import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="glitcher",
    passwd="glitcher",
    database="cimsapi"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")
for db in mycursor:
    print(db)