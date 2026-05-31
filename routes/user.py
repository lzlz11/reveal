import os
import uuid
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, current_app
from middleware.auth import require_auth
from models.follow import (
    toggle_follow,
    get_following_users,
    get_followers_users,
    get_followers_count,
    get_following_count,
    is_following,
)
from models.user import get_user_by_id, update_profile_picture
from models.post import get_posts_by_user_id
from services.notification_service import notify_user_followed

users_bp = Blueprint('users', __name__)
ALLOWED_IMAGES = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

@users_bp.route('/profile')
@require_auth
def profile():
    user = get_user_by_id(request.user_id)
    followers = get_followers_users(request.user_id)
    following = get_following_users(request.user_id)
    posts = get_posts_by_user_id(request.user_id)

    return render_template(
        'users/profile.html',
        user=user,
        followers=followers,
        following=following,
        posts=posts,
        followers_count=get_followers_count(request.user_id),
        following_count=get_following_count(request.user_id),
        current_username=request.username,
        is_own_profile=True,
        is_following_user=False
    )

@users_bp.route('/users/<int:user_id>/follow', methods=['POST'])
@require_auth
def follow(user_id):
    """
    Toggle follow/unfollow for the given user.
    Returns JSON: { "following": true }
    """
    if int(user_id) == int(request.user_id):
        return jsonify({'error': 'You cannot follow yourself.'}), 400

    result = toggle_follow(follower_id=request.user_id, following_id=user_id)
    if result['following']:
        notify_user_followed( actor_user_id=request.user_id, recipient_user_id=user_id)
    return jsonify(result)


@users_bp.route('/profile/picture', methods=['POST'])
@require_auth
def upload_picture():
    """Handle profile picture upload."""
    file = request.files.get('picture')

    if not file or file.filename == '':
        return redirect(url_for('users.profile'))

    user = get_user_by_id(request.user_id)
    if user['profile_picture_path']:
        old_path = os.path.join(current_app.static_folder, user['profile_picture_path'])
        if os.path.exists(old_path):
            os.remove(old_path)

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGES:
        followers = get_followers_users(request.user_id)
        following = get_following_users(request.user_id)
        return render_template(
            'users/profile.html',
            user=get_user_by_id(request.user_id),
            followers=followers,
            following=following,
            posts=get_posts_by_user_id(request.user_id),
            followers_count=get_followers_count(request.user_id),
            following_count=get_following_count(request.user_id),
            current_username=request.username,
            is_own_profile=True,
            is_following_user=False,
            error='Unsupported file type. Allowed: jpg, png, gif, webp.'
        )

    filename = f"{uuid.uuid4().hex}.{ext}"
    relative_path = f"uploads/avatars/{filename}"
    absolute_path = os.path.join(current_app.static_folder, 'uploads', 'avatars', filename)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    file.save(absolute_path)

    update_profile_picture(request.user_id, relative_path)
    return redirect(url_for('users.profile'))



@users_bp.route('/users/<int:user_id>')
@require_auth
def public_profile(user_id):
    user = get_user_by_id(user_id)

    if not user:
        return "User not found", 404

    posts = get_posts_by_user_id(user_id)
    followers = get_followers_users(user_id)
    following = get_following_users(user_id)

    return render_template(
        'users/profile.html',
        user=user,
        followers=followers,
        following=following,
        posts=posts,
        followers_count=get_followers_count(user_id),
        following_count=get_following_count(user_id),
        current_username=request.username,
        is_own_profile=int(user_id) == int(request.user_id),
        is_following_user=is_following(request.user_id, user_id)
    )
