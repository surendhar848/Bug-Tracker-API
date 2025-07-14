from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bug_tracker.db'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin, developer, tester

# Bug Model
class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')  # open, in_progress, resolved
    priority = db.Column(db.String(50), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return "Bug Tracker API is Running!"

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"})

@app.route('/bugs', methods=['POST'])
def report_bug():
    data = request.json
    bug = Bug(**data)
    db.session.add(bug)
    db.session.commit()
    return jsonify({"message": "Bug reported"})

@app.route('/bugs', methods=['GET'])
def get_bugs():
    status = request.args.get('status')
    query = Bug.query
    if status:
        query = query.filter_by(status=status)
    bugs = query.all()
    return jsonify([{
        'id': b.id, 'title': b.title, 'status': b.status, 'priority': b.priority,
        'assigned_to': b.assigned_to, 'updated_at': b.updated_at
    } for b in bugs])

@app.route('/bugs/<int:id>/assign', methods=['PUT'])
def assign_bug(id):
    data = request.json
    bug = Bug.query.get(id)
    if not bug:
        return jsonify({"error": "Bug not found"}), 404
    bug.assigned_to = data.get('assigned_to')
    bug.status = 'in_progress'
    db.session.commit()
    return jsonify({"message": "Bug assigned"})

@app.route('/bugs/<int:bug_id>/comments', methods=['POST'])
def add_comment(bug_id):
    data = request.json
    comment = Comment(bug_id=bug_id, user_id=data['user_id'], text=data['text'])
    db.session.add(comment)
    db.session.commit()
    return jsonify({"message": "Comment added"})

@app.route('/bugs/<int:bug_id>/comments', methods=['GET'])
def get_comments(bug_id):
    comments = Comment.query.filter_by(bug_id=bug_id).all()
    return jsonify([{
        'user_id': c.user_id, 'text': c.text, 'created_at': c.created_at
    } for c in comments])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
