
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    # Register authentication routes
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Register account routes
    from app.routes.accounts import accounts_bp
    app.register_blueprint(accounts_bp)

    from app.routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    # Home route
    @app.route("/")
    def home():
        return {
            "message": "LedgerLine Backend is running!",
            "status": "healthy"
        }

    # Health check
    @app.route("/api/health")
    def health():
        return {"status": "healthy"}

    # Database check
    @app.route("/api/db-check")
    def db_check():
        try:
            from sqlalchemy import text

            with db.engine.connect() as connection:
                result = connection.execute(
                    text("SELECT current_database()")
                ).scalar()

            return {
                "status": "connected",
                "database": result
            }

        except Exception:
            return {
                "status": "error",
                "message": "Database connection failed"
            }, 500

    # Initialize database tables
    with app.app_context():
        from app import models
        db.create_all()

    return app
