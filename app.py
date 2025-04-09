from flask import Flask
from config import Config
from models import db
from routes.books import books_bp
from routes.students import students_bp
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager  

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


jwt = JWTManager(app)

@app.route('/')
def index():
    return 'Bienvenue sur l\'API Flask!'

with app.app_context():
    db.create_all()

app.register_blueprint(books_bp)
app.register_blueprint(students_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
