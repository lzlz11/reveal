from dotenv import load_dotenv, dotenv_values
import psycopg2
import os

load_dotenv()
connection = psycopg2.connect(host=os.getenv("DB_HOST"),
                              dbname=os.getenv("DB_NAME"),
                              user=os.getenv("DB_USER"),
                              password=os.getenv("DB_PASSWORD"),
                              port=os.getenv("DB_PORT"))


cursor = connection.cursor()
# ======================
# USERS
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY
);
""")

cursor.execute("""
ALTER TABLE users
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS password_hash TEXT,
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS profile_picture_path TEXT;
""")

# ======================
# POSTS
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
""")

cursor.execute("""
ALTER TABLE posts
ADD COLUMN IF NOT EXISTS caption TEXT,
ADD COLUMN IF NOT EXISTS media_path TEXT,
ADD COLUMN IF NOT EXISTS media_type TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
""")

# ======================
# COMMENTS
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
""")

cursor.execute("""
ALTER TABLE comments
ADD COLUMN IF NOT EXISTS text TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS comment_parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE;
""")

# ======================
# LIKES
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
""")

cursor.execute("""
ALTER TABLE likes
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
""")

# ======================
# FOLLOWS
# ======================

cursor.execute("""
CREATE TABLE IF NOT EXISTS follows (
    user1_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user1_id, user2_id),
    CHECK (user1_id <> user2_id)
);
""")

#Notifacations
cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    recipient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    actor_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    comment_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

connection.commit()

cursor.close()
connection.close()
