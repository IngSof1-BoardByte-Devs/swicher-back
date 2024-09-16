from app.database.session import config_database
from app.database.session import db
import pytest

@pytest.fixture(scope="module")
def setup_database():
    config_database(test=True)

    # Remove the 'with db_session()' lines
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

    yield

    db.drop_all_tables(with_all_data=True)