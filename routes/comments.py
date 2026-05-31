from flask import Blueprint, jsonify, request
from middleware.auth import require_auth
from models.comment import add_comment, get_comments_by_post, comment_belongs_to_post, get_comment_by_id, delete_comment
from services.notification_service import notify_post_commented

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
@require_auth
def get_comments(post_id):
    comments = get_comments_by_post(post_id)
    return jsonify(comments)


@comments_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@require_auth
def post_comment(post_id):
    data = request.get_json()
    text = data.get('text', '').strip() if data else ''

    if not text:
        return jsonify({'error': 'Comment cannot be empty.'}), 400

    if len(text) > 1000:
        return jsonify({'error': 'Comment is too long.'}), 400

    comment = add_comment(
        user_id=request.user_id,
        post_id=post_id,
        text=text
    )

    notify_post_commented(
    actor_user_id=request.user_id,
    post_id=post_id,
    comment_id=comment['id']
    )
    return jsonify(comment), 201


@comments_bp.route('/posts/<int:post_id>/comments/<int:comment_id>/reply', methods=['POST'])
@require_auth
def reply_comment(post_id, comment_id):
    data = request.get_json()
    text = data.get('text', '').strip() if data else ''

    if not text:
        return jsonify({'error': 'Reply cannot be empty.'}), 400

    if len(text) > 1000:
        return jsonify({'error': 'Reply is too long.'}), 400
    
    if not comment_belongs_to_post(comment_id, post_id):
        return jsonify({'error': 'Parent comment not found for this post.'}), 404

    reply = add_comment(
        user_id=request.user_id,
        post_id=post_id,
        text=text,
        parent_id=comment_id
    )

    notify_post_commented(
    actor_user_id=request.user_id,
    post_id=post_id,
    comment_id=reply['id']
    )

    return jsonify(reply), 201

#delete comment and all its replies
@comments_bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment_route(post_id, comment_id):
    comment = get_comment_by_id(comment_id)

    if not comment or int(comment['post_id']) != int(post_id):
        return jsonify({'error': 'Comment not found.'}), 404

    if int(comment['user_id']) != int(request.user_id):
        return jsonify({'error': 'You cannot delete this comment.'}), 403

    delete_comment(comment_id)

    return jsonify({'deleted': True})