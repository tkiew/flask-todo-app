from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Todo {self.title}>'

@app.route('/')
def index():
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    description = request.form.get('description')
    
    if not title:
        flash('Title is required!', 'error')
        return redirect(url_for('index'))
    
    new_todo = Todo(title=title, description=description)
    db.session.add(new_todo)
    db.session.commit()
    
    flash('Todo added successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
def complete(id):
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    
    status = 'completed' if todo.completed else 'uncompleted'
    flash(f'Todo marked as {status}!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    todo = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.description = request.form.get('description')
        
        if not todo.title:
            flash('Title is required!', 'error')
            return render_template('edit.html', todo=todo)
        
        db.session.commit()
        flash('Todo updated successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', todo=todo)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 