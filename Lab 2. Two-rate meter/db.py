import sqlite3

class Database:
    def __init__(self, db_name="meter.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        # Таблиця з останніми показниками
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS meters (
                    id TEXT PRIMARY KEY,
                    last_day INTEGER,
                    last_night INTEGER,
                    last_date TEXT
                )''')

        # Таблиця з історією розрахунків
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meter_id TEXT,
                    date TEXT,
                    day INTEGER,
                    night INTEGER,
                    used_day INTEGER,
                    used_night INTEGER,
                    bill REAL
                )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tariffs (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    day_rate REAL,
                    night_rate REAL,
                    fake_day INTEGER,
                    fake_night INTEGER
                )''')

        self.cursor.execute('SELECT COUNT(*) FROM tariffs')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO tariffs (id, day_rate, night_rate, fake_day, fake_night)
                VALUES (1, 4.32, 2.16, 100, 80)
            ''')

        self.conn.commit()

    def update_tariffs(self, day_rate, night_rate, fake_day, fake_night):
        self.cursor.execute('''
            UPDATE tariffs SET day_rate = ?, night_rate = ?, fake_day = ?, fake_night = ? WHERE id = 1
        ''', (day_rate, night_rate, fake_day, fake_night))
        self.conn.commit()

    def get_tariffs(self):
        self.cursor.execute('SELECT day_rate, night_rate, fake_day, fake_night FROM tariffs WHERE id = 1')
        return self.cursor.fetchone()

    def save_meter(self, meter_id, corrected_day, corrected_night, date):
        self.cursor.execute("SELECT COUNT(*) FROM meters WHERE id = ?", (meter_id,))
        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute('''UPDATE meters
                                   SET last_day = ?, last_night = ?, last_date = ?
                                   WHERE id = ?''',
                                (corrected_day, corrected_night, date, meter_id))
        else:
            self.cursor.execute('''INSERT INTO meters (id, last_day, last_night, last_date)
                                   VALUES (?, ?, ?, ?)''',
                                (meter_id, corrected_day, corrected_night, date))

        self.conn.commit()

    def get_meter(self, meter_id):
        self.cursor.execute("SELECT * FROM meters WHERE id = ?", (meter_id,))
        return self.cursor.fetchone()

    def get_last_meter_id(self):
        self.cursor.execute("SELECT MAX(id) FROM meters")
        result = self.cursor.fetchone()
        if result and result[0] is not None:
            return result[0]
        return None

    def add_history(self, meter_id, date, day_tariff, night_tariff, used_day, used_night, bill):
        self.cursor.execute('''INSERT INTO history (meter_id, date, day, night, used_day, used_night, bill)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (meter_id, date, day_tariff, night_tariff, used_day, used_night, bill))
        self.conn.commit()

    def get_history(self):
        self.cursor.execute("SELECT * FROM history ORDER BY date DESC")
        return self.cursor.fetchall()