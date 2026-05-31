from config import get_db


def create_notification(recipient_user_id, actor_user_id, notification_type, post_id=None, comment_id=None):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO notifications
        (recipient_user_id, actor_user_id, type, post_id, comment_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (recipient_user_id, actor_user_id, notification_type, post_id, comment_id))

    db.commit()
    return cursor.fetchone()['id']


def get_notifications_for_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            n.id,
            n.type,
            n.post_id,
            n.comment_id,
            n.is_read,
            n.created_at,
            u.name AS actor_username,
            u.profile_picture_path AS actor_profile_picture_path
        FROM notifications n
        JOIN users u ON n.actor_user_id = u.id
        WHERE n.recipient_user_id = %s
          AND n.is_read = FALSE
        ORDER BY n.created_at DESC
        LIMIT 50
    """, (user_id,))

    return cursor.fetchall()


def get_unread_notification_count(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM notifications
        WHERE recipient_user_id = %s AND is_read = FALSE
    """, (user_id,))

    return cursor.fetchone()['count']


def mark_notifications_as_read(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE notifications
        SET is_read = TRUE
        WHERE recipient_user_id = %s
    """, (user_id,))

    db.commit()
