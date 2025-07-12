from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')

def get_db():
    conn = sqlite3.connect('skill_swap.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            if user['is_banned']:
                flash('Your account is banned', 'error')
                return render_template('login.html')
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('profile'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        name = request.form['name'].strip()
        location = request.form.get('location', '').strip()
        if not username or not password or not name:
            flash('Username, password, and name are required', 'error')
            return render_template('signup.html')
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password, name, location, is_admin, is_public) VALUES (?, ?, ?, ?, ?, ?)',
                        (username, generate_password_hash(password), name, location, 0, 1))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
        conn.close()
    return render_template('signup.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('login'))
    skills_offered = conn.execute('SELECT * FROM skills WHERE user_id = ? AND type = ?', (session['user_id'], 'offered')).fetchall()
    skills_wanted = conn.execute('SELECT * FROM skills WHERE user_id = ? AND type = ?', (session['user_id'], 'wanted')).fetchall()
    if request.method == 'POST':
        if 'update_profile' in request.form:
            name = request.form['name'].strip()
            location = request.form.get('location', '').strip()
            is_public = 1 if request.form.get('is_public') else 0
            availability = request.form['availability'].strip()
            if not name or not availability:
                flash('Name and availability are required', 'error')
            else:
                conn.execute('UPDATE users SET name = ?, location = ?, is_public = ?, availability = ? WHERE id = ?',
                            (name, location, is_public, availability, session['user_id']))
                conn.commit()
                flash('Profile updated successfully', 'success')
        elif 'add_skill' in request.form:
            skill = request.form['skill'].strip()
            skill_type = request.form['skill_type'].strip()
            if not skill:
                flash('Skill name is required', 'error')
            elif skill_type not in ['offered', 'wanted']:
                flash('Invalid skill type', 'error')
            else:
                conn.execute('INSERT INTO skills (user_id, skill, type) VALUES (?, ?, ?)', (session['user_id'], skill, skill_type))
                conn.commit()
                flash('Skill added successfully', 'success')
        elif 'delete_skill' in request.form:
            skill_id = request.form['skill_id']
            conn.execute('DELETE FROM skills WHERE id = ? AND user_id = ?', (skill_id, session['user_id']))
            conn.commit()
            flash('Skill deleted successfully', 'success')
    conn.close()
    return render_template('profile.html', user=user, skills_offered=skills_offered, skills_wanted=skills_wanted)

@app.route('/api/skills/offered', methods=['GET'])
def get_offered_skills():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    skills = conn.execute('SELECT id, skill FROM skills WHERE user_id = ? AND type = ?', (session['user_id'], 'offered')).fetchall()
    conn.close()
    return jsonify([{'id': skill['id'], 'skill': skill['skill']} for skill in skills])

@app.route('/browse')
def browse():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search = request.args.get('search', '').strip()
    conn = get_db()
    query = 'SELECT u.id, u.name, u.location, u.availability, s.id as skill_id, s.skill, s.type FROM users u JOIN skills s ON u.id = s.user_id WHERE u.is_public = 1 AND u.is_banned = 0 AND u.id != ?'
    params = [session['user_id']]
    if search:
        query += ' AND s.skill LIKE ?'
        params.append(f'%{search}%')
    users = conn.execute(query, params).fetchall()
    skills_offered = conn.execute('SELECT id, skill FROM skills WHERE user_id = ? AND type = ?', (session['user_id'], 'offered')).fetchall()
    conn.close()
    return render_template('browse.html', users=users, search=search, skills_offered=skills_offered)

@app.route('/swap', methods=['POST'])
def swap():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    action = request.form['action'].strip()
    conn = get_db()
    if action == 'request':
        requester_skill_id = request.form['requester_skill_id'].strip()
        receiver_id = request.form['receiver_id'].strip()
        receiver_skill_id = request.form['receiver_skill_id'].strip()
        if receiver_id == str(session['user_id']):
            flash('Cannot request a swap with yourself', 'error')
        elif not requester_skill_id or not receiver_id or not receiver_skill_id:
            flash('All fields are required for swap request', 'error')
        else:
            conn.execute('INSERT INTO swaps (requester_id, requester_skill_id, receiver_id, receiver_skill_id, status) VALUES (?, ?, ?, ?, ?)',
                        (session['user_id'], requester_skill_id, receiver_id, receiver_skill_id, 'pending'))
            conn.commit()
            flash('Swap request sent successfully', 'success')
    elif action == 'accept':
        swap_id = request.form['swap_id'].strip()
        swap = conn.execute('SELECT * FROM swaps WHERE id = ? AND receiver_id = ?', (swap_id, session['user_id'])).fetchone()
        if swap:
            conn.execute('UPDATE swaps SET status = ? WHERE id = ?', ('accepted', swap_id))
            conn.commit()
            flash('Swap accepted successfully', 'success')
        else:
            flash('Invalid or unauthorized swap', 'error')
    elif action == 'reject':
        swap_id = request.form['swap_id'].strip()
        swap = conn.execute('SELECT * FROM swaps WHERE id = ? AND receiver_id = ?', (swap_id, session['user_id'])).fetchone()
        if swap:
            conn.execute('UPDATE swaps SET status = ? WHERE id = ?', ('rejected', swap_id))
            conn.commit()
            flash('Swap rejected', 'success')
        else:
            flash('Invalid or unauthorized swap', 'error')
    elif action == 'delete':
        swap_id = request.form['swap_id'].strip()
        swap = conn.execute('SELECT * FROM swaps WHERE id = ? AND requester_id = ?', (swap_id, session['user_id'])).fetchone()
        if swap:
            conn.execute('DELETE FROM swaps WHERE id = ?', (swap_id,))
            conn.commit()
            flash('Swap request deleted successfully', 'success')
        else:
            flash('Invalid or unauthorized swap', 'error')
    elif action == 'feedback':
        swap_id = request.form['swap_id'].strip()
        rating = request.form['rating'].strip()
        comment = request.form['comment'].strip()
        swap = conn.execute('SELECT * FROM swaps WHERE id = ? AND (requester_id = ? OR receiver_id = ?)', (swap_id, session['user_id'], session['user_id'])).fetchone()
        if swap and swap['status'] == 'accepted':
            if not rating or int(rating) < 1 or int(rating) > 5:
                flash('Rating must be between 1 and 5', 'error')
            else:
                conn.execute('UPDATE swaps SET rating = ?, comment = ? WHERE id = ?', (rating, comment, swap_id))
                conn.commit()
                flash('Feedback submitted successfully', 'success')
        else:
            flash('Invalid or unauthorized swap', 'error')
    conn.close()
    return redirect(url_for('requests'))

@app.route('/requests')
def requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    pending_swaps = conn.execute('SELECT s.*, u1.name as requester_name, u2.name as receiver_name, s1.skill as requester_skill, s2.skill as receiver_skill FROM swaps s JOIN users u1 ON s.requester_id = u1.id JOIN users u2 ON s.receiver_id = u2.id JOIN skills s1 ON s.requester_skill_id = s1.id JOIN skills s2 ON s.receiver_skill_id = s2.id WHERE (s.requester_id = ? OR s.receiver_id = ?) AND s.status = ?', (session['user_id'], session['user_id'], 'pending')).fetchall()
    current_swaps = conn.execute('SELECT s.*, u1.name as requester_name, u2.name as receiver_name, s1.skill as requester_skill, s2.skill as receiver_skill FROM swaps s JOIN users u1 ON s.requester_id = u1.id JOIN users u2 ON s.receiver_id = u2.id JOIN skills s1 ON s.requester_skill_id = s1.id JOIN skills s2 ON s.receiver_skill_id = s2.id WHERE (s.requester_id = ? OR s.receiver_id = ?) AND s.status = ?', (session['user_id'], session['user_id'], 'accepted')).fetchall()
    conn.close()
    return render_template('requests.html', pending_swaps=pending_swaps, current_swaps=current_swaps)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    conn = get_db()
    if request.method == 'POST':
        action = request.form['action'].strip()
        if action == 'reject_skill':
            skill_id = request.form['skill_id'].strip()
            conn.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
            conn.commit()
            flash('Skill rejected successfully', 'success')
        elif action == 'ban_user':
            user_id = request.form['user_id'].strip()
            if user_id == str(session['user_id']):
                flash('Cannot ban yourself', 'error')
            else:
                conn.execute('UPDATE users SET is_banned = 1 WHERE id = ?', (user_id,))
                conn.commit()
                flash('User banned successfully', 'success')
        elif action == 'send_message':
            message = request.form['message'].strip()
            if not message:
                flash('Message cannot be empty', 'error')
            else:
                conn.execute('INSERT INTO messages (message, created_at) VALUES (?, ?)', (message, datetime.now()))
                conn.commit()
                flash('Message sent successfully', 'success')
    users = conn.execute('SELECT * FROM users WHERE is_banned = 0').fetchall()
    skills = conn.execute('SELECT s.*, u.name FROM skills s JOIN users u ON s.user_id = u.id').fetchall()
    swaps = conn.execute('SELECT s.*, u1.name as requester_name, u2.name as receiver_name FROM swaps s JOIN users u1 ON s.requester_id = u1.id JOIN users u2 ON s.receiver_id = u2.id').fetchall()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin.html', users=users, skills=skills, swaps=swaps, messages=messages)

@app.route('/admin/report')
def admin_report():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    users = conn.execute('SELECT * FROM users').fetchall()
    swaps = conn.execute('SELECT s.*, u1.name as requester_name, u2.name as receiver_name, s1.skill as requester_skill, s2.skill as receiver_skill FROM swaps s JOIN users u1 ON s.requester_id = u1.id JOIN users u2 ON s.receiver_id = u2.id JOIN skills s1 ON s.requester_skill_id = s1.id JOIN skills s2 ON s.receiver_skill_id = s2.id').fetchall()
    conn.close()
    report = "Skill Swap Platform Report\n\n"
    report += "Users:\n"
    for user in users:
        report += f"ID: {user['id']}, Username: {user['username']}, Name: {user['name']}, Banned: {user['is_banned']}\n"
    report += "\nSwaps:\n"
    for swap in swaps:
        report += f"ID: {swap['id']}, Requester: {swap['requester_name']}, Receiver: {swap['receiver_name']}, Status: {swap['status']}, Rating: {swap['rating'] or 'N/A'}, Comment: {swap['comment'] or 'N/A'}\n"
    return jsonify({'report': report})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)