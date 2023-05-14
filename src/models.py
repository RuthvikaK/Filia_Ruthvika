from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

post_likes = db.Table('post_likes',
db.Column("user_id", db.Integer, db.ForeignKey('filia_user.user_id')),
db.Column("post_id", db.Integer, db.ForeignKey('photo_post.id')))

follower = db.Table('follower',
db.Column("follower_id", db.Integer, db.ForeignKey('filia_user.user_id')),
db.Column("followed_id", db.Integer, db.ForeignKey('filia_user.user_id')))



# class PhotoPost(db.Model):
#     __tablename__ = 'photo_post'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('filia_user.user_id'), nullable=False)
#     photo_path = db.Column(db.String(255), nullable=False)
#     caption = db.Column(db.String(255), nullable=True)

post_comments = db.Table('post_comments',
db.Column('post_id', db.Integer, db.ForeignKey('photo_post.id')),
db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')))


class FiliaUser(db.Model):
    __tablename__ = 'filia_user'
    user_id = db.Column(db.Integer, primary_key=True) # has a serial type
    firstname = db.Column(db.String(255), nullable=False) # null is not an option
    lastname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(16), nullable=False, unique=True)
    gender = db.Column(db.String(255), nullable=True)
    major = db.Column(db.String(255), nullable=False)
    grad_date = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.String(255), nullable=False)
    profile_path = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    #posts_liked = db.relationship('PhotoPost', secondary=post_likes, backref='likes')
    followers = db.relationship('FiliaUser', secondary=follower, primaryjoin=user_id==follower.c.followed_id, secondaryjoin=user_id==follower.c.follower_id,  backref='following')

    # following = db.relationship('FiliaUser', secondary=follower, backref='followers')

    # postsLiked = db.relationship('PhotoPost', secondary=postLikes, backref='likes')  

    #following = db.relationship('FiliaUser', secondary=follower, backref='followers')
    comments = db.relationship('Comment', backref='author')
    posts_liked = db.relationship('PhotoPost', secondary=post_likes, backref='likes')  

    def post_count(self):
        return db.session.execute(db.select(PhotoPost).filter_by(user_id=self.id)).count()


class PhotoPost(db.Model):
    __tablename__ = 'photo_post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('filia_user.user_id'), nullable=False)
    photo_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    comments = db.relationship('Comment', secondary=post_comments)

class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationship with the FiliaUser model
    creator_id = db.Column(db.Integer, db.ForeignKey('filia_user.user_id'))
    creator = db.relationship('FiliaUser', backref='created_communities')

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('filia_user.user_id'))

    # Relationships
    user = db.relationship('FiliaUser', backref=db.backref('user_comments'))
    associated_posts = db.relationship('PhotoPost', secondary=post_comments, backref=db.backref('post_comments'))