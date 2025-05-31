import os
from os.path import split

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from champion import Champion
from build_recommender import BuildRecommender
from db_func import db_manager

app = Flask(__name__)
app.secret_key = os.environ['project_key']


@app.route('/')
def home():
    return render_template('home_page.html')


@app.route('/profile')
def profile():
    saved_builds = db_manager.get_saved_builds(session['user'])[0].split()
    return render_template('user_page.html', saved_builds=saved_builds)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        stored_hash = db_manager.get_pass(user)

        if stored_hash and check_password_hash(stored_hash, password):
            session['user'] = user
            return redirect(url_for('home'))
        flash("Invalid username or password.", "error")
        return render_template('login.html')

    if 'user' in session:
        return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/delete_acc', methods=['POST'])
def delete_acc():
    if 'user' in session:
        db_manager.delete_user(session['user'])
        session.clear()
    flash("Account deleted successfully.", "success")
    return redirect(url_for('home'))


@app.route('/update_passw', methods=['GET', 'POST'])
def update_passw():
    if request.method == 'POST':
        if 'user' not in session:
            return redirect(url_for('login'))

        user = session['user']
        old_password = request.form.get('old-password')
        new_passw = request.form.get('password')
        stored_hash = db_manager.get_pass(user)

        if stored_hash and check_password_hash(stored_hash, old_password):
            hashed = generate_password_hash(new_passw)
            response = db_manager.update_pass(session['user'], hashed)
            if response:
                flash("Password was changed successfully.", "success")
                return redirect(url_for("profile"))
            flash("Failed to update password.", "error")
            return redirect(url_for("profile"))

    return render_template('change_pass.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            user = request.form.get('username')
            password = request.form.get('password')

            if not email or not user or not password:
                flash("All fields are required.", "error")
                return render_template('create_account.html')

            if len(password) < 8:
                flash("Minimum 8 character password is required.", "error")
                return render_template('create_account.html')

            if db_manager.user_exists(user):
                flash("Username already taken.", "error")
                return render_template('create_account.html')
            if db_manager.email_exists(email):
                flash("Email already registered.", "error")
                return render_template('create_account.html')

            hashed = generate_password_hash(password)
            response = db_manager.add_user(user, email, hashed)
            if response:
                flash("Account created successfully", "success")
                return redirect(url_for("login"))

            flash("Something went wrong. Try again.", "error")
            return render_template('create_account.html')

        except Exception as e:
            print(f"Error: {e}")
            flash("Something went wrong. Try again.")
            return render_template('create_account.html')

    return render_template('create_account.html')


@app.route('/search', methods=['GET'])
def search_champion():
    search = request.args.get('q', '').strip().lower()

    if not search:
        return jsonify([])

    suggestions = db_manager.search_champions(search)
    return jsonify(suggestions)


@app.route('/champions')
def champions():
    return render_template('champions.html')


@app.route('/champion/<name>')
def champion_page(name):
    try:
        champ = Champion(name)
        if champ is None:
            flash(f"Champion data not found for {name}", "error")
            return redirect(url_for('champions'))

        recommender = BuildRecommender(champ)
        start, core, situational = recommender.recommend_items()
        spell1, spell2 = recommender.recommend_spells()
        primary_tree, primary_runes, secondary_tree, secondary_runes = recommender.recommend_runes()
        skill_order, stats = recommender.skill_priority, recommender.stat_shards

        return render_template('champion.html', champion=champ, version=champ.version, starting_items=start, core_items=core,
                situational_items=situational, spell_1=spell1, spell_2=spell2, skill_priority=skill_order, stat_shards=stats, runes_primary_tree=primary_tree,
                runes_primary_runes=primary_runes, runes_secondary_tree=secondary_tree, runes_secondary_runes=secondary_runes)

    except Exception as e:
        print(f"Error loading champion data for {name}: {e}")
        flash(f"Error loading champion data for {name}", "error")
        return render_template('champions.html')


@app.route('/save', methods=['POST'])
def save_build():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))

        champ_name = request.form['champion_name']
        response = db_manager.save_champ_build(champ_name, session['user'])
        if response:
            flash("Build saved successfully.", "success")
            return redirect(url_for('profile'))
        flash("Failed to save build", "error")
        return redirect(url_for('champion_page'))

    except Exception as e:
        print(f"Error saving build: {e}")
        flash("Unexpected error occurred. Try again", "error")
        return redirect(url_for('champion_page'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)