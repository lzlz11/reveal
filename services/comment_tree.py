def build_comment_tree(rows):
    comments_by_id = {}

    for row in rows:
        comment = dict(row)
        comment['replies'] = []
        comments_by_id[comment['id']] = comment

    tree = []

    for comment in comments_by_id.values():
        parent_id = comment.get('comment_parent_id')

        if parent_id is None:
            tree.append(comment)
        elif parent_id in comments_by_id:
            comments_by_id[parent_id]['replies'].append(comment)

    return tree