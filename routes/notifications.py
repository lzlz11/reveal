from flask import Blueprint, render_template, request
from middleware.auth import require_auth
from models.notification import get_notifications_for_user, mark_notifications_as_read

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/notifications')
@require_auth
def notifications():
    notifications = get_notifications_for_user(request.user_id)
    mark_notifications_as_read(request.user_id)

    return render_template(
        'notifications.html',
        notifications=notifications
    )