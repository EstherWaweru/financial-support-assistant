import pathlib
import sys
from typing import Generator


import pytest

from app.db.session import SessionLocal

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from main import test_app as application
from app.api import deps


@pytest.fixture(scope="module")
def db() -> Generator:
    db_session = SessionLocal()

    def override_get_db() -> Generator:
        client_session = db_session
        yield client_session

    application.dependency_overrides[deps.get_db] = override_get_db

    yield db_session

    db_session.rollback()

    db_session.close()
