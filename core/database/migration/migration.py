import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import mysql.connector
from core.database.tables.users import table_user
from core.database.tables.categories import table_categories
from core.database.tables.incidents import table_incidents
from core.database.tables.investigation_notes import table_investigation_notes
from core.database.tables.attachments import table_attachments
from core.database.tables.chats import table_chats
from core.database.tables.audit_logs import table_audit_logs



def get_database():
    database = mysql.connector.connect(
        host="localhost",
        user="glitcher",
        passwd="glitcher",
        database="cimsapi"
    )
    return database

def migrate():
    database = mysql.connector.connect(
        host="localhost",
        user="glitcher",
        passwd="glitcher",
        database="cimsapi"
    )

    mycursor = database.cursor()

    #Create database and use it
    mycursor.execute("USE cimsapi")

    #Create table users
    mycursor.execute(table_user())
    mycursor.execute(table_categories())
    mycursor.execute(table_incidents())
    mycursor.execute(table_investigation_notes())
    mycursor.execute(table_attachments())
    mycursor.execute(table_chats())
    mycursor.execute(table_audit_logs())
    mycursor.execute("ALTER TABLE incidents MODIFY assigned_to INT NULL")
    

if __name__ == "__main__":
    migrate()
