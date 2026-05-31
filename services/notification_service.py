from models.notification import create_notification
from models.post import get_post_by_id


def notify_post_liked(actor_user_id, post_id):
    post = get_post_by_id(post_id)

    if not post:
        return None

    recipient_user_id = post['user_id']

    if int(recipient_user_id) == int(actor_user_id):
        return None

    return create_notification(
        recipient_user_id=recipient_user_id,
        actor_user_id=actor_user_id,
        notification_type='like',
        post_id=post_id
    )


def notify_post_commented(actor_user_id, post_id, comment_id):
    post = get_post_by_id(post_id)

    if not post:
        return None

    recipient_user_id = post['user_id']

    if int(recipient_user_id) == int(actor_user_id):
        return None

    return create_notification(
        recipient_user_id=recipient_user_id,
        actor_user_id=actor_user_id,
        notification_type='comment',
        post_id=post_id,
        comment_id=comment_id
    )


def notify_user_followed(actor_user_id, recipient_user_id):
    if int(recipient_user_id) == int(actor_user_id):
        return None

    return create_notification(
        recipient_user_id=recipient_user_id,
        actor_user_id=actor_user_id,
        notification_type='follow'
    )