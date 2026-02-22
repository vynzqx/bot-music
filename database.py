import sqlite3

def setup_database():
    """Creates the database file and table if they don't exist."""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id TEXT,
            track_name TEXT,
            artist_name TEXT,
            spotify_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_song_to_db(user_id, track_name, artist_name, spotify_url):
    """Inserts a new song into the database."""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO favorites (user_id, track_name, artist_name, spotify_url) VALUES (?, ?, ?, ?)",
        (str(user_id), track_name, artist_name, spotify_url)
    )
    conn.commit()
    conn.close()

def get_user_playlist(user_id):
    """Fetches all saved songs for a specific user."""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT track_name, artist_name, spotify_url FROM favorites WHERE user_id = ?", (str(user_id),))
    rows = cursor.fetchall()
    conn.close()
    return rows