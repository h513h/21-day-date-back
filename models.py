from app import db
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    daily_list = db.relationship('DailyList', backref='user', lazy=True)
    weekly_list = db.relationship('WeeklyList', backref='user', lazy=True)
    completed_tasks = db.relationship('CompletedTask', backref='user', lazy=True)
    todo_list = db.relationship('TodoList', backref='user', lazy=True)

class DailyList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    steps = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def steps_list(self):
        return json.loads(self.steps)

    @steps_list.setter
    def steps_list(self, value):
        self.steps = json.dumps(value)

class WeeklyList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    steps = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def steps_list(self):
        return json.loads(self.steps)

    @steps_list.setter
    def steps_list(self, value):
        self.steps = json.dumps(value)

class CompletedTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(255))
    comment1 = db.Column(db.String(255))
    comment2 = db.Column(db.String(255))
    title = db.Column(db.String(255))
    date = db.Column(db.String(255))
    user_id = db.Column(db.String(255), db.ForeignKey('user.username'))

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 改為 Text 類型以存儲更多信息
    done = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    list_type = db.Column(db.String(10), nullable=False)  # 'daily' 或 'weekly'