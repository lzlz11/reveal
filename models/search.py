from config import get_db

def search_users(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.name AS username, u.bio, u.profile_picture_path,
               COUNT(DISTINCT f.user1_id) AS followers_count
        FROM users u
        LEFT JOIN follows f ON f.user2_id = u.id
        WHERE u.name ILIKE %s
        GROUP BY u.id
        ORDER BY followers_count DESC
        LIMIT 20
    """, (f'%{query}%',))
    return cursor.fetchall()

def search_posts(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.caption, p.media_path, p.media_type, p.created_at,
               p.user_id, u.name AS username, u.profile_picture_path,
               COUNT(DISTINCT l.id) AS like_count, COUNT(DISTINCT c.id) AS comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN likes l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        WHERE p.caption ILIKE %s
        GROUP BY p.id, u.name, u.profile_picture_path
        ORDER BY p.created_at DESC
        LIMIT 30
    """, (f'%{query}%',))
    return cursor.fetchall()