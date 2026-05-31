from flask import Blueprint, request, render_template
from middleware.auth import require_auth
from models.search import search_users, search_posts
from models.notification import get_unread_notification_count

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
@require_auth
def search():
    query = request.args.get('q', '').strip()
    users = []
    posts = []
    if query:
        users = search_users(query)
        posts = search_posts(query)
    unread_notification_count = get_unread_notification_count(request.user_id)
    return render_template('search.html',
        query=query, users=users, posts=posts,
        current_user_id=request.user_id, username=request.username,
        unread_notification_count=unread_notification_count
    )