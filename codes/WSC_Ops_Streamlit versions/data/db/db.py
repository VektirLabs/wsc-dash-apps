import sqlite3


def create_Test():
    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('sql.db')
        cursor = sqliteConnection.cursor()
        print('DB Init')

        # Write a query and execute it with cursor
        query = 'select sqlite_version();'
        cursor.execute(query)

        # Fetch and output result
        result = cursor.fetchall()
        print('SQLite Version is {}'.format(result))

        # Close the cursor
        cursor.close()

    # Handle errors
    except sqlite3.Error as error:
        print('Error occured - ', error)

    # Close DB Connection irrespective of success
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')


def create_forecast_db():
    pass


Import libraries
import pandas as pd, csv, sqlite3

# Create sqlite database and cursor
conn = sqlite3.connect('test.db')
c = conn.cursor()
# Create the table of pitches
c.execute("""CREATE TABLE IF NOT EXISTS pitches (
            pitch_type text,
            game_date text,
            release_speed real
            )""")
conn.commit()

test = conn.execute('SELECT * from pitches')
names = [description[0] for description in test.description]
print(names)

df = pd.DataFrame([['SL','8/31/2017','81.9']],columns = ['pitch_type','game_date','release_speed'])
df.to_sql('pitches', conn, if_exists='append', index=False)

conn.execute('SELECT * from pitches').fetchall()
>> [('SL', '8/31/2017', 81.9), ('SL', '8/31/2017', 81.9)]

conn = sqlite3.connect('data/db/forecast.db')
c = conn.cursor()
c = conn.cursor()
# Create the table of pitches
c.execute("""CREATE TABLE IF NOT EXISTS pitches (
            pitch_type text,
            game_date text,
            release_speed real
            )""")
conn.commit()

test = conn.execute('SELECT * from pitches')