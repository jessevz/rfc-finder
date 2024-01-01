import sqlite3
import os

class SimpleSQLiteDB:
    db_file = os.path.expanduser("~") + "/.rfc-finder/rfc.db"

    def __init__(self):
        self.db_file = self.db_file
        self.connection = sqlite3.connect(self.db_file)

    def create_tables(self):
        self.create_rfc_table()
        self.create_author_table()
        self.create_author_rfc_table()
        self.create_config_table()

    def create_rfc_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS RFC (
                RFC_number INTEGER PRIMARY KEY,
                RFC_title TEXT NOT NULL
            )
        '''

        self.connection.execute(query)
        self.connection.commit()

    def create_author_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS Author (
                        author_id INTEGER PRIMARY KEY,
                        author_name TEXT NOT NULL UNIQUE
                    )
        '''

        self.connection.execute(query)
        self.connection.commit()

    def create_author_rfc_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS AuthorRFC (
                        author_id INTEGER,
                        RFC_number INTEGER,
                        FOREIGN KEY (author_id) REFERENCES Author (author_id),
                        FOREIGN KEY (RFC_number) REFERENCES RFC (RFC_number),
                        PRIMARY KEY (author_id, RFC_number)
                    )
        '''

        self.connection.execute(query)
        self.connection.commit()

    def create_config_table(self):
        query = '''
            CREATE TABLE IF NOT EXISTS Config (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
        '''

        self.connection.execute(query)
        self.connection.commit()

    def insert_config_value(self, key, value):
        cursor = self.connection.cursor()

        cursor.execute("INSERT OR REPLACE INTO Config (key, value) VALUES (?, ?)",
                       (key, value))
        self.connection.commit()

    def get_config_value(self, key):
        cursor = self.connection.cursor()
        cursor.execute("SELECT value from Config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_latest_RFC_number(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT MAX(rfc_number) FROM rfc")
        result = cursor.fetchone()
        assert result is not None, "There should be a highest RFC in the database"

        return result[0]


    def insert_RFC(self, rfc):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO RFC (RFC_number, RFC_title) VALUES (?,?)",
                                (rfc.rfc_number, rfc.title))
        self.connection.commit()

        for author in rfc.authors:
            author_result = self.retrieve_author_id(author)

            if author_result is None:
                cursor.execute("INSERT INTO Author (author_name) VALUES (?)", (author,))
                self.connection.commit()
                author_id = cursor.lastrowid
            else:
                author_id = author_result
           
            try:
                cursor.execute("INSERT INTO AuthorRFC (author_id, RFC_number) VALUES (?, ?)",
                           (author_id, rfc.rfc_number))
                self.connection.commit()
            except sqlite3.IntegrityError as e:
                pass

    def retrieve_author_id(self, name):
        cursor = self.connection.cursor()
        cursor.execute("select author_id from Author where author_name = ?", (name,))
        result = cursor.fetchone()
        
        if result is None:
            return None
        return result[0]

    def search_by_author(self, name):
        author_id = self.retrieve_author_id(name)
        if author_id is None:
            return None

        cursor = self.connection.cursor()
        RFCs = []
        for row in cursor.execute("select * from AuthorRFC where author_id = ?", (author_id,)):
            rfc_number = row[1]
            RFCs.append(self.retrieve_rfc(rfc_number))
        return RFCs

    def retrieve_rfc(self, rfc_number):
        cursor = self.connection.cursor()
        cursor.execute("select * from RFC where RFC_number = ?", (rfc_number,))
        return cursor.fetchone()

    def retrieve_rfcs(self):
        query = 'SELECT * FROM RFC'
        cursor = self.connection.execute(query)
        return cursor.fetchall()

    def search_by_title(self, title):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * from RFC where RFC_title LIKE ?", ("%" + title + "%",))
        return cursor.fetchall()

    def close_connection(self):
        self.connection.close()
