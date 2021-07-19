from flask import Flask, render_template, url_for, redirect, flash, abort, g
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy.orm import relationship
from wtforms import StringField, TextAreaField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, URL, ValidationError
import smtplib
import email_validator
import datetime as dt
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random
import os

#ENV
TO_EMAIL = "HELP"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Databases (SQL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# flask_login
login_manager = LoginManager()
login_manager.init_app(app)

Bootstrap(app)
ckeditor = CKEditor(app)

# FORMS
class ContactForm(FlaskForm):
    contact_name = StringField('Name', validators=[DataRequired()])
    contact_email = StringField('Email', validators=[DataRequired(), Email()])
    contact_msg = TextAreaField('Message', validators=[DataRequired()])
    contact_submit = SubmitField("Submit")


class NewPostForm(FlaskForm):
    new_post_title = StringField('Blog Post Title', validators=[DataRequired()])
    new_post_des = StringField('Blog Post Description', validators=[DataRequired()])
    new_post_author = StringField('Your Name', validators=[DataRequired()])
    new_post_img = StringField('Blog Image URL', validators=[DataRequired(), URL()])
    new_post_featured = SelectField("Featured?", validators=[DataRequired()], choices=[True, False])
    new_post_body = CKEditorField("Blog Body", validators=[DataRequired()])
    new_post_form_submit = SubmitField("Submit Post")


class CommentForm(FlaskForm):
    comment = CKEditorField("Comments", validators=[DataRequired()])
    comment_submit = SubmitField("Submit New Comment")


# REGISTER FORM
def username_not_taken(form, field):
    username = field.data
    if User.query.filter_by(username=username).first(): # username already exists in db
        raise ValidationError('This Username Has Already Been Taken. Please Use Another.')


def email_not_used(form, field):
    email = field.data
    if User.query.filter_by(email=email).first(): # username already exists in db
        raise ValidationError('An Account Has Already Been Registered With This E-Mail.')


class RegisterForm(FlaskForm):
    register_name = StringField('Name', validators=[DataRequired()])
    register_email = StringField('Email', validators=[DataRequired(), email_not_used])
    register_username = StringField('Username', validators=[DataRequired(), username_not_taken])
    register_pswd = StringField('Password', validators=[DataRequired()])
    register_submit = SubmitField("Register User")


class LoginForm(FlaskForm):
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_submit = SubmitField("Login")


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    description = db.Column(db.String(300), unique=False, nullable=False)
    date = db.Column(db.String(300), unique=False, nullable=False)
    body = db.Column(db.String(2000), unique=True, nullable=False)
    author = db.Column(db.String(2000), unique=False, nullable=False)
    img_path = db.Column(db.String(2000), unique=False, nullable=False)
    featured = db.Column(db.Boolean, unique=False, nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    profile_img = db.Column(db.String(1000), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(1000), unique=True, nullable=False)
    hash_salt = db.Column(db.String(2000), unique=False, nullable=False)
    admin = db.Column(db.Boolean, unique=False, nullable=False)
    comments = relationship("Comment", back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    parent_post = relationship("Post", back_populates="comments")


db.create_all()
db.session.commit()

def admin_only(func):
    @wraps(func)
    def decorate(*args, **kwargs):
        if current_user.admin == False:
            return abort(403)
        else:
            return func(*args, **kwargs)
    return decorate


def logged_out_required(func):
    @wraps(func)
    def decorate(*args, **kwargs):
        if not current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            return abort(403)
    return decorate


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    all_posts = db.session.query(Post).all()
    all_posts.reverse() # to sort by newest
    return render_template('home.html', all_posts=all_posts, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/posts')
def posts():
    all_posts = db.session.query(Post).all()
    all_posts.reverse()  # to sort by newest
    return render_template('posts.html', all_posts=all_posts, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/post/<int:post_id>', methods=["POST", "GET"])
def get_post(post_id):
    comment_form = CommentForm()
    post_to_get = Post.query.get(post_id)
    if comment_form.validate_on_submit():
        new_comment = Comment(
            text=comment_form.comment.data,
            parent_post=post_to_get,
            comment_author=current_user
        )
        db.session.add(new_comment)
        db.session.commit()
        return render_template('post.html', post=post_to_get, logged_in=current_user.is_authenticated, cur_user=current_user, form=comment_form)
    return render_template('post.html', post=post_to_get, logged_in=current_user.is_authenticated, cur_user=current_user, form=comment_form)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        name = contact_form.name.data
        email = contact_form.email.data
        msg = contact_form.msg.data
        email_contact_data(name, email, msg)
        return redirect(url_for('contact'))
    return render_template('contact.html', form=contact_form, logged_in=current_user.is_authenticated, cur_user=current_user)


def email_contact_data(name, email, msg):
    to_email = TO_EMAIL
    from_email = os.environ.get('FROM_EMAIL')
    from_pass = os.environ.get('FROM_PASSWORD')

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(from_email, from_pass)
        connection.sendmail(
            from_addr=from_email,
            to_addrs=to_email,
            msg=f"Subject:The Hearth Contact Form Submission\n\n{name} has tried to contact you.\n They sent the message: {msg}.\n"
                f"To reply to them, send and email to {email}."
        )


@app.route('/new-post', methods=['POST', 'GET'])
@login_required
@admin_only
def new_post():
    new_post_form = NewPostForm()
    if new_post_form.validate_on_submit():
        new_post_featured = False
        if new_post_form.new_post_featured.data == "True":
            new_post_featured = True
        new_post = Post(
            title=new_post_form.new_post_title.data,
            description=new_post_form.new_post_des.data,
            date=dt.datetime.now().strftime("%b %d, %Y"),
            author=new_post_form.new_post_author.data,
            body=new_post_form.new_post_body.data,
            img_path=new_post_form.new_post_img.data,
            featured=new_post_featured
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('new_post'))
    return render_template('new_post.html', form=new_post_form, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/edit-post/<int:post_id>', methods=["POST", "GET"])
@login_required
@admin_only
def edit_post(post_id):
    post = Post.query.get(post_id)
    edit_form = NewPostForm(new_post_title=post.title, new_post_des=post.description, new_post_author=post.author,
                            new_post_img=post.img_path, new_post_body=post.body, new_post_featured=post.featured)
    if edit_form.validate_on_submit():
        edit_post_featured = post.featured
        if edit_form.new_post_featured.data == 'True':
            edit_post_featured = True
        else:
            edit_post_featured = False
        post.title = edit_form.new_post_title.data
        post.description = edit_form.new_post_des.data
        post.author = edit_form.new_post_author.data
        post.img_path = edit_form.new_post_img.data
        post.body = edit_form.new_post_body.data
        post.featured = edit_post_featured
        db.session.commit()
        return redirect(url_for('get_post', post_id=post_id))
    return render_template('edit_post.html', post=post, form=edit_form, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/delete-post/<int:post_id>')
@login_required
@admin_only
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts'), logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/register', methods=["GET", "POST"])
@logged_out_required
def register():
    profile_imgs = ["../static/images/profile/anduin.jpeg", "../static/images/profile/garrosh.jpeg",
                    "../static/images/profile/guldan.jpeg", "../static/images/profile/illidan.jpeg",
                    "../static/images/profile/jaina.jpeg", "../static/images/profile/malfurion.png",
                    "../static/images/profile/rexxar.jpeg", "../static/images/profile/thrall.jpeg",
                    "../static/images/profile/uther.jpeg", "../static/images/profile/valeera.jpeg"]
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.register_email.data
        name = register_form.register_name.data
        username = register_form.register_username.data
        password = register_form.register_pswd.data

        hashed_and_salted_pswd = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            profile_img=random.choice(profile_imgs),
            username=username,
            email=email,
            name=name,
            hash_salt=hashed_and_salted_pswd,
            admin=False
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=register_form, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/login', methods=["GET", "POST"])
@logged_out_required
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.login_username.data).first()
        if not user:
            flash("That Username Does Not Exist. Please Try Again")
            return render_template('login.html', form=login_form)
        elif not check_password_hash(user.hash_salt, login_form.login_password.data):
            flash('Password Incorrect. Please Try Again.')
            return render_template('login.html', form=login_form)
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=login_form, logged_in=current_user.is_authenticated, cur_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home", logged_in=current_user.is_authenticated))


if __name__ == '__main__':
    app.run(debug=True)