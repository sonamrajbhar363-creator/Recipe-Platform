import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

# --- HOME PAGE ---
@app.route('/')
def index():
    search_query = request.args.get('search')
    conn = get_db_connection()
    
    # 1. Fetch Trending Recipes
    trending = conn.execute("SELECT * FROM recipes WHERE status = 'approved' AND is_trending = 1").fetchall()
    
    # 2. Fetch User's Personal Recipes (if logged in)
    my_recipes = []
    if 'user_id' in session:
        my_recipes = conn.execute("SELECT * FROM recipes WHERE user_id = ?", (session['user_id'],)).fetchall()
    
    # 3. Fetch General Recipes
    if search_query:
        recipes = conn.execute("SELECT * FROM recipes WHERE status = 'approved' AND title LIKE ?", 
                               ('%' + search_query + '%',)).fetchall()
    else:
        recipes = conn.execute("SELECT * FROM recipes WHERE status = 'approved' AND is_trending = 0").fetchall()
        
    conn.close()
    return render_template('index.html', recipes=recipes, trending=trending, my_recipes=my_recipes)

# --- AUTHENTICATION (Login/Register) ---
@app.route('/register', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # PASSWORD HASHING: Plain text ko secure hash mein convert karna
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                         (username, hashed_password, 'user'))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # CHECK PASSWORD: Kya plain password hashed password se match karta hai?
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            return "Invalid username or password!"
    return render_template('login.html')

# --- YOU NEED THIS ROUTE FOR THE REDIRECT TO WORK ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    # Sirf us user ki recipes fetch karein jo login hai
    user_recipes = conn.execute('SELECT * FROM recipes WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', recipes=user_recipes)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- RECIPE MANAGEMENT ---
@app.route('/recipe/<int:id>')
def recipe_detail(id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('detail.html', recipe=recipe)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        image_url = request.form['image_url']
        user_id = session['user_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO recipes (title, ingredients, instructions, image_url, status, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, ingredients, instructions, image_url, 'pending', user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    if 'user_id' not in session: 
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    
    # SECURITY: Check if the logged-in user is actually the owner
    if recipe['user_id'] != session['user_id']:
        conn.close()
        return "Unauthorized! You can only edit your own recipes.", 403

    if request.method == 'POST':
        conn.execute('UPDATE recipes SET title=?, ingredients=?, instructions=?, image_url=? WHERE id=?',
                     (request.form['title'], request.form['ingredients'], request.form['instructions'], request.form['image_url'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    conn.close()
    return render_template('edit.html', recipe=recipe)

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    # Redirect back to index with the hash so it opens 'Your Kitchen' tab
    return redirect(url_for('index') + '#my-kitchen')

# --- ADMIN ROUTES ---
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied", 403
        
    conn = get_db_connection()
    
    # We join recipes with users to get the username of the person who posted it
    query = '''
        SELECT recipes.*, users.username 
        FROM recipes 
        JOIN users ON recipes.user_id = users.id 
        WHERE recipes.status = 'pending'
    '''
    pending_recipes = conn.execute(query).fetchall()
    
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', recipes=pending_recipes, all_users=users)

@app.route('/approve/<int:id>', methods=['POST'])
def approve_recipe(id):
    if session.get('role') != 'admin': return "Unauthorized", 403
    conn = get_db_connection()
    conn.execute("UPDATE recipes SET status = 'approved' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

# --- ADD THESE TO YOUR ADMIN ROUTES SECTION ---

@app.route('/reject/<int:id>', methods=['POST'])
def reject_recipe(id):
    if session.get('role') != 'admin': return "Unauthorized", 403
    conn = get_db_connection()
    # Option A: Change status to rejected
    conn.execute("UPDATE recipes SET status = 'rejected' WHERE id = ?", (id,))
    # Option B: Or just delete it if you don't want to keep junk data
    # conn.execute("DELETE FROM recipes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if session.get('role') != 'admin': return "Unauthorized", 403
    conn = get_db_connection()
    # Delete the user's recipes first to avoid errors
    conn.execute("DELETE FROM recipes WHERE user_id = ?", (id,))
    # Then delete the user
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)