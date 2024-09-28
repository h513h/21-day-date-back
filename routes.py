from flask import request, jsonify
from app import app, db
from models import User, DailyList, WeeklyList, CompletedTask, TodoList
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is up and running!'}), 200

@app.route('/create_user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 200

def handle_login_options():
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500
    
@app.route('/user/<username>', methods=['DELETE'])
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        # 刪除與用戶相關的所有數據
        DailyList.query.filter_by(user_id=user.id).delete()
        WeeklyList.query.filter_by(user_id=user.id).delete()
        CompletedTask.query.filter_by(user_id=user.id).delete()
        TodoList.query.filter_by(user_id=user.id).delete()
        
        # 刪除用戶
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User and all associated data deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/user', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([{'username': user.username} for user in users])

@app.route('/<username>/daily_list', methods=['GET'])
def get_daily_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    daily_list = DailyList.query.filter_by(user_id=user.id).all()
    
    # 對每個 item 進行處理，確保 steps 是正確顯示的字串
    result = []
    for item in daily_list:
        # 確保 steps 是字串類型，並去除多餘的轉義符號
        steps = item.steps if isinstance(item.steps, str) else str(item.steps)
        steps = steps.encode('utf-8').decode('unicode_escape')  # 處理多餘的轉義符號
        
        # 加入處理後的資料到結果列表
        result.append({
            'title': item.title,
            'steps': steps,
            'time': item.time
        })
    
    return jsonify(result)
    
@app.route('/<username>/daily_list', methods=['POST'])
def add_daily_list(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first_or_404()
    new_item = DailyList(title=data['title'], time=data['time'], user_id=user.id)
    new_item.steps_list = data['steps']
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Daily list item added'})

@app.route('/<username>/daily_list/<int:item_id>', methods=['DELETE'])
def delete_daily_list(username, item_id):
    user = User.query.filter_by(username=username).first_or_404()
    item = DailyList.query.filter_by(id=item_id, user_id=user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Daily list item deleted'})

@app.route('/<username>/weekly_list', methods=['GET'])
def get_weekly_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    weekly_list = WeeklyList.query.filter_by(user_id=user.id).all()
    
    # 對每個 item 進行處理，確保 steps 是正確顯示的字串
    result = []
    for item in weekly_list:
        # 確保 steps 是字串類型，並去除多餘的轉義符號
        steps = item.steps if isinstance(item.steps, str) else str(item.steps)
        steps = steps.encode('utf-8').decode('unicode_escape')  # 處理多餘的轉義符號
        
        # 加入處理後的資料到結果列表
        result.append({
            'title': item.title,
            'steps': steps,
            'time': item.time
        })
    
    return jsonify(result)
    
@app.route('/<username>/weekly_list', methods=['POST'])
def add_weekly_list(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first_or_404()
    new_item = WeeklyList(title=data['title'], time=data['time'], user_id=user.id)
    new_item.steps_list = data['steps']
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Weekly list item added'})

@app.route('/<username>/weekly_list/<int:item_id>', methods=['DELETE'])
def delete_weekly_list(username, item_id):
    user = User.query.filter_by(username=username).first_or_404()
    item = WeeklyList.query.filter_by(id=item_id, user_id=user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Weekly list item deleted'})

@app.route('/<username>/completed_tasks', methods=['GET'])
def get_completed_tasks(username):
    user = User.query.filter_by(username=username).first_or_404()
    completed_tasks = CompletedTask.query.filter_by(user_id=user.id).all()
    return jsonify([{'photo': task.photo, 'comment1': task.comment1, 'comment2': task.comment2, 'title': task.title, 'date': task.date} for task in completed_tasks])

@app.route('/<username>/completed_tasks', methods=['POST'])
def add_completed_task(username):
    data = request.get_json()
    user = User.query.filter_by(username=username).first_or_404()
    new_task = CompletedTask(photo=data['photo'], comment1=data['comment1'], comment2=data['comment2'], title=data['title'], date=data['date'], user_id=user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Completed task added'})

@app.route('/<username>/completed_tasks/<int:task_id>', methods=['DELETE'])
def delete_completed_task(username, task_id):
    user = User.query.filter_by(username=username).first_or_404()
    task = CompletedTask.query.filter_by(id=task_id, user_id=user.id).first()

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'})

def serialize_list_item(item):
    return {
        'title': item.title,
        'steps': json.loads(item.steps),
        'time': item.time
    }

@app.route('/<username>/generate_todo_list', methods=['POST'])
def generate_todo_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    daily_items = DailyList.query.filter_by(user_id=user.id).all()
    weekly_items = WeeklyList.query.filter_by(user_id=user.id).all()
    
    if len(daily_items) < 6 or len(weekly_items) < 4:
        return jsonify({'message': 'Not enough items in daily or weekly lists'}), 400
    
    selected_daily = random.sample(daily_items, 6)
    selected_weekly = random.sample(weekly_items, 3)
    
    todo_items = selected_daily + selected_weekly
    random.shuffle(todo_items)
    
    # 清除現有的 TodoList 項目
    TodoList.query.filter_by(user_id=user.id).delete()
    
    for item in todo_items:
        content = json.dumps(serialize_list_item(item))
        list_type = 'daily' if isinstance(item, DailyList) else 'weekly'
        new_todo = TodoList(content=content, user_id=user.id, list_type=list_type)
        db.session.add(new_todo)
    
    db.session.commit()
    
    return jsonify({'message': 'New todo list generated successfully'})

@app.route('/<username>/edit_todo_item/<int:item_id>', methods=['PUT'])
def edit_todo_item(username, item_id):
    user = User.query.filter_by(username=username).first_or_404()
    todo_item = TodoList.query.filter_by(id=item_id, user_id=user.id).first_or_404()
    
    if todo_item.list_type == 'daily':
        available_items = DailyList.query.filter_by(user_id=user.id).all()
    else:
        available_items = WeeklyList.query.filter_by(user_id=user.id).all()
    
    current_content = json.loads(todo_item.content)
    available_items = [item for item in available_items if serialize_list_item(item) != current_content]
    
    if not available_items:
        return jsonify({'message': 'No available items to replace with'}), 400
    
    new_item = random.choice(available_items)
    todo_item.content = json.dumps(serialize_list_item(new_item))
    
    db.session.commit()
    
    new_item = random.choice(available_items)
    todo_item.content = json.dumps(serialize_list_item(new_item))
    
    db.session.commit()
    
    steps = new_item.steps if isinstance(new_item.steps, str) else str(new_item.steps)
    steps = steps.encode('utf-8').decode('unicode_escape')

    return jsonify({
        'steps': steps,
        'time': new_item.time,
        'title': new_item.title,
        'id': item_id
    })
    
@app.route('/<username>/todo_list/<int:item_id>', methods=['PUT'])
def update_todo_item(username, item_id):
    user = User.query.filter_by(username=username).first_or_404()
    todo_item = TodoList.query.filter_by(id=item_id, user_id=user.id).first_or_404()

    data = request.get_json()
    new_status = data.get('status', 'yet') # 預設為 'yet'

    if new_status not in ['yet', 'processing', 'done']:
        return jsonify({'message': 'Invalid status. Status must be "yet", "processing", or "done"'}), 400

    todo_item.done = new_status
    db.session.commit()

    return jsonify({
        'id': todo_item.id,
        'content': json.loads(todo_item.content),
        'done': todo_item.done,
        'list_type': todo_item.list_type
    })
    
@app.route('/<username>/todo_list', methods=['GET'])
def get_todo_list(username):
    user = User.query.filter_by(username=username).first_or_404()
    todo_list = TodoList.query.filter_by(user_id=user.id).all()
    return jsonify([{
        'id': item.id,
        'content': json.loads(item.content),
        'done': item.done,
        'list_type': item.list_type
    } for item in todo_list])

@app.route('/<username>/todo_list/<int:item_id>', methods=['DELETE'])
def delete_todo_item(username, item_id):
    user = User.query.filter_by(username=username).first_or_404()
    item = TodoList.query.filter_by(id=item_id, user_id=user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Todo item deleted'})

@app.route('/admin/aJ2x9B4nK7/all_data', methods=['GET'])
def get_all_data():
    all_data = {}

    # 獲取所有用戶
    users = User.query.all()

    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'password': user.password,  # 注意：這是哈希後的密碼
            'todo_list': [],
            'completed_tasks': []
        }

        # 獲取用戶的待辦清單
        todo_items = TodoList.query.filter_by(user_id=user.id).all()
        for item in todo_items:
            content = json.loads(item.content)
            user_data['todo_list'].append({
                'id': item.id,
                'title': content['title'],
                'steps': content['steps'],
                'time': content['time'],
                'done': item.done,
                'list_type': item.list_type
            })

        # 獲取用戶的已完成任務
        completed_tasks = CompletedTask.query.filter_by(user_id=user.id).all()
        for task in completed_tasks:
            user_data['completed_tasks'].append({
                'id': task.id,
                'photo': task.photo,
                'comment1': task.comment1,
                'comment2': task.comment2,
                'title': task.title,
                'date': task.date
            })

        all_data[user.username] = user_data

    return jsonify(all_data)