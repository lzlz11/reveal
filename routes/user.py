import os
import uuid
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, current_app
from middleware.auth import require_auth
from models.follow import toggle_follow, get_following_users
from models.user import get_user_by_id, update_profile_picture
from models.post import get_posts_by_user_id

users_bp = Blueprint('users', __name__)
ALLOWED_IMAGES = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

@users_bp.route('/profile')
@require_auth
def profile():
    user = get_user_by_id(request.user_id)
    following = get_following_users(request.user_id)
    posts = get_posts_by_user_id(request.user_id)

    return render_template(
        'users/profile.html',
        user=user,
        following=following,
        posts=posts,
        followers_count=0,
        following_count=len(following),
        current_username=request.username
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
        return render_template('users/profile.html',
                               user=get_user_by_id(request.user_id),
                               following=get_following_users(request.user_id),
                               current_username=request.username,
                               error='Unsupported file type. Allowed: jpg, png, gif, webp.'
                               )

    filename = f"{uuid.uuid4().hex}.{ext}"
    relative_path = f"uploads/avatars/{filename}"
    absolute_path = os.path.join(current_app.static_folder, 'uploads', 'avatars', filename)

    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    file.save(absolute_path)

    update_profile_picture(request.user_id, relative_path)
    return redirect(url_for('users.profile'))
