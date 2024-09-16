import os
from flask import Flask
from flask_cors import CORS
import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 獲取允許的源
allowed_origins = [
    "http://localhost:3000",  # 本地開發
    "https://21-day-date-front.vercel.app/",  # 您的 React 應用部署 URL
    os.environ.get("REACT_APP_URL", "")  # 從環境變量獲取
]

# 移除列表中的空字符串
allowed_origins = [origin for origin in allowed_origins if origin]

# 設置 CORS
CORS(app, resources={r"/*": {
    "origins": [
        "https://21-day-date-front.vercel.app",  # Vercel 前端 URL
        "http://localhost:3000"  # 本地開發 URL
    ],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# SQLAlchemy 設置
sa.__version__  # 這行可以保留，用於版本檢查

# 使用環境變量或默認值設置數據庫 URI
database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)