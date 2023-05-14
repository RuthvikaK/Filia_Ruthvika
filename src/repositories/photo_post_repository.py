#Aaloki
from src.models import PhotoPost, db
from sqlalchemy import or_

class PhotoPostRepository:
    def create_photo_post(self, user_id, photo_path, caption):
        new_photo_post = PhotoPost(user_id=user_id, photo_path=photo_path, caption=caption)

        db.session.add(new_photo_post)
        db.session.commit()
        return new_photo_post


    def get_photo_post(self, photo_post_id):
        return PhotoPost.query.get(photo_post_id)


    def update_photo_post(self, photo_post_id, photo_path=None, caption=None):
        photo_post = self.get_photo_post(photo_post_id)
        if photo_post is None:
            return None
        if photo_path is not None:
            photo_post.photo_path = photo_path

        if caption is not None:
            photo_post.caption = caption
        db.session.commit()
        return photo_post
    
    def search_photo_posts(self, search_query, user_id=None):
        if user_id is not None:
            return PhotoPost.query.filter(PhotoPost.caption.ilike(f'%{search_query}%'), PhotoPost.user_id == user_id).all()
        return PhotoPost.query.filter(PhotoPost.caption.ilike(f'%{search_query}%')).all()

    def delete_photo_post(self, photo_post_id):
        photo_post = self.get_photo_post(photo_post_id)
        if photo_post is None:
            return None
        db.session.delete(photo_post)
        db.session.commit()
        return True

    def get_all_photo_posts(self, user_id=None):
        if user_id is not None:
            return PhotoPost.query.filter_by(user_id=user_id).all()
        return PhotoPost.query.all()

# Create a singleton instance of the repository
photo_post_repository_singleton = PhotoPostRepository()
