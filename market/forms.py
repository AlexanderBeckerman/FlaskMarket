from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.models import User, Item


class RegisterForm(FlaskForm):
    username = StringField(label='User Name', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=4, max=200), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("This Username Is Taken, Please Choose A Different Username")

    def validate_email_address(self, email_address_to_check):
        email = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email:
            raise ValidationError("This Email Is Taken, Please Choose A Different Email")


class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='Sell Item')


class CreateItemForm(FlaskForm):
    item_name = StringField(label='Item Name', validators=[Length(min=2, max=30), DataRequired()])
    price = IntegerField(label='Item Price In Dollars', validators=[DataRequired()])
    barcode = StringField(label='Item Barcode', validators=[DataRequired()])
    description = StringField(label='Item Description', validators=[DataRequired()])
    submit = SubmitField(label='Create Item')

    def validate_barcode(self, barcode_to_check):
        item = Item.query.filter_by(barcode=barcode_to_check.data).first()
        if item:
            raise ValidationError("This Barcode already exists, input a different barcode!")


class UpdateBudgetForm(FlaskForm):
    user_name = StringField(label='User Name', validators=[DataRequired(), Length(min=2, max=30)])
    budget = IntegerField(label='Add Money', validators=[DataRequired()])
    submit = SubmitField(label='Update Budget')

    def validate_user_name(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user is None:
            raise ValidationError("No user found, please check the username")

