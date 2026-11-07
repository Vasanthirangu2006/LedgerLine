
import pytest

from config import Config
from app import create_app, db


@pytest.fixture()
def app():
    # Never allow automated tests to use the real banking database.
    test_url = Config.SQLALCHEMY_DATABASE_URI.set(
        database="ledgerline_test_db"
    )

    if test_url.database != "ledgerline_test_db":
        raise RuntimeError("Unsafe test database configuration")

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_url,
        "JWT_SECRET_KEY": "ledgerline-automated-testing-secret-key-2026",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
