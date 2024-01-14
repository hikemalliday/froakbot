import Levenshtein
import sqlite3
import mysql.connector
from decouple import config as env
 
def levenshtein_distance(string1, string2):
    return Levenshtein.distance(string1, string2)

def create_levenshtein_function(bot: object):
    bot.db_connection.create_function("levenshtein", 2, levenshtein_distance)

def test_select(bot: object):
    c = bot.db_connection.cursor()
    c.execute('''SELECT * FROM items_virtual WHERE name = ?''', ('Amulet of Necropotence',))
    results = c.fetchall()

def drop_virtual_table(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE items_virtual''')
        bot.db_connection.commit()
    except Exception as e:
        print(e)

# Doesnt appear to be faster than regular table
def create_virtual_table(bot: object):
    
    try:
        c = bot.db_connection.cursor()
        c.execute('''CREATE VIRTUAL TABLE IF NOT EXISTS items_virtual USING fts5(
                  name,
                  id UNINDEXED
        )''')
        c.execute('''
            INSERT INTO items_virtual (name, id)
            SELECT name, id from items_master;            
        ''')
        bot.db_connection.commit()
        print('Virtual Table "items_virtual" created.')
    except Exception as e:
        print('Error creating virtual table:', e)
# Created from the Prject Quarm items database.
def create_items_master_table(bot: object):
    try:
        c1 = bot.db_connection.cursor()
        c1.execute('''CREATE Table IF NOT EXISTS items_master (
                id INTEGER PRIMARY KEY,
                name TEXT,
                icon INTEGER
        )''')
        bot.db_connection.commit()
    except Exception as e:
        print(e)

    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='Albinotroll1324!',
            database='quarm' 
        )
        if connection.is_connected():
            print("Succesffully connected to quarm-db")
        c2 = connection.cursor()
        c2.execute('SELECT id, name, icon FROM items')
        results = c2.fetchall()
        for result in results:
            print(result)
            c1.execute('INSERT INTO items_master (id, name, icon) VALUES (?, ?, ?)', (result[0], result[1], result[2]))
        
    except mysql.connector.Error as e:
        print(f'Error connection to MariaDB: {e}')
        return

def create_tables():
    sql_person_table = """CREATE Table IF NOT EXISTS person (
                        person_name TEXT PRIMARY KEY,
                        relation INTEGER,
                        guild TEXT
    )"""

    sql_character_table = """CREATE Table IF NOT EXISTS character (
                          char_name TEXT PRIMARY KEY,
                          char_class TEXT NOT NULL,
                          person_name text,
                          level INTEGER,
                          FOREIGN KEY (person_name) REFERENCES person(person_name)
    )"""

    sql_raid_master_table = """CREATE Table IF NOT EXISTS raid_master (
                            raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid_name TEXT NOT NULL,
                            raid_date TEXT
    )"""

    sql_person_loot_table = """CREATE Table IF NOT EXISTS person_loot (
                            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            person_name TEXT,
                            item_name TEXT,
                            raid_id INTEGER,
                            FOREIGN KEY (person_name) REFERENCES person(person_name),
                            FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id)
    )"""

    sql_dkp_table = """CREATE Table IF NOT EXISTS dkp (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT,
                    raid_id INTEGER,
                    FOREIGN KEY (person_name) REFERENCES person(person_name),
                    FOREIGN KEY (raid_id) REFERENCES raids_master(raid_id)
    )"""

    sql_raid_ra_table = """CREATE Table IF NOT EXISTS raid_ra (
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        person_name TEXT,
                        raid_id INTEGER,
                        FOREIGN KEY (person_name) REFERENCES person(person_name),
                        FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id)
    )"""

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(sql_person_table)
        c.execute(sql_character_table)
        c.execute(sql_raid_master_table)
        c.execute(sql_person_loot_table)
        c.execute(sql_dkp_table)
        c.execute(sql_raid_ra_table)
        conn.commit()
        print('re-vamped tables created!')
    except Exception as e:
        print('db_migration.create_tables() error:')
        print(e)
        return str(e)
    finally:
        conn.close()

# Next, we need to SELECT ALL from the old tables, and insert into the new tables
def migrate_players_db():
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        query = """INSERT INTO person (person_name, relation, guild)
                SELECT player_name, relation, guild
                FROM Players_db"""
        c.execute(query)
        conn.commit()
        print('Players_db to person migration complete!')
    except Exception as e:
        print('db_migration.migrate_players_db() error:')
        print(e)
        return str(e)
    finally:
        conn.close()

def migrate_characters_db():
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        query = """INSERT INTO character (char_name, char_class, person_name, level)
                SELECT char_name, char_class, player_name, level
                FROM Characters_db"""
        c.execute(query)
        conn.commit()
        print('Characters_db to character migration complete!')
    except Exception as e:
        print('db_migration.migrate_characters_db complete!')
    finally:
        conn.close()
