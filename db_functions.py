import Levenshtein
import mysql.connector
from decouple import config as env
from datetime import datetime
 
# The term 'test' in this module does not imply traditional unit or end to end tests, its for creating test tables that I can read / write


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

# Created from the Project Quarm items database.
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
# Used to migrate the old tables into the new schema:
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

def migrate_players_db_test(bot: object):
    try:
        c = bot.db_connection.cursor()
        query = """INSERT INTO person_test (person_name, relation, guild)
                SELECT player_name, relation, guild
                FROM Players_db"""
        c.execute(query)
        bot.db_connection.commit()
        print('Players_db to person migration complete!')
    except Exception as e:
        print('db_migration.migrate_players_db() error:')
        print(e)
        return str(e)
    
# Used to migrate the old tables into the new schema:
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
        print('migrate_characters_db error: ', str(e))

def migrate_characters_db_test(bot: object):
    try:
        c = bot.db_connection.cursor()
        query = """INSERT INTO character_test (char_name, char_class, person_name, level)
                SELECT char_name, char_class, player_name, level
                FROM Characters_db"""
        c.execute(query)
        bot.db_connection.commit()
        print('Characters_db to character_test migration complete!')
    except Exception as e:
        print('migrate_characters_db_test error', str(e))

def create_tables(bot: object):
    sql_person_table = """CREATE Table IF NOT EXISTS person (
                        person_name TEXT PRIMARY KEY,
                        relation INTEGER,
                        guild TEXT,
                        username TEXT UNIQUE
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
                    FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id),
                    UNIQUE(person_name, raid_id)
    )"""

    sql_raid_master_table_backup = """CREATE Table IF NOT EXISTS raid_master_backup (
                            raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid_name TEXT NOT NULL,
                            raid_date TEXT
    )"""

    sql_dkp_table_backup = """CREATE Table IF NOT EXISTS dkp_backup (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    UNIQUE(person_name, raid_id)
    )"""

    sql_person_loot_table_backup = """CREATE Table IF NOT EXISTS person_loot_backup (
                            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            person_name TEXT,
                            item_name TEXT,
                            raid_id INTEGER
                            
    )"""

    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table)
        c.execute(sql_character_table)
        c.execute(sql_raid_master_table)
        c.execute(sql_person_loot_table)
        c.execute(sql_dkp_table)
        c.execute(sql_raid_master_table_backup)
        c.execute(sql_dkp_table_backup)
        c.execute(sql_person_loot_table_backup)
        bot.db_connection.commit()
        print('re-vamped tables created!')
    except Exception as e:
        print('db_migration.create_tables() error:')
        print(e)
        return str(e)

def create_test_tables(bot: object):
    sql_person_table_test = """CREATE Table IF NOT EXISTS person_test (
                        person_name TEXT PRIMARY KEY,
                        relation INTEGER,
                        guild TEXT,
                        username TEXT UNIQUE
    )"""

    sql_character_table_test = """CREATE Table IF NOT EXISTS character_test (
                          char_name TEXT PRIMARY KEY,
                          char_class TEXT NOT NULL,
                          person_name text,
                          level INTEGER,
                          FOREIGN KEY (person_name) REFERENCES person_test(person_name)
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
                            FOREIGN KEY (person_name) REFERENCES person_test(person_name),
                            FOREIGN KEY (raid_id) REFERENCES raid_master_test(raid_id)
    )"""

    sql_dkp_table_test = """CREATE Table IF NOT EXISTS dkp_test (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    FOREIGN KEY (person_name) REFERENCES person_test(person_name),
                    FOREIGN KEY (raid_id) REFERENCES raid_master_test(raid_id),
                    UNIQUE(person_name, raid_id)
    )"""

    sql_raid_master_table_test_backup = """CREATE Table IF NOT EXISTS raid_master_test_backup (
                            raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid_name TEXT NOT NULL,
                            raid_date TEXT
    )"""

    sql_dkp_table_test_backup = """CREATE Table IF NOT EXISTS dkp_test_backup (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_name TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    UNIQUE(person_name, raid_id)
    )"""

    sql_person_loot_table_test_backup = """CREATE Table IF NOT EXISTS person_loot_test_backup (
                            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            person_name TEXT,
                            item_name TEXT,
                            raid_id INTEGER
                            
    )"""

    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table_test)
        c.execute(sql_character_table_test)
        c.execute(sql_raid_master_table_test)
        c.execute(sql_person_loot_table_test)
        c.execute(sql_dkp_table_test)
        c.execute(sql_raid_master_table_test_backup)
        c.execute(sql_dkp_table_test_backup)
        c.execute(sql_person_loot_table_test_backup)
        
        bot.db_connection.commit()
        print('Test tables created!')
    except Exception as e:
        print('db_migration.create_test_tables() error:')
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
        c.execute('''DROP TABLE dkp_backup;''')
        c.execute('''DROP TABLE raid_master_backup;''')
        c.execute('''DROP TABLE person_loot_backup;''')
        bot.db_connection.commit()
        print('TABLES DROPPED')
        
    except Exception as e:
        print('drop_tables() error: ', str(e))
        return str(e)
    
def drop_test_tables(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE person_test;''')
        c.execute('''DROP TABLE person_loot_test;''')
        c.execute('''DROP TABLE raid_master_test;''')
        c.execute('''DROP TABLE character_test;''')
        c.execute('''DROP TABLE dkp_test;''')
        c.execute('''DROP TABLE dkp_test_backup;''')
        c.execute('''DROP TABLE raid_master_test_backup;''')
        c.execute('''DROP TABLE person_loot_test_backup;''')
        bot.db_connection.commit()
        print('Test tables dropped.')   
    except Exception as e:
        print('drop_test_tables() error, couldnt drop tables: ', str(e))
        return str(e)

def reset_tables(bot: object):
    try:
        drop_tables(bot)
        create_tables(bot)
        migrate_players_db(bot)
        migrate_characters_db(bot)
    except Exception as e:
        print(e)
        return str(e)

def reset_test_tables(bot: object):
    try:
        drop_test_tables(bot)
        create_test_tables(bot)
        migrate_players_db_test(bot)
        migrate_characters_db_test(bot)
        add_mock_rows_raid_master_test(bot)
        add_mock_rows_dkp_test(bot)
    except Exception as e:
        print('Couldnt reset test tables: ', str(e))
        return

def reset_backup_tables(bot: object):
    pass

def add_mock_rows_raid_master_test(bot: object):
    try:
        date_time = datetime.now().strftime("%m-%d-%Y")
        mock_rows = [
            ("Veeshan's Peak", date_time),
            ("Golems",  date_time),
            ("Plane of Hate", date_time),
            ("Plane of Sky", date_time),
            ("Halls of Testing", date_time),
            ("Klandicar", date_time),
            ("Royals", date_time),
            ("Veeshan's Peak", date_time),
            ("Dracholiche", date_time),
            ("Golems + Dracho", date_time),
            ("Halls of Testing", date_time),
                     ]
        conn = bot.db_connection
        c = conn.cursor()
        c.executemany('''INSERT INTO raid_master_test (raid_name, raid_date) VALUES (?, ?)''', (mock_rows))
        c.executemany('''INSERT INTO raid_master_test_backup (raid_name, raid_date) VALUES (?, ?)''', (mock_rows))
        conn.commit()
        print('add_mock_rows_raid_master_test() success.')
    except Exception as e:
        print('add_mock_rows_raid_master_test() error:' , str(e))
        return e

def add_mock_rows_dkp_test(bot: object):
    try:
      mock_rows = [
          ('Sharknado', 1, 1),
          ('Threepeat', 1, 1),
          ('Choopa', 1, 1),
          ('Slarti', 1, 1),
          ('Filpox', 1, 1),
          ('Norrix', 1, 1),
          ('Tune', 1, 1),
          ('Bodied', 1, 1),
          ('Kilbur', 1, 1),
          ('Ivah', 1, 1),
          ('Grixus', 1, 1),
          ('Sharknado', 2, 1),
          ('Threepeat', 2, 1),
          ('Choopa', 2, 1),
          ('Slarti', 2, 1),
          ('Filpox', 2, 1),
          ('Norrix', 2, 1),
          ('Tune', 2, 1),
          ('Bodied', 2, 1),
          ('Kilbur', 2, 1),
          ('Ivah', 2, 1),
          ('Grixus', 2, 1),
          ('Sharknado', 3, 1),
          ('Threepeat', 3, 1),
          ('Choopa', 3, 1),
          ('Slarti', 3, 1),
          ('Filpox', 3, 1),
          ('Norrix', 3, 1),
          ('Tune', 3, 1),
          ('Bodied', 3, 1),
          ('Kilbur', 3, 1),
          ('Ivah', 3, 1),
          ('Grixus', 3, 1),
          ('Sharknado', 4, 1),
          ('Threepeat', 4, 1),
          ('Choopa', 4, 1),
          ('Slarti', 4, 1),
          ('Filpox', 4, 1),
          ('Norrix', 4, 1),
          ('Tune', 4, 1),
          ('Bodied', 4, 1),
          ('Kilbur', 4, 1),
          ('Ivah', 4, 1),
          ('Grixus', 4, 1),
          ('Sharknado', 5, 1),
          ('Threepeat', 5, 1),
          ('Choopa', 5, 1),
          ('Slarti', 5, 1),
          ('Filpox', 5, 1),
          ('Norrix', 5, 1),
          ('Tune', 5, 1),
          ('Bodied', 5, 1),
          ('Kilbur', 5, 1),
          ('Ivah', 5, 1),
          ('Grixus', 5, 1),
          ('Sharknado', 6, 1),
          ('Threepeat',6, 1),
          ('Choopa', 6, 1),
          ('Slarti', 6, 1),
          ('Filpox', 6, 1),
          ('Norrix', 6, 1),
          ('Tune', 6, 1),
          ('Bodied', 6, 1),
          ('Kilbur', 6, 1),
          ('Ivah', 6, 1),
          ('Grixus', 6, 1),
          ('Sharknado', 7, 1),
          ('Threepeat', 7, 1),
          ('Choopa', 7, 1),
          ('Slarti', 7, 1),
          ('Filpox', 7, 1),
          ('Norrix', 7, 1),
          ('Tune', 7, 1),
          ('Bodied', 7, 1),
          ('Kilbur', 7, 1),
          ('Ivah', 7, 1),
          ('Grixus', 7, 1),
          ('Sharknado', 8, 1),
          ('Threepeat', 8, 1),
          ('Choopa', 8, 1),
          ('Slarti', 8, 1),
          ('Filpox', 8, 1),
          ('Norrix', 8, 1),
          ('Tune', 8, 1),
          ('Bodied', 8, 1),
          ('Kilbur', 8, 1),
          ('Ivah', 8, 1),
          ('Grixus', 8, 1),
          ('Sharknado', 9, 1),
          ('Threepeat', 9, 1),
          ('Choopa', 9, 1),
          ('Slarti', 9, 1),
          ('Filpox', 9, 1),
          ('Norrix', 9, 1),
          ('Tune', 9, 1),
          ('Bodied', 9, 1),
          ('Kilbur', 9, 1),
          ('Ivah', 9, 1),
          ('Grixus', 9, 1),
          ('Sharknado', 10, 1),
          ('Threepeat', 10, 1),
          ('Choopa', 10, 1),
          ('Slarti', 10, 1),
          ('Filpox', 10, 1),
          ('Norrix', 10, 1),
          ('Tune', 10, 1),
          ('Bodied', 10, 1),
          ('Kilbur', 10, 1),
          ('Ivah', 10, 1),
          ('Grixus', 10, 1),
          ('Sharknado', 11, 1),
          ('Threepeat', 11, 1),
          ('Choopa', 11, 1),
          ('Slarti', 11, 1),
          ('Filpox', 11, 1),
          ('Norrix', 11, 1),
          ('Tune', 11, 1),
          ('Bodied', 11, 1),
          ('Kilbur', 11, 1),
          ('Ivah', 11, 1),
          ('Grixus', 11, 1)
      ]
      conn = bot.db_connection
      c = conn.cursor()
      c.executemany('''INSERT INTO dkp_test (person_name, raid_id, dkp_points) VALUES (?, ?, ?)''', (mock_rows))
      c.executemany('''INSERT INTO dkp_test_backup (person_name, raid_id, dkp_points) VALUES (?, ?, ?)''', (mock_rows))
      conn.commit()
      print('add_mock_rows_dkp_test() success.')
    except Exception as e:
        print('add_mock_rows_dkp_test() error: ', str(e))
        return str(e)


