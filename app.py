
from flask import Flask, request, jsonify
from extensions import db
from config import Config
from models import TaskModel, DatabaseModel
import pymysql

# Use pymysql as the MySQL connector
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

with app.app_context():
    DatabaseModel.init_db()
    DatabaseModel.insert_initial_data()

@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Endpoint to create a new task
    """
    result, status_code = TaskModel.create_task(request.json)
    return jsonify(result), status_code

@app.route('/tasks/<int:taskId>', methods=['PUT'])
def update_task(taskId):
    """
    Endpoint to update an existing task
    """
    result, status_code = TaskModel.update_task(taskId, request.json)
    return jsonify(result), status_code

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    """
    Endpoint to retrieve all tasks
    """
    result, status_code = TaskModel.get_all_tasks()
    return jsonify(result), status_code

@app.route('/tasks/<int:taskId>', methods=['DELETE'])
def delete_task(taskId):
    """
    Endpoint to delete a task
    """
    result, status_code = TaskModel.delete_task(taskId)
    return jsonify(result), status_code

@app.route('/tasks/<int:taskId>/progress', methods=['GET'])
def get_task_progress(taskId):
    """
    Endpoint to retrieve task progress details
    """
    result, status_code = TaskModel.get_task_with_progress(taskId)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True)
