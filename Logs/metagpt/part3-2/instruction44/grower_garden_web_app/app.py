import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from src.models import db, User, Item, Transaction
from src.forms import RegistrationForm, LoginForm, PurchaseForm
from src.payment import PaymentProcessor
from src.roblox_bot import RobloxBot
from src.discord_logger import DiscordLogger
from src.utils import login_required, admin_required

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///grower_garden.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialize modules
payment_processor = PaymentProcessor()
roblox_bot = RobloxBot()
discord_logger = DiscordLogger()

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            roblox_username=form.roblox_username.data,
            private_server_info=form.private_server_info.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/purchase/<int:item_id>', methods=['GET', 'POST'])
@login_required
def purchase(item_id):
    item = Item.query.get_or_404(item_id)
    user = User.query.get(session['user_id'])
    form = PurchaseForm(obj=user)
    if form.validate_on_submit():
        # Update user data if changed
        user.roblox_username = form.roblox_username.data
        user.private_server_info = form.private_server_info.data
        db.session.commit()

        # Process payment
        transaction = payment_processor.process_payment(user, item)
        if transaction.status != 'success':
            flash('Payment failed. Please try again.', 'danger')
            return render_template('purchase.html', form=form, item=item)

        # Deliver item via Roblox bot
        delivery_proof_url = roblox_bot.deliver_item(user, item)
        transaction.delivery_proof_url = delivery_proof_url
        transaction.status = 'delivered'
        db.session.commit()

        # Log transaction and delivery proof to Discord
        discord_logger.log_transaction(transaction)
        discord_logger.log_delivery_proof(transaction, delivery_proof_url)

        flash('Purchase successful! Your item will be delivered shortly.', 'success')
        return redirect(url_for('index'))
    return render_template('purchase.html', form=form, item=item)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('admin_dashboard.html', transactions=transactions)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)