from market import app, db
from flask import render_template, url_for, redirect, flash, request, jsonify
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, CreateItemForm, UpdateBudgetForm
from flask_login import login_user, logout_user, login_required, current_user
import platform


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()
    if request.method == "POST":
        # Handle the purchased item
        purchased_item = request.form.get('purchased_item')
        p_item_obj = Item.query.filter_by(name=purchased_item).first()
        if p_item_obj:
            if current_user.can_purchase(p_item_obj):
                p_item_obj.buy_item(current_user)
                flash(f'Purchase Complete, thank you for buying a brand new {p_item_obj.name}'
                      f' for only {p_item_obj.show_price}$!', 'success')
            else:
                flash(f'Insufficient funds, You are missing {p_item_obj.price - current_user.budget}$', 'danger')
        # Handle the sold item
        sold_item = request.form.get('sold_item')
        s_item_obj = Item.query.filter_by(name=sold_item).first()
        if s_item_obj:
            if current_user.can_sell(s_item_obj):
                s_item_obj.sell_item(current_user)
                flash(f'Congratulations! You have sold your {s_item_obj.name} for {s_item_obj.show_price}$', 'success')

        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items,
                               sell_form=sell_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email_address=form.email_address.data,
                        password=form.password1.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash(f'Account created successfully, Logged in as {new_user.username}', 'success')
        return redirect(url_for('home_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error creating user: {err_msg}', category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Login Succesful, logged in as {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Login Failed! Please check email and password', category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for('home_page'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    create_item_form = CreateItemForm()
    budget_form = UpdateBudgetForm()
    if 'add_item' in request.form and create_item_form.validate_on_submit():
        new_item = Item(name=create_item_form.item_name.data, price=create_item_form.price.data,
                        description=create_item_form.description.data, barcode=create_item_form.barcode.data,
                        owner=None)
        db.session.add(new_item)
        db.session.commit()
        flash('Added a new item to the market!', 'success')
        return redirect(url_for('market_page'))
    elif 'change_budget' in request.form and budget_form.validate_on_submit():
        user = User.query.filter_by(username=budget_form.user_name.data).first()
        user.budget = budget_form.budget.data
        db.session.commit()
        return redirect(url_for('market_page'))
    return render_template('admin.html', create_item_form=create_item_form, budget_form=budget_form)


@app.route('/information', methods=['GET'])
def information():
    return {"processor": platform.processor(), "os name": platform.system()}
