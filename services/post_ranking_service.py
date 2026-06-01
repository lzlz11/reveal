from datetime import datetime, timezone

from config import get_db


def calculate_hot_score(like_count, comment_count, created_at, author_followed=False):
    engagement = like_count * 1 + comment_count * 2

    now = datetime.now()
    age_seconds = (now - created_at).total_seconds()
    age_hours = max(age_seconds / 3600, 0)

    hot_score = (engagement + 1) / ((age_hours + 2) ** 1.2)

    if author_followed:
        hot_score += 0.5

    return hot_score


def get_ranked_feed_post_ids(current_user_id, limit=50):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.user_id,
            p.created_at,
            COUNT(DISTINCT l.id) AS like_count,
            COUNT(DISTINCT c.id) AS comment_count,
            CASE
                WHEN f.user2_id IS NULL THEN FALSE
                ELSE TRUE
            END AS author_followed
        FROM posts p
        LEFT JOIN likes l ON p.id = l.post_id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN follows f
            ON f.user1_id = %s
           AND f.user2_id = p.user_id
        GROUP BY p.id, p.user_id, p.created_at, f.user2_id
        LIMIT 200
    """, (current_user_id,))

    posts = cursor.fetchall()

    ranked_posts = []

    for post in posts:
        score = calculate_hot_score(
            like_count=post['like_count'],
            comment_count=post['comment_count'],
            created_at=post['created_at'],
            author_followed=post['author_followed']
        )

        ranked_posts.append((post['id'], score))

    ranked_posts.sort(key=lambda item: item[1], reverse=True)

    return [post_id for post_id, score in ranked_posts[:limit]]