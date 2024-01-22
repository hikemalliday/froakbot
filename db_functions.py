import Levenshtein
import mysql.connector
from decouple import config as env
from datetime import datetime
import os
import re
 
# The term 'test' in this module does not imply traditional unit or end to end tests, its for creating test tables that I can read / write

def levenshtein_distance(string1, string2):
    return Levenshtein.distance(string1, string2)

def create_levenshtein_function(bot: object):
    bot.db_connection.create_function("levenshtein", 2, levenshtein_distance)

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
    except Exception as e:
        exception = f'EXCEPTION: db_functions.create_items_master_table(): {str(e)}'
        print(exception)
        return exception
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
        exception = f'EXCEPTION: db_functions.migrate_players_db(): {str(e)}'
        print(exception)
        return exception
# Not a 'test', this migrates the froakbotv1 players table into the current schema table
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
        exception = f'EXCEPTION: db_functions.migrate_players_db(): {str(e)}'
        print(exception)
        return exception   
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
        exception = f'db_functions.migrate_characters_db(): {str(e)}'
        print(exception)
        return exception
# Not a 'test', this migrates the froakbotv1 characters table into the current schema table
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
        exception = f'EXCEPTION: db_functions.migrate_characters_db_test: {str(e)}'
        print(exception)
        return exception

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
                    username TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id),
                    UNIQUE(username, raid_id)
    )"""
    
    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table)
        c.execute(sql_character_table)
        c.execute(sql_raid_master_table)
        c.execute(sql_person_loot_table)
        c.execute(sql_dkp_table)
        bot.db_connection.commit()
        print('Regular tables created.')
    except Exception as e:
        exception = f'EXCEPTION: db_functions.create_tables(): {str(e)}'
        print(exception)
        return exception
    
def create_backup_tables(bot: object):
    sql_person_table_backup = """CREATE Table IF NOT EXISTS person_backup (
                        person_name TEXT PRIMARY KEY,
                        relation INTEGER,
                        guild TEXT,
                        username TEXT UNIQUE
    )"""

    sql_character_table_backup = """CREATE Table IF NOT EXISTS character_backup (
                          char_name TEXT PRIMARY KEY,
                          char_class TEXT NOT NULL,
                          person_name text,
                          level INTEGER,
                          FOREIGN KEY (person_name) REFERENCES person(person_name)
    )"""

    sql_raid_master_table_backup = """CREATE Table IF NOT EXISTS raid_master_backup (
                            raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid_name TEXT NOT NULL,
                            raid_date TEXT
    )"""

    sql_person_loot_table_backup = """CREATE Table IF NOT EXISTS person_loot_backup (
                            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            person_name TEXT,
                            item_name TEXT,
                            raid_id INTEGER,
                            FOREIGN KEY (person_name) REFERENCES person(person_name),
                            FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id)
    )"""

    sql_dkp_table_backup = """CREATE Table IF NOT EXISTS dkp_backup (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    FOREIGN KEY (raid_id) REFERENCES raid_master(raid_id),
                    UNIQUE(username, raid_id)
    )"""

    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table_backup)
        c.execute(sql_character_table_backup)
        c.execute(sql_raid_master_table_backup)
        c.execute(sql_person_loot_table_backup)
        c.execute(sql_dkp_table_backup)
        bot.db_connection.commit()
        print('Backup tables created.')
    except Exception as e:
        exception = f'EXCEPTION: db_functions.create_backup_tables(): {str(e)}'
        print(exception)
        return exception

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
                    username TEXT,
                    raid_id INTEGER,
                    dkp_points INTEGER,
                    FOREIGN KEY (raid_id) REFERENCES raid_master_test(raid_id),
                    UNIQUE(username, raid_id)
    )"""

    try:
        c = bot.db_connection.cursor()
        c.execute(sql_person_table_test)
        c.execute(sql_character_table_test)
        c.execute(sql_raid_master_table_test)
        c.execute(sql_person_loot_table_test)
        c.execute(sql_dkp_table_test)
        bot.db_connection.commit()
        print('Test tables created.')
    except Exception as e:
        exception = f'create_test_tables.create_test_tables() {str(e)}:'
        print(exception)
        return exception

def create_backup_timestamp_table(bot: object):
    sql_backup_timestamp = """CREATE Table IF NOT EXISTS backup_timestamp (
                        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT
    )"""
    
    try:
        c = bot.db_connection.cursor()
        c.execute(sql_backup_timestamp)
        bot.db_connection.commit()
        print('Timestamp table created.')
    except Exception as e:
        exception = f'create_test_tables.create_test_tables() {str(e)}:'
        print(exception)
        return exception
    
def drop_tables(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE person;''')
        c.execute('''DROP TABLE person_loot;''')
        c.execute('''DROP TABLE raid_master;''')
        c.execute('''DROP TABLE character;''')
        c.execute('''DROP TABLE dkp;''')
        bot.db_connection.commit()
        print('Regular tables dropped.')
    except Exception as e:
        exception = f'EXCEPTION db_functions.drop_tables():  {str(e)}'
        print(exception)
        return exception

def drop_backup_tables(bot: object):
    user_input = input("Are you sure you want to drop the backup tables? (y/n): ")
    if user_input.lower() == 'y':
        try:
            c = bot.db_connection.cursor()
            c.execute('''DROP TABLE person_backup;''')
            c.execute('''DROP TABLE person_loot_backup;''')
            c.execute('''DROP TABLE raid_master_backup;''')
            c.execute('''DROP TABLE character_backup;''')
            c.execute('''DROP TABLE dkp_backup;''')
            bot.db_connection.commit()
            print('Backup tables dropped.')
        except Exception as e:
            exception = f'EXCEPTION db_functions.drop_backup_tables():  {str(e)}'
            print(exception)
            return exception
    else:
        print('Backup tables dropped.')
    
def drop_test_tables(bot: object):
    try:
        c = bot.db_connection.cursor()
        c.execute('''DROP TABLE person_test;''')
        c.execute('''DROP TABLE person_loot_test;''')
        c.execute('''DROP TABLE raid_master_test;''')
        c.execute('''DROP TABLE character_test;''')
        c.execute('''DROP TABLE dkp_test;''')
        bot.db_connection.commit()
        print('Test tables dropped.')   
    except Exception as e:
        exception = f'EXCEPTION db_functions.drop_test_tables(): {str(e)}'
        print(exception)
        return exception

def reset_tables(bot: object):
    user_input = input("Are you sure you want to reset the tables? (y/n): ")
    if user_input.lower() == 'y':
        try:
            drop_tables(bot)
            create_tables(bot)
            migrate_players_db(bot)
            migrate_characters_db(bot)
        except Exception as e:
            exception  = f'db_functions.reset_tables(): {str(e)}'
            print(exception)
            return exception
    else:
        print("Table reset cancelled.")

def reset_test_tables(bot: object):
    user_input = input("Are you sure you want to reset the test tables? (y/n): ")
    if user_input.lower() == 'y':
        try:
            drop_test_tables(bot)
            create_test_tables(bot)
            migrate_players_db_test(bot)
            migrate_characters_db_test(bot)
            add_mock_rows_raid_master_test(bot)
            add_mock_rows_dkp_test(bot)
            mock_usernames_test(bot)
        except Exception as e:
            exception  = f'db_functions.reset_test_tables(): {str(e)}'
            print(exception)
            return exception    
    else:
        print("Test table reset cancelled.")

# Returns Boolean so that caller can decide to proceed with other calls
def copy_paste_backup_database(bot: object) -> bool:
    try:
        max_num = 0
        dir = './froak-db/'

        for filename in os.listdir(dir):
            if filename.startswith('master') and filename.endswith('.db'):
                match = re.search(r'\d+', filename)
                if match:
                    num = int(match.group())
                    max_num = max(max_num, num)
        
        new_num = max_num + 1
        new_filename = f'master{new_num}.db'
        original_file = os.path.join(dir, 'master.db')
        new_file = os.path.join(dir, new_filename)

        with open(original_file, 'rb') as f_read:
            with open(new_file, 'wb') as f_write:
                f_write.write(f_read.read())
        
        print(f'Backup db file created: {new_filename}')
        return True
    except Exception as e:
        print(f'EXCEPTION: db_functions.copy_paste_backup_database(): {str(e)}')
        return False

def backup_database(bot: object):
    try:
        # Cannot include DROP and CREATE calls in a transaction, so we need to FIRST create the backup DB file before attempting to call this function.
        # That way, we have a safeguard in place.
        success = copy_paste_backup_database(bot)
        if success == False:
            print(f'db_functions.copy_paste_backup_database returned False, too risky to proceed. Aborting backup.')
            return
        
        drop_backup_tables(bot)
        create_backup_tables(bot)
        
        conn = bot.db_connection
        with conn:
            c = conn.cursor()
            # Cannot wrap these in a commit
            c.execute('''SELECT * FROM person''')
            results = c.fetchall()
            if results:
                c.executemany('''INSERT INTO person_backup VALUES (?, ?, ?, ?)''', results)
            else:
                print(f'SELECT * FROM person failed, please revert to backup DB file and try again.')
            c.execute('''SELECT * FROM character''')
            results = c.fetchall()
            if results:
                c.executemany('''INSERT INTO character_backup VALUES (?, ?, ?, ?)''', results)
            else:
                print(f'SELECT * FROM character failed, please revert to backup DB file and try again.')
            c.execute('''SELECT username, raid_id, dkp_points FROM dkp''')
            results = c.fetchall()
            if results:
                c.executemany('''INSERT INTO dkp_backup (username, raid_id, dkp_points) VALUES (?, ?, ?)''', results)
            c.execute('''SELECT person_name, item_name, raid_id  FROM person_loot''') 
            results = c.fetchall()
            if results:
                c.executemany('''INSERT INTO person_loot_backup (person_name, item_name, raid_id) VALUES (?, ?, ?)''', results)
            c.execute('''SELECT raid_name, raid_date FROM raid_master''')
            results = c.fetchall()
            if results:
                c.executemany('''INSERT INTO raid_master_backup VALUES (?, ?)''', results)
            c.execute('''INSERT INTO backup_timestamp (date) VALUES (?)''', (datetime.now().strftime("%m-%d-%Y"),) )
            conn.commit()
        print('Database backup complete.')
    except Exception as e:
        exception = f'EXCEPTION: db_functions.backup_database(): {str(e)}'
        print(exception)
        return exception

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
        conn.commit()
        print('add_mock_rows_raid_master_test() success.')
    except Exception as e:
        print('add_mock_rows_raid_master_test() error:' , str(e))
        return e

def add_mock_rows_dkp_test(bot: object):
    try:
      mock_rows = [
          ('therealdodger', 1, 1),
          ('norrix455', 1, 1),
          ('nocsucow', 1, 1),
          ('deimos888', 1, 1),
          ('bodied3', 1, 1),
          ('afflictx', 1, 1),
          ('therealdodger', 2, 1),
          ('norrix455', 2, 1),
          ('nocsucow', 2, 1),
          ('deimos888', 2, 1),
          ('bodied3', 2, 1),
          ('afflictx', 2, 1),
          ('therealdodger', 3, 1),
          ('norrix455', 3, 1),
          ('nocsucow', 3, 1),
          ('deimos888', 3, 1),
          ('bodied3', 3, 1),
          ('afflictx', 3, 1),
          ('therealdodger', 4, 1),
          ('norrix455', 4, 1),
          ('nocsucow', 4, 1),
          ('deimos888', 4, 1),
          ('bodied3', 4, 1),
          ('afflictx', 4, 1),
          ('therealdodger', 5, 1),
          ('norrix455', 5, 1),
          ('nocsucow', 5, 1),
          ('deimos888', 5, 1),
          ('bodied3', 5, 1),
          ('afflictx', 5, 1),
          ('therealdodger', 6, 1),
          ('norrix455', 6, 1),
          ('nocsucow', 6, 1),
          ('deimos888', 6, 1),
          ('bodied3', 6, 1),
          ('afflictx', 6, 1),
          ('therealdodger', 7, 1),
          ('norrix455', 7, 1),
          ('nocsucow', 7, 1),
          ('deimos888', 7, 1),
          ('bodied3', 7, 1),
          ('afflictx', 7, 1),
          ('therealdodger', 8, 1),
          ('norrix455', 8, 1),
          ('nocsucow', 8, 1),
          ('deimos888', 8, 1),
          ('bodied3', 8, 1),
          ('afflictx', 8, 1),
          ('therealdodger', 9, 1),
          ('norrix455', 9, 1),
          ('nocsucow', 9, 1),
          ('deimos888', 9, 1),
          ('bodied3', 9, 1),
          ('afflictx', 9, 1),
          ('therealdodger', 10, 1),
          ('norrix455', 10, 1),
          ('nocsucow', 10, 1),
          ('deimos888', 10, 1),
          ('bodied3', 10, 1),
          ('afflictx', 10, 1),
          ('therealdodger', 11, 1),
          ('norrix455', 11, 1),
          ('nocsucow', 11, 1),
          ('deimos888', 11, 1),
          ('bodied3', 11, 1),
          ('afflictx', 11, 1),
          ('therealdodger', 12, 1),
          ('norrix455', 12, 1),
          ('nocsucow', 12, 1),
          ('deimos888', 12, 1),
          ('bodied3', 12, 1),
          ('afflictx', 12, 1),
      ]
      conn = bot.db_connection
      c = conn.cursor()
      c.executemany('''INSERT INTO dkp_test (username, raid_id, dkp_points) VALUES (?, ?, ?)''', (mock_rows))
      conn.commit()
      print('add_mock_rows_dkp_test() success.')
    except Exception as e:
        exception = f'EXCEPTION: db_functions.add_mock_rows_dkp_test(): {str(e)}'
        print(exception)
        return exception

def mock_usernames_test(bot: object):
    try:
        mock_usernames = [
            ('afflictx','Afflictx'),
            ('norrix455','Norrix'),
            ('bodied3','Bodied'),
            ('deimos888','Deimos'),
            ('nocsucow','Nocsucow'),
            ('therealdodger','Dodger'),
            ('grixus.', 'Grixus')
        ]
        conn = bot.db_connection
        c = conn.cursor()
        for username, person_name in mock_usernames:
            c.execute('UPDATE person_test SET username = ? WHERE person_name = ?', (username, person_name))
        conn.commit()
        print(f'db_functions.mock_register_usernames() success.')
    except Exception as e:
        exception = f'EXCEPTION: db_functions.mock_register_usernames: {str(e)}'
        print(exception)
        return exception