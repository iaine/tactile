'''
   Data Access file

   Assumption is that the bash start file will initialise the database
'''
import sqlite3

class DAO():

    def __init__(self):
        conn = sqlite3.connect('tactile.db')
        self.db = conn.cursor()

    def check_table_exists(self, table_name):
        '''
          Query to check that the table exists. If not create it.
          @parameter: table_name - the table name for query
        '''
        self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if self.db.fetchone() is None:
            if table_name == 'sounds':
                self.db.execute(''' CREATE TABLE sounds
                                (picture text, soundfile text, xpos real, ypos real)''')

    def fetch(self, x, y):
        '''
          Fetch the sound file linked to the tile number
          @parameter tile, integer for the tile number
        '''

        try:
            self.db.execute('SELECT soundfile FROM sounds WHERE xpos=? and ypos=?', (x,y,))
            return self.db.fetchone()[0]
        except Exception,e:
            print (e)

    def insert_data(self, picture, audio, x, y):
        '''
          Method to insert data
        '''
        try:
            print("picture: " + picture + " audio: " + audio + "x: " + str(x) + " y: " + str(y))
            conn = sqlite3.connect('tactile.db')
            db = conn.cursor()

            db.execute("INSERT INTO sounds (picture, soundfile, xpos, ypos) VALUES (?,?,?,?)", (picture, audio, x, y,))
            conn.commit()
        except Exception, e:
            print e
