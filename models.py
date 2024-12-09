
from extensions import db
from flask import jsonify
from sqlalchemy import text

class DatabaseModel:
    @staticmethod
    def init_db():
        """
        Initialize all database tables using raw SQL scripts
        """
        # Table creation statements
        table_creation_statements = [
            '''
            CREATE TABLE IF NOT EXISTS `Task` (
                `taskId` INT PRIMARY KEY AUTO_INCREMENT,
                `name` VARCHAR(255),
                `description` TEXT,
                `points` INT,
                `image_url` TEXT
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS `User` (
                `userId` INT PRIMARY KEY AUTO_INCREMENT,
                `username` VARCHAR(50),
                `email` VARCHAR(100)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS `TaskProgress` (
                `progressId` INT PRIMARY KEY AUTO_INCREMENT,
                `userId` INT NOT NULL,
                `taskId` INT NOT NULL,
                `completion_date` TIMESTAMP,
                `notes` TEXT,
                FOREIGN KEY (`userId`) REFERENCES `User`(`userId`),
                FOREIGN KEY (`taskId`) REFERENCES `Task`(`taskId`)
            )
            '''
        ]
        
        # Execute each table creation statement
        with db.engine.connect() as connection:
            for statement in table_creation_statements:
                try:
                    connection.execute(text(statement))
                except Exception as e:
                    print(f"Error creating table: {e}")
                    # Optionally, we can re-raise the exception if we want to stop execution
                    # raise

    @staticmethod
    def insert_initial_data():
        """
        Insert initial data for all tables
        """
        # Initial tasks data
        initial_tasks_sql = text('''
        INSERT IGNORE INTO `Task` (taskId, name, description, points, image_url) VALUES
        (1, 'Get groceries', 'Get weekly groceries from supermarket', 10, 'https://live.staticflickr.com/7238/7259669024_61fc5a98f6_b.jpg'),
        (2, 'Exercise', 'Go to the gym for a one hour work out', 50, 'https://live.staticflickr.com/3329/3210745877_4feb7cd118_b.jpg'),
        (3, 'Finish report', 'Complete the progress report before it is due end of the month', 40, 'https://live.staticflickr.com/3400/4566115233_b2471d4de7_b.jpg'),
        (4, 'Book hotel', 'Book the accommodation for the upcoming trip.', 30, 'https://live.staticflickr.com/3255/2313201182_53b64e6633_b.jpg'),
        (5, 'Reserve dinner', 'Make dinner reservation for birthday', 30, 'https://live.staticflickr.com/2365/1908487131_7ae755a70d_b.jpg')
        ''')

        # Initial users data
        initial_users_sql = text('''
        INSERT IGNORE INTO `User` (userId, username, email) VALUES
        (1, 'john_doe', 'john.doe@example.com'),
        (2, 'jane_smith', 'jane.smith@example.com')
        ''')

        # Initial task progress data
        initial_task_progress_sql = text('''
        INSERT IGNORE INTO `TaskProgress` (progressId, userId, taskId, completion_date, notes) VALUES
        (1, 1, 1, CURRENT_TIMESTAMP, 'Completed grocery shopping'),
        (2, 2, 2, CURRENT_TIMESTAMP, 'Gym session completed')
        ''')
        
        # Execute the SQL scripts to insert initial data
        with db.engine.connect() as connection:
            try:
                connection.execute(initial_tasks_sql)
                connection.execute(initial_users_sql)
                connection.execute(initial_task_progress_sql)
                connection.commit()
            except Exception as e:
                print(f"Error inserting initial data: {e}")
                connection.rollback()

class TaskModel:
    @staticmethod
    def create_task(data):
        """
        Create a new task
        
        :param data: Dictionary containing task details
        :return: Tuple of (task details, status code)
        """
        # Validate request body
        if not all(key in data for key in ['name', 'description', 'points', 'image_url']):
            return {"error": "Missing required fields"}, 400

        # Prepare SQL query
        insert_query = '''
        INSERT INTO Task (name, description, points, image_url) 
        VALUES (%(name)s, %(description)s, %(points)s, %(image_url)s)
        '''

        try:
            # Execute the insert query
            with db.engine.connect() as connection:
                result = connection.execute(insert_query, data)
                
                # Get the newly created task ID
                task_id = result.lastrowid

            # Fetch the newly created task
            select_query = 'SELECT * FROM Task WHERE taskId = %(task_id)s'
            with db.engine.connect() as connection:
                task = connection.execute(select_query, {'task_id': task_id}).fetchone()

            return {
                'taskId': task_id,
                'name': task['name'],
                'description': task['description'],
                'points': task['points'],
                'image_url': task['image_url']
            }, 201

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def update_task(taskId, data):
        """
        Update an existing task
        
        :param taskId: ID of the task to update
        :param data: Dictionary containing updated task details
        :return: Tuple of (updated task details, status code)
        """
        # Validate request body
        if not all(key in data for key in ['name', 'description', 'points', 'image_url']):
            return {"error": "Missing required fields"}, 400

        # First, check if task exists
        check_query = 'SELECT * FROM Task WHERE taskId = %(task_id)s'
        with db.engine.connect() as connection:
            existing_task = connection.execute(check_query, {'task_id': taskId}).fetchone()

        if not existing_task:
            return {"error": "Task not found"}, 404

        # Prepare SQL update query
        update_query = '''
        UPDATE Task 
        SET name = %(name)s, 
            description = %(description)s, 
            points = %(points)s, 
            image_url = %(image_url)s 
        WHERE taskId = %(task_id)s
        '''

        # Add taskId to the data dictionary
        data['task_id'] = taskId

        try:
            with db.engine.connect() as connection:
                connection.execute(update_query, data)

            # Fetch the updated task
            select_query = 'SELECT * FROM Task WHERE taskId = %(task_id)s'
            with db.engine.connect() as connection:
                updated_task = connection.execute(select_query, {'task_id': taskId}).fetchone()

            return {
                'taskId': updated_task['taskId'],
                'name': updated_task['name'],
                'description': updated_task['description'],
                'points': updated_task['points'],
                'image_url': updated_task['image_url']
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_all_tasks():
        """
        Retrieve all tasks
        
        :return: Tuple of (list of tasks, status code)
        """
        try:
            select_query = 'SELECT * FROM Task'
            with db.engine.connect() as connection:
                tasks = connection.execute(select_query).fetchall()

            # Convert tasks to list of dictionaries
            task_list = [{
                'taskId': task['taskId'],
                'name': task['name'],
                'description': task['description'],
                'points': task['points'],
                'image_url': task['image_url']
            } for task in tasks]

            return task_list, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def delete_task(taskId):
        """
        Delete a task by its ID
        
        :param taskId: ID of the task to delete
        :return: Tuple of (result message, status code)
        """
        # First, check if task exists
        check_query = 'SELECT * FROM Task WHERE taskId = %(task_id)s'
        with db.engine.connect() as connection:
            existing_task = connection.execute(check_query, {'task_id': taskId}).fetchone()

        if not existing_task:
            return {"error": "Task not found"}, 404

        # Prepare delete query
        delete_query = 'DELETE FROM Task WHERE taskId = %(task_id)s'

        try:
            with db.engine.connect() as connection:
                connection.execute(delete_query, {'task_id': taskId})

            return {"message": f"Task {taskId} successfully deleted"}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_task_with_progress(taskId):
        """
        Retrieve a task with its progress details
        """
        query = '''
        SELECT t.*, tp.progressId, tp.userId, tp.completion_date, tp.notes, 
               u.username, u.email
        FROM Task t
        LEFT JOIN TaskProgress tp ON t.taskId = tp.taskId
        LEFT JOIN User u ON tp.userId = u.userId
        WHERE t.taskId = %(task_id)s
        '''

        try:
            with db.engine.connect() as connection:
                result = connection.execute(query, {'task_id': taskId}).fetchone()

            if not result:
                return {"error": "Task not found"}, 404

            return {
                'task': {
                    'taskId': result['taskId'],
                    'name': result['name'],
                    'description': result['description'],
                    'points': result['points'],
                    'image_url': result['image_url']
                },
                'progress': {
                    'progressId': result['progressId'],
                    'userId': result['userId'],
                    'username': result['username'],
                    'email': result['email'],
                    'completion_date': str(result['completion_date']) if result['completion_date'] else None,
                    'notes': result['notes']
                }
            }, 200

        except Exception as e:
            return {"error": str(e)}, 500
