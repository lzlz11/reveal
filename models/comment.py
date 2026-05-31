from config import get_db
from services.comment_tree import build_comment_tree

def add_comment(user_id, post_id, text, parent_id=None):
    """
    Insert a new comment and return the full comment row
    (including username) so it can be sent back to the browser immediately.
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO comments (user_id, post_id, text, comment_parent_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id, text, created_at, comment_parent_id
    """, (user_id, post_id, text, parent_id))

    db.commit()
    new_comment = cursor.fetchone()

    # Fetch the username to include in the response
    cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    return {
        'id':         new_comment['id'],
        'text':       new_comment['text'],
        'username':   user['name'],
        'created_at': new_comment['created_at'].strftime('%B %d, %Y · %H:%M'),
        'comment_parent_id': new_comment['comment_parent_id'],
        'replies': []
    }


def get_comments_by_post(post_id):
    """
    Return all comments for a post, oldest first, with their author's username.
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.text,
            c.created_at,
            c.comment_parent_id,
            u.name AS username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s
        ORDER BY c.created_at ASC
    """, (post_id,))

    rows = cursor.fetchall()

    # Convert datetime to string for JSON serialisation
    formatted = [
        {
            'id': row['id'],
            'text': row['text'],
            'username': row['username'],
            'created_at': row['created_at'].strftime('%B %d, %Y · %H:%M'),
            'comment_parent_id': row['comment_parent_id']
        }
        for row in rows
    ]

    return build_comment_tree(formatted)


def comment_belongs_to_post(comment_id, post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT 1 FROM comments
        WHERE id = %s AND post_id = %s
    """, (comment_id, post_id))
    return cursor.fetchone() is not None
