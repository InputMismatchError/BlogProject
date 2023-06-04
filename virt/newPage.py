from flask import Flask, render_template, flash , request , url_for , redirect
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime , date
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import UserMixin , login_user , LoginManager , login_required , logout_user , current_user
from WebForms import LoginForm , UserForm , UserForm_withfeedback , PasswordForm , PostForm , SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os

# safe , capitalize , lower , upper , title , trim , striptags

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/users' 
app.config['SECRET_KEY'] = "password"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__))+'\static\images') # Assigns upload path to variable
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

#UPLOAD_FOLDER = 'virt/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ckeditor = CKEditor(app)

admin_id = 33

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model ,UserMixin):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False , unique=True)   
    fav_color = db.Column(db.String(100),nullable=True)
    date_added = db.Column(db.DateTime , default=datetime.utcnow)
    username = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(10000),nullable=True)
    posts = db.relationship('Posts' , backref='poster')
    

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)
    def __repr__(self):
        return '<Name %r>' % self.name

class Posts(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)    
    slug = db.Column(db.String(255))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class ShortFeedback(db.Model):
    name = db.Column(db.String(150), primary_key = True)
    feedback = db.Column(db.Text)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)



@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.profile_pic = request.files['profile_pic']


        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        
        saver = request.files['profile_pic']
        

        name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            flash("User Updated Successfuly")
            return redirect(url_for('dashboard'))
        except:
            flash("Error, try again!")
            return redirect(url_for('user_add'))
    else:       
        return render_template('update.html', name_to_update = name_to_update , form = form,id=id)
    
    
@app.route('/')
def index():
    
    return render_template("index_copy.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html" , user_name = name)

@app.errorhandler(404)
def error_page(e):
    return render_template("404.html") , 404


@app.route('/feedback', methods = ['GET','POST'])
def name():
    name = None
    form = UserForm_withfeedback()
    if form.validate_on_submit():
        user = ShortFeedback.query.filter_by(feedback=form.feedback.data).first()
        isDuplicate = ShortFeedback.query.filter_by(name = form.name.data).first()
        if isDuplicate is not None:
           flash("You have already gave a feedback with this username, try another one")
           return redirect(url_for('name'))
        if user is None:
            user = ShortFeedback(name = form.name.data, feedback = form.feedback.data)
            db.session.add(user)
            db.session.commit() 
        name = form.name.data
        form.name.data = ''
        form.feedback.data = ''
        flash("Feedback is taken, thank you!")
    return render_template('name.html', name = name , form = form) 

@app.route('/user/add', methods = ['GET','POST'])
def user_add():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users.query.filter_by(username=form.username.data).first()
            if user is None:
                hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
                user = Users(username = form.username.data,name = form.name.data, email = form.email.data , fav_color = form.fav_color.data , password_hash = hashed_pw ,profile_pic = form.profile_pic.data )
                db.session.add(user)
                db.session.commit()
                user.profile_pic = request.files['profile_pic']
                pic_filename = secure_filename(user.profile_pic.filename)
                pic_name = str(uuid.uuid1()) + "_" + pic_filename
                saver = request.files['profile_pic']
                user.profile_pic = pic_name
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                db.session.delete(user)
                db.session.add(user)
                db.session.commit()
                flash("User added successfully")                
            else:
                flash("This username is taken")
        else:
            flash("This email is taken")
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.password_hash.data = ''
        
    return render_template('user_add.html' , form = form, name = name)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully ! ")
        return render_template('delete.html' , 
        form = form, 
        name = name, 
        our_users = our_users,
        user_to_delete = user_to_delete)
    except:
        flash("An error has accured, try again !")
        return render_template('delete.html', 
        form = form, 
        name = name, 
        our_users = our_users,
        user_to_delete = user_to_delete)

@app.route('/test_pw',methods=['GET','POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None  
    form = PasswordForm()


    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        

        pw_to_check = Users.query.filter_by(email = email).first()
        
        passed = check_password_hash(pw_to_check.password_hash  ,password)

    return render_template("test_pw.html",
    email=email,
    password=password, 
    pw_to_check=pw_to_check,  
    passed=passed, 
    form=form   
    ) 

@app.route('/date')
def get_date():
    dictof_date_1 = {"Date" : date.today()}
    return dictof_date_1

@app.route('/add-post', methods=['GET','POST'])
@login_required
def postform():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
        title = form.title.data,
        content = form.content.data,
        poster_id = poster,
        slug = form.slug.data,)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash("Blog Post Submitted Succesfully !")
    
    post_items = Posts.query.order_by(Posts.date_posted)

    return render_template('add_blogpost.html', form = form, post_items = post_items)

@app.route('/blogposts/pages/<int:page>')
def blogposts(page):

    
    template = 'blogposts' + str(page) + '.html'

    if page==1000 and (current_user.id == admin_id):
        template = 'blogpost_all.html'
    if page == 1:
        template = 'blogposts.html'
    if page == 0:
        template = 'blogposts_left.html'
    post_items = Posts.query.order_by(Posts.date_posted)

    a = len(list(post_items))

    return render_template(template, post_items = post_items)

@app.context_processor
def base():
    url = request.path
    return dict(url = url)

@app.route('/blogposts/<int:id>')
def showPost(id):
    post = Posts.query.get_or_404(id)
    return render_template('post_of_blogposts.html', post = post, admin_id=admin_id)



@app.route('/update_blogpost/<int:id>',methods=['GET','POST'])
@login_required
def update_blogpost(id):
    form = PostForm()
    post = Posts.query.get_or_404(id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated")
        return redirect(url_for('showPost', id = post.id))
    if current_user.id == post.poster_id or current_user.id == admin_id:   
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('update_blogpost.html',form = form,post= post)
    else :
        return render_template('access_denied.html')    

@app.route('/delete_blogpost/<int:id>')
@login_required
def delete_blogpost(id):
    user_to_delete = Posts.query.get_or_404(id)
    form = PostForm()
    our_users = Posts.query.order_by(Posts.date_posted)
    user_id = current_user.id

    if user_id == user_to_delete.poster.id or current_user.id == admin_id:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("Blogpost deleted successfully ! ")
            return render_template('delete_blogpost.html' , 
            form = form,  
            our_users = our_users)
        except:
            flash("An error has accured, try again !")
            return render_template('delete_blogpost.html', 
            form = form, 
            our_users = our_users)
    else:
        return render_template('access_denied.html')

@app.route('/check/<int:id>', methods=['GET','POST'])

@app.route('/access_denied')
def access_denied():
    return render_template('access_denied.html')

@app.route('/log_in', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in, log out to log in with another account !")
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else :
                flash("Wrong email/password, try again !")
        else:
            flash("That user does not exits")
    return render_template('login.html',form = form)

@app.route('/log_out', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out !")
    return redirect(url_for('login'))

@app.route('/dashboard', methods = ['GET','POST'])
@login_required

def dashboard():
    user = current_user
    
    posts = None

    if Posts.query.filter_by(poster_id = current_user.id) != None:
        posts = Posts.query.filter_by(poster_id = current_user.id)

    return render_template('dashboard.html',user=user,posts = posts)

@app.route('/search', methods = ['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post_searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post_searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form = form , searched = post_searched , posts = posts)
    else:
        return redirect('blogposts')
        

@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == admin_id:
        return render_template('admin.html')
    else:
        flash("This account does not belong to an admin !")
        return redirect(url_for('dashboard'))

@app.route('/users_list')
@login_required
def users_list():
    id = current_user.id
    if id == admin_id:
        our_users = Users.query.order_by(Users.date_added)
        return render_template('users_list.html',our_users=our_users)

@app.route('/feedbacks')
@login_required
def feedbacks():
    id = current_user.id 
    if id == admin_id:
        our_users = ShortFeedback.query.order_by(ShortFeedback.date_added)
        return render_template('feedbacks.html', our_users=our_users)