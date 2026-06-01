from flask import Blueprint, render_template, request
from middleware.auth import require_auth
from models.post import get_posts_by_ids
from models.like import get_liked_post_ids
from models.follow import get_users_by_ids, get_followed_ids
from services.follow_recommendation_service import get_suggested_user_ids
from models.notification import get_unread_notification_count
from services.post_ranking_service import get_ranked_feed_post_ids

home_bp = Blueprint('home', __name__)



@home_bp.route('/home')
@require_auth
def home():
    # Posts
    post_ids = get_ranked_feed_post_ids(request.user_id)
    posts     = get_posts_by_ids(post_ids)
    liked_ids = get_liked_post_ids(request.user_id, post_ids)

    # Suggestions
    suggested_ids = get_suggested_user_ids(request.user_id)
    suggestions   = get_users_by_ids(suggested_ids)

    # Which users the current user already follows
    # (so the follow button renders correctly on page load)
    followed_ids = get_followed_ids(request.user_id)
    unread_notification_count = get_unread_notification_count(request.user_id)

    return render_template('home.html',
    username=request.username,
    current_user_id=request.user_id,
    posts=posts,
    liked_ids=liked_ids,
    suggestions=suggestions,
    followed_ids=followed_ids,
    unread_notification_count=unread_notification_count
    )