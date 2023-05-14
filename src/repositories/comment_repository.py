from src.models import Comment, db

class CommentRepository:
    def add_comment(self, user, comment_text):
        comment = Comment(user=user, comment_text=comment_text)
        db.session.add(comment)
        db.session.commit()
        return comment

    def get_all_comments(self):
        return Comment.query.all()

# Initialize the repository instance
comment_repository_singleton = CommentRepository()
