from wtforms import StringField , SubmitField , PasswordField 
from wtforms.validators import DataRequired , EqualTo , Length
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class UserForm_withfeedback(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    feedback = StringField("Feedback: ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("Email : ", validators=[DataRequired()])
    password_hash = PasswordField("Password : ", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    username = StringField("Username ", validators=[DataRequired()])
    email = StringField("Email : ", validators=[DataRequired()])
    submit = SubmitField("Submit")
    fav_color = StringField("Your Favorite Color : ")
    password_hash = PasswordField("Password : ",validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match !')])
    password_hash2 = PasswordField("Confirm your password : ",validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")

class PostForm(FlaskForm):
    title = StringField("Title" , validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    searched = StringField("Searched" , validators=[DataRequired()])
    submit = SubmitField("Submit")
    