
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config


db = SQLAlchemy()
jwt = JWTManager()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Allow tests to use a separate database and test settings.
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.accounts import accounts_bp
    app.register_blueprint(accounts_bp)

    from app.routes.transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    @app.route("/")
    def home():
        return {
            "message": "LedgerLine Backend is running!",
            "status": "healthy"
        }

    @app.route("/api/health")
    def health():
        return {"status": "healthy"}

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

    with app.app_context():
        from app import models
        db.create_all()

    return app
