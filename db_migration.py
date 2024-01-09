import sqlite3
from decouple import config as env
db_path = env('DB_PATH')

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

