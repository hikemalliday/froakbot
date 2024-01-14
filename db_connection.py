import sqlite3

class DatabaseConnection:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
    
    def open(self):
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None