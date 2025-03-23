import sqlite3

class Database(object):
    _instance = None
    
    def __init__(self, db_name='database/bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    
    def __new__(cls):
        if cls._instance is None:
            # Create the instance if it doesn't exist
            cls._instance = super(Database, cls).__new__(cls)
            # Call initialization logic only for the first instance
            cls._instance._initialize()

        return cls._instance
    
    def _initialize(self, db_name='database/bot.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        

    def create_tables(self):
        # Create the 'user' table if it doesn't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        )
        ''')

        # Create the 'message' table if it doesn't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY,
            sender INTEGER,
            receiver INTEGER,
            content TEXT NOT NULL,
            time DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender) REFERENCES user (id),
            FOREIGN KEY (receiver) REFERENCES user (id)
        )
        ''')

        self.conn.commit()

    # User-related methods
    def add_user(self, username):
        """Add a user to the database."""
        self.cursor.execute('''
        INSERT INTO user (username) VALUES (?)
        ''', (username,))
        self.conn.commit()

    def delete_user(self, user_id):
        """Delete a user by their ID."""
        self.cursor.execute('''
        DELETE FROM user WHERE id = ?
        ''', (user_id,))
        self.conn.commit()

    def find_user_by_id(self, user_id):
        """Find a user by their ID."""
        self.cursor.execute('''
        SELECT * FROM user WHERE id = ?
        ''', (user_id,))
        return self.cursor.fetchone()  # Returns a single user or None
    
    def find_user_by_name(self, username):
        """Find a user by their ID."""
        self.cursor.execute('''
        SELECT * FROM user WHERE username = ?
        ''', (username,))
        return self.cursor.fetchone()  # Returns a single user or None

    # Message-related methods
    def add_message(self, id, sender_id, receiver_id, content):
        """Add a message to the database."""
        self.cursor.execute('''
        INSERT INTO message (id, sender, receiver, content) VALUES (?, ?, ?, ?)
        ''', (id, sender_id, receiver_id, content))
        self.conn.commit()

    def delete_message(self, message_id):
        """Delete a message by its ID."""
        self.cursor.execute('''
        DELETE FROM message WHERE id = ?
        ''', (message_id,))
        self.conn.commit()

    def find_message_by_id(self, message_id):
        """Find a message by its ID."""
        self.cursor.execute('''
        SELECT * FROM message WHERE id = ?
        ''', (message_id,))
        return self.cursor.fetchone()  # Returns a single message or None

    def get_sender_id_by_message_id(self, message_id):
        """Get the sender of a message by its ID."""
        self.cursor.execute('''
        SELECT sender FROM message WHERE id = ?
        ''', (message_id,))
        result = self.cursor.fetchone()  # Returns the sender ID or None
        if result:
            return result[0]
        
        return None
    
    def get_receiver_id_by_message_id(self, message_id):
        """Get the receiver of a message by its ID."""
        self.cursor.execute('''
        SELECT receiver FROM message WHERE id = ?
        ''', (message_id,))
        result = self.cursor.fetchone()  # Returns the sender ID or None
        if result:
            print(f'result{result}')
            return result[0]
    
        return None

    def close(self):
        """Close the database connection."""
        self.conn.close()

