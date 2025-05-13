import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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
    return render_template('user_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')
        stored_hash = db_manager.get_pass(user)

        if stored_hash and check_password_hash(stored_hash, password):
            session['user'] = user
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid username or password.")

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
                return redirect(url_for("profile"))
            return render_template('user_page.html', error="Failed to update password.")

    return render_template('change_pass.html')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            user = request.form.get('username')
            password = request.form.get('password')

            if not email or not user or not password:
                return render_template('create_account.html', error="All fields are required.")

            if db_manager.user_exists(user):
                return render_template('create_account.html', error="Username already taken.")
            if db_manager.email_exists(email):
                return render_template('create_account.html', error="Email already registered.")

            hashed = generate_password_hash(password)
            response = db_manager.add_user(user, email, hashed)
            if response:
                return redirect(url_for("login"))

            return render_template('create_account.html', error="Something went wrong. Try again.")

        except Exception as e:
            print(f"Error: {e}")
            return render_template('create_account.html', error=f"Something went wrong. Try again.")

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
            return render_template('champions.html', error=f"Champion data not found for {name}")

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
        return render_template('champions.html', error=f"Error loading champion data for {name}")


@app.route('/save', methods=['POST'])
def save_build():
    try:
        if 'user' not in session:
            return redirect(url_for('login'))

        champ_name = request.form['champion_name']
        response = db_manager.save_champ_build(champ_name, session['user'])
        if response:
            return redirect(url_for('profile'))
        return redirect(url_for('champion_page', error="Failed to save build"))

    except Exception as e:
        print(f"Error saving build: {e}")
        return redirect(url_for('build_page', error="Unexpected error occurred"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)