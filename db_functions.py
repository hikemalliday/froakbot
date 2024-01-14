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

# Created from the Proect Quarm items database.
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
            password='-',
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
# Used to migrate the old tables into the new schema (descrated):
def migrate_players_db(bot: object):
    try:
        c = bot.db_connection.cursor()
        query = """INSERT INTO person (person_name, relation, guild)
                SELECT player_name, relation, guild
                FROM Players_db"""
        c.execute(query)
        bot.db_connection.commit()
        print('Players_db to person migration complete!')
    except Exception as e:
        print('db_migration.migrate_players_db() error:')
        print(e)
        return str(e)
    
# Used to migrate the old tables into the new schema (desecrated):
def migrate_characters_db(bot: object):
    try:
        c = bot.db_connection.cursor()
        query = """INSERT INTO character (char_name, char_class, person_name, level)
                SELECT char_name, char_class, player_name, level
                FROM Characters_db"""
        c.execute(query)
        bot.db_connection.commit()
        print('Characters_db to character migration complete!')
    except Exception as e:
        print('db_migration.migrate_characters_db complete!')

def create_tables(bot: object):
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
        c = bot.db_connection.cursor()
        c.execute(sql_person_table)
        c.execute(sql_character_table)
        c.execute(sql_raid_master_table)
        c.execute(sql_person_loot_table)
        c.execute(sql_dkp_table)
        c.execute(sql_raid_ra_table)
        bot.db_connection.commit()
        print('re-vamped tables created!')
    except Exception as e:
        print('db_migration.create_tables() error:')
        print(e)
        return str(e)

def drop_tables(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE person;''')
        c.execute('''DROP TABLE person_loot;''')
        c.execute('''DROP TABLE raid_master;''')
        c.execute('''DROP TABLE character;''')
        c.execute('''DROP TABLE dkp;''')
        c.execute('''DROP TABLE raid_ra;''')
        bot.db_connection.commit()
        print('TABLES DROPPED')
        
    except Exception as e:
        print('reset_tables() error: ', str(e))
        return str(e)
    
def create_test_tables(bot: object):
    sql_person_table_test = """CREATE Table IF NOT EXISTS person_test (
                        person_name TEXT PRIMARY KEY,
                        relation INTEGER,
                        guild TEXT
    )"""

    sql_character_table_test = """CREATE Table IF NOT EXISTS character_test (
                          char_name TEXT PRIMARY KEY,
                          char_class TEXT NOT NULL,
                          person_name text,
                          level INTEGER,
                          FOREIGN KEY (person_name) REFERENCES person(person_name)
    )"""

    sql_raid_master_table_test = """CREATE Table IF NOT EXISTS raid_master_test (
                            raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid_name TEXT NOT NULL,
                            raid_date TEXT
    )"""

    sql_person_loot_table_test = """CREATE Table IF NOT EXISTS person_loot_test (
                            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            person_name TEXT,
                            item_name TEXT,
                            raid_id INTEGER,
                            FOREIGN KEY (person_name) REFERENCES person(person_name),
                            FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id)
    )"""

    sql_dkp_table_test = """CREATE Table IF NOT EXISTS dkp_test (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    FOREIGN KEY (person_name) REFERENCES person(person_name),
                    FOREIGN KEY (raid_id) REFERENCES raids_master(raid_id)
    )"""

    sql_raid_ra_table_test = """CREATE Table IF NOT EXISTS raid_ra_test (
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        person_name TEXT,
                        raid_id INTEGER,
                        FOREIGN KEY (person_name) REFERENCES person(person_name),
                        FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id)
    )"""

    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table_test)
        c.execute(sql_character_table_test)
        c.execute(sql_raid_master_table_test)
        c.execute(sql_person_loot_table_test)
        c.execute(sql_dkp_table_test)
        c.execute(sql_raid_ra_table_test)
        bot.db_connection.commit()
        print('Test tables created!')
    except Exception as e:
        print('db_migration.create_tables() error:')
        print(e)
        return str(e)

def drop_test_tables(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE person_test;''')
        c.execute('''DROP TABLE person_loot_test;''')
        c.execute('''DROP TABLE raid_master_test;''')
        c.execute('''DROP TABLE character_test;''')
        c.execute('''DROP TABLE dkp_test;''')
        c.execute('''DROP TABLE raid_ra_test;''')
        bot.db_connection.commit()
        print('Test tables dropped.')   
    except Exception as e:
        print('reset_tables() error, couldnt drop tables: ', str(e))
        return str(e)

def reset_test_tables(bot: object):
    try:
        drop_test_tables(bot)
        create_test_tables(bot)
    except Exception as e:
        print('Couldnt reset test tables: ', str(e))
        return
    

