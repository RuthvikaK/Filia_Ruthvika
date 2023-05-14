import os
from sqlalchemy import or_
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from src.models import db, FiliaUser, PhotoPost,  Community, Comment, post_comments
from src.repositories.photo_post_repository import photo_post_repository_singleton
from flask import jsonify
from flask import Flask, abort, redirect, render_template, request, session, flash, url_for
from src.repositories.comment_repository import comment_repository_singleton 
from security import bcrypt
import itsdangerous
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime


load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
#app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['RESET_PASSWORD_SECRET'] = os.getenv('RESET_PASSWORD_SECRET')

app.secret_key = os.getenv('APP_SECRET')

db.init_app(app)
bcrypt.init_app(app)

users = []


# Import the wraps function from functools module
from functools import wraps

# code for making a folder for uploading user's profile pic 
PROFILE_PICS_FOLDER = 'static/profile-pics'
app.config['PROFILE_PICS_FOLDER'] = PROFILE_PICS_FOLDER

# code for making a folder for user's posts
UPLOAD_FOLDER_POSTS = 'static/uploads' #os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER_POSTS'] = UPLOAD_FOLDER_POSTS


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'heic'}

app.config['UPLOAD_FOLDER_POSTS'] = UPLOAD_FOLDER_POSTS

@app.route('/')
# @login_required
def index():
    # del session['user']
    if 'user' not in session: 
        return render_template('/welcome_page.html')
    #Fetch all PhotoPost records from the database
    posts = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).all()
  
    if 'user' in session:
        return redirect('/home_page')
    return render_template('/welcome_page.html')


@app.post('/welcome_page')
def welcome_page():
    return render_template('welcome_page.html')

@app.post('/register')
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    phone = request.form.get('phoneNumber')
    gender= request.form.get('gender')
    major = request.form.get('major')
    grad_date = request.form.get('gradDate')
    bio = request.form.get('bio')
    bio = ''
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        abort(400)

    if 'profile_path' not in request.files:
        print('profile_path')
        abort(400)

    profile_path = request.files['profile_path']

    if profile_path.filename == '' or profile_path.filename.rsplit('.', 1)[1] not in ['jpg', 'jpeg', 'png', 'gif']:
        abort(400)

    # save the uploaded file to the user's directory
    profile_path.filename = f'{username}.{profile_path.filename.split(".")[-1]}'
    filename = secure_filename(profile_path.filename)
    filepath = os.path.join(app.config['PROFILE_PICS_FOLDER'], filename)
    profile_path.save(filepath)

    hashed_password = bcrypt.generate_password_hash(password).decode()

    new_user = FiliaUser(firstname = firstname,
                        lastname = lastname, 
                        email = email,
                        phone = phone,
                        gender = gender,
                        major = major,
                        grad_date = grad_date,
                        bio = bio,
                        profile_path = filepath.replace('static/', ''),
                        username = username, 
                        password = hashed_password)
                      
    db.session.add(new_user)
    db.session.commit()

    user = {}
    user["firstname"] = firstname
    user["lastname"] = lastname
    user["email"] = email
    user["phone"] = phone
    user["gender"] = gender
    user["major"] = major
    user["grad_date"] = grad_date
    user["bio"] = bio
    user["username"] = username
    user["profile_path"] = profile_path
    users.append(user)

    return redirect('/')

@app.post('/login')
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        abort(400)
        return redirect('/login?error=Please enter both username and password')

    existing_user = FiliaUser.query.filter_by(username=username).first()

    if not existing_user:
        return redirect('/login?error=Invalid username')

    if not bcrypt.check_password_hash(existing_user.password, password):
        return redirect('/login?error=Invalid password')

    session['user'] = {
        'user_id': existing_user.user_id,
        'username': username,
        'profile_path': existing_user.profile_path,
        'firstname': existing_user.firstname,
        'lastname': existing_user.lastname,
        'email': existing_user.email,
        'phone': existing_user.phone,
        'gender': existing_user.gender,
        'major': existing_user.major,
        'grad_date': existing_user.grad_date,
        'bio': existing_user.bio,
    }
    return redirect('/home_page')

@app.get('/login')
def login_template():
    return render_template('login.html')

@app.context_processor
def user_info():
    # return session.get('user')
    return {"user": session.get('user')}

@app.get('/home_page')
def home_page():
    user = session['user']
    user_major = session['user']['major']
    if 'user' in session:
        user_info = session['user']
        current_user = FiliaUser.query.filter_by(username=user_info['username']).first()
        home_content = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).add_columns(PhotoPost.id).all()
     
     #posts = {'posts': home_content}
        posts = []
        for (user, post, post_id) in home_content:
            if user.major == user_major:
                post_dict = {
                    'user': user,
                    'post': post,
                    'photo_path': post.photo_path,
                    'id': post_id,
                    'caption': post.caption
                }
                posts.append(post_dict)
        return render_template('home_page.html', posts=posts)
        posts = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).all()
        comments = {}
        for _, post in posts:
            comments[post.id] = post.comments
        return render_template('home_page.html', user=current_user, posts=posts, comments=comments)
    else:
        return redirect('/login')

@app.post('/logout')
def logout():
    if "user" in session:
        del session['user']
    return redirect('/')

@app.get('/profile_page/<int:user_id>')
def profile_page(user_id):
    user = FiliaUser.query.get(user_id)
    is_user_page = user_id == session['user']['user_id']#checking if this is current user or someone else
    is_following = False
    if(not is_user_page):
       for i in user.following:
           if(i.user_id == session['user']['user_id']):
               is_following = True
    
    num_followers = len(user.followers)
    num_following = len(user.following)

    profile_content = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).all()
    profile_posts = []
    for user, post in profile_content:
        if user.user_id == user_id:
            post_dict = {
                'user': user,
                'post': post,
                'photo_path': post.photo_path
            }
            profile_posts.append(post_dict)

    #return render_template('profile_page.html', num_posts = num_posts)
    #num_posts = PhotoPost.query.get(user_id)
    num_posts = PhotoPost.query.filter_by(user_id=user_id).count()
    return render_template('profile_page.html', profile_posts = profile_posts, is_following = is_following, num_following = num_following, num_followers = num_followers, user_id = user_id, user = user, num_posts = num_posts, is_user_page = is_user_page)

@app.get('/profile_page/<int:user_id>/unfollow')
def unfollow(user_id):
    user = FiliaUser.query.get(user_id)#getting the user that the sessioned user is unfollowing
    for i in user.followers:
        if(i.user_id == session['user']['user_id']):
            user.followers.remove(i)
            ses_user = FiliaUser.query.get(session['user']['user_id'])
            ses_user.following.remove(user)
    db.session.commit()
    return redirect(f'/profile_page/{user.user_id}')

@app.get('/profile_page/<int:user_id>/follow')
def follow(user_id):
    user = FiliaUser.query.get(user_id)#getting the user that the sessioned user is following
    is_following = False
    for i in user.followers:
        if(i.user_id == session['user']['user_id']):
            is_following = True
    ses_user = FiliaUser.query.get(session['user']['user_id'])
    if(not is_following) :
        user.followers.append(ses_user)
        ses_user.following.append(user)
    db.session.commit()
    return redirect(f'/profile_page/{user.user_id}')#python file is flask, and html file is jinja

@app.get('/view_edit_profile')
def view_edit_profile():
    user_id = session['user']['user_id']
    user = FiliaUser.query.get(user_id)
    return render_template('edit_profile.html', user_id = user_id, user = user)

@app.post('/edit_profile')
def edit_profile():
    user_id = session['user']['user_id']
    update_user = FiliaUser.query.get(user_id)
    required_params = ['firstname', 'lastname', 'email', 'phone', 'gender', 'major', 'grad_date', 'username']
    if not all(param in request.form for param in required_params):
        abort(400)
    update_user.firstname = request.form['firstname']
    update_user.lastname = request.form['lastname']
    update_user.email = request.form['email']
    update_user.phone = request.form['phone']
    update_user.gender = request.form['gender']
    update_user.major = request.form['major']
    update_user.grad_date = request.form['grad_date']
    update_user.username = request.form['username']
    update_user.bio = request.form['bio']
    db.session.commit()
    flash("Changes saved!")
    return redirect('/view_edit_profile')#, user_id = user_id)
 
    posts = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).all()
    return render_template('home_page.html', user=current_user, posts=posts)

@app.route('/reset_password_page')
def reset_password_page():
    return render_template('reset_password_page.html')

@app.get('/editprofpic')
def editprofpic():
    user_id = session['user']['user_id']
    # update_user = FiliaUser.query.get(user_id)
    # update_user.profile_path = request.form['profile_path']
    # db.session.commit()
    return redirect('/editprofpic')#, user_id = user_id)#, user = current_user )


@app.route('/create_photo_post', methods=['GET', 'POST'])
def create_photo_post():
    if request.method == 'POST':
        user_id = session['user']['user_id']  # Get user_id from session
        photo_path = request.files.get('photo')
        print(photo_path.filename)
        caption = request.form.get('caption')
        if not photo_path or not caption:
            abort(400)
        
        if photo_path.filename == '' or photo_path.filename.rsplit('.', 1)[1] not in ALLOWED_EXTENSIONS:
            abort(400)

        # Save the photo to a directory on your server
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        photo_path.filename = secure_filename(f'{user_id}.{current_time}.{photo_path.filename.split(".")[-1]}')
        filename = secure_filename(photo_path.filename)
        print(filename)
        postpath = os.path.join(app.config['UPLOAD_FOLDER_POSTS'], filename)  
        photo_path.save(postpath)
        
        # Save the photo URL to the database
        photo_path = os.path.join(UPLOAD_FOLDER_POSTS, filename)
        post = photo_post_repository_singleton.create_photo_post(user_id, photo_path, caption)
        return redirect('/')  # Changed to redirect to the home page
    else:
        return render_template('create_photo_post.html')


@app.route('/reset_password', methods=['POST'])
def reset_password_submit():
    email_or_username = request.form.get('email_or_username')
    new_password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    if new_password != confirm_password:
        return 'The passwords do not match.', 400

    user = FiliaUser.query.filter((FiliaUser.email == email_or_username) | (FiliaUser.username == email_or_username)).first()
    if not user:
        return 'User not found.', 400

    hashed_password = bcrypt.generate_password_hash(new_password).decode()
    user.password = hashed_password
    db.session.commit()
    return render_template('password_reset_successful.html')


@app.post('/delete_photo_post/<int:post_id>')
# @login_required
def delete_photo_post(post_id):
    post = PhotoPost.query.get_or_404(post_id)

    # Check if the current user is the owner of the post
    current_user_id = session['user']['user_id']
    if post.user_id != current_user_id:
        abort(403)
    return render_template('home_page.html')


@app.get('/create_photo_post/<int:post_id>')
def show_photo_post():
    photo = request.files.get('photo')
    caption = request.form.get('caption')
    if photo == '' and caption == '':
        abort(400)
    post = photo_post_repository_singleton.create_photo_post(photo, caption)
    return redirect(f'/create_photo_post/{post.id}')


@app.post('/create_photo_post/<int:post_id>/edit')
def edit_photo_post(post_id):
    # auto fill the form with old comments
    # Delete the post's photo from the file system
    photo_path = os.path.join(UPLOAD_FOLDER_POSTS, os.path.basename(post.photo_path))
    if os.path.exists(photo_path):
        os.remove(photo_path)

    current_user_id = session['user']['user_id']
    post = PhotoPost.query.get_or_404(post_id)
    if post.user_id != current_user_id:
        abort(403)


    post = PhotoPost.query.get_or_404(post_id)
    post.caption = request.form['caption']
    return render_template('home_page.html')


@app.get('/signup')
def signup():
    return render_template('signup.html')

@app.post('/uploadprofpic')
def uploadprofpic():
    upload = True
    return render_template('editprofpic.html', upload=upload)

@app.route('/comment_page/<int:post_id>')
def comment_page(post_id):
    post_and_user = db.session.query(FiliaUser, PhotoPost).join(PhotoPost, FiliaUser.user_id == PhotoPost.user_id).filter(PhotoPost.id == post_id).first()
    if post_and_user:
        user, post = post_and_user
        comments = post.comments
        return render_template('comment_page.html', user=user, post=post, comments=comments)
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    post = PhotoPost.query.get(post_id)
    if post:
        comments = post.comments
        return render_template('comment_page.html', post=post, comments=comments)
    return redirect(url_for('home'))

@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    if request.method == 'POST':
       
        user_id = session['user']['user_id']  
        text = request.form.get('comment')
        if text:
            new_comment = Comment(text=text, user_id=user_id)
            db.session.add(new_comment)
            db.session.commit()

            assoc = post_comments.insert().values(post_id=post_id, comment_id=new_comment.id)
            db.session.execute(assoc)
            db.session.commit()
            return redirect(url_for('comment_page', post_id=post_id)) 
    return redirect(url_for('home'))

def search_posts(query):
    query = f'%{query}%'
    posts = PhotoPost.query.filter(PhotoPost.caption.ilike(query)).all()
    users = FiliaUser.query.filter(FiliaUser.username.ilike(query)).all()
    communities = Community.query.filter(Community.name.ilike(query)).all()
    return {'posts': posts, 'users': users, 'communities': communities}

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if not search_query:
            abort(400)

        search_results = search_posts(search_query)
        return render_template('search_results.html', search_results=search_results)
    else:
        return render_template('search.html')


@app.post('/deleteprofpic')
#@app.post('/deleteprofpic/<photo>')
def deleteprofpic():
    delete = True
    return render_template('editprofpic.html', delete = delete)

# make a route for logout
if __name__ == '__main__':
     app.run(debug=True)
