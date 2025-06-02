import pytest
import sqlite3
import os
import tempfile
from app import app, get_db
import json
from typing import List, Dict, Any, Optional, Generator
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.wrappers import Response as WerkzeugResponse


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    """Create a test client with a temp database."""
    db_fd: int
    db_path: str
    db_fd, db_path = tempfile.mkstemp()
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    flask_app: Flask = app

    with flask_app.test_client() as current_client:
        with flask_app.app_context():
            app.test_cli_runner().invoke(args=["init-db"])
        yield current_client

    os.close(db_fd)
    os.unlink(flask_app.config["DATABASE"])


@pytest.fixture
def sample_jobs() -> List[Dict[str, str]]:
    """Sample job data for testing."""
    return [
        {"company": "Amazon", "position": "Full Stack Developer", "status": "Declined"},
        {"company": "Google", "position": "Software Engineer", "status": "Applied"},
        {"company": "Microsoft", "position": "Data Analyst", "status": "Interviewed"},
    ]


class TestJobAdding:
    """Test job adding functionality."""

    def test_add_job_success(self, client: FlaskClient) -> None:
        """Test successfully adding a new job."""
        response: WerkzeugResponse = client.post(
            "/add",
            data={
                "company": "Google",
                "position": "Software Engineer",
                "status": "Applied",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Job application added successfully!" in response.data
        assert b"Google" in response.data
        assert b"Software Engineer" in response.data

    def test_add_job_missing_company(self, client: FlaskClient) -> None:
        """Test adding job with missing company fails."""
        response: WerkzeugResponse = client.post(
            "/add",
            data={"company": "", "position": "Software Engineer", "status": "Applied"},
        )

        assert response.status_code == 200
        assert b"Company and position are required!" in response.data

    def test_add_job_missing_position(self, client: FlaskClient) -> None:
        """Test adding job with missing position fails."""
        response: WerkzeugResponse = client.post(
            "/add", data={"company": "Google", "position": "", "status": "Applied"}
        )

        assert response.status_code == 200
        assert b"Company and position are required!" in response.data


class TestJobEditing:
    """Test job editing functionality."""

    def add_test_job(
        self,
        client: FlaskClient,
        company: str = "Google",
        position: str = "Software Engineer",
        status: str = "Applied",
    ) -> Optional[int]:
        """Helper method to add a test job directly to the database and return its ID."""
        flask_app: Flask = app
        with flask_app.app_context():
            db: sqlite3.Connection = get_db()
            db.execute(
                "INSERT INTO jobs (company, position, status) VALUES (?, ?, ?)",
                (company, position, status),
            )
            db.commit()
            cursor: sqlite3.Cursor = db.execute(
                "SELECT id FROM jobs WHERE company = ? AND position = ?",
                (company, position),
            )
            job: Optional[sqlite3.Row] = cursor.fetchone()
            return job["id"] if job else None

    def test_edit_job_success(self, client: FlaskClient) -> None:
        """Test successfully editing a job."""
        job_id: Optional[int] = self.add_test_job(client)
        assert job_id is not None

        response: WerkzeugResponse = client.post(
            f"/{job_id}/edit",
            data={
                "company": "Microsoft",
                "position": "Senior Software Engineer",
                "status": "Interviewed",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        print(f"Response data for edit_job: {response.data.decode()}")
        assert b"Job application updated successfully!" in response.data
        assert b"Microsoft" in response.data
        assert b"Senior Software Engi..." in response.data


class TestJobDeletion:
    """Test job deletion functionality."""

    def add_test_job(
        self,
        client: FlaskClient,
        company: str = "Meta",
        position: str = "Test Engineer",
        status: str = "Applied",
    ) -> Optional[int]:
        """Helper method to add a test job directly to the database and return its ID."""
        flask_app: Flask = app
        with flask_app.app_context():
            db: sqlite3.Connection = get_db()
            db.execute(
                "INSERT INTO jobs (company, position, status) VALUES (?, ?, ?)",
                (company, position, status),
            )
            db.commit()
            cursor: sqlite3.Cursor = db.execute(
                "SELECT id FROM jobs WHERE company = ? AND position = ?",
                (company, position),
            )
            job: Optional[sqlite3.Row] = cursor.fetchone()
            return job["id"] if job else None

    def test_delete_job_success(self, client: FlaskClient) -> None:
        """Test successfully deleting a job."""
        job_id: Optional[int] = self.add_test_job(client)
        assert job_id is not None

        response: WerkzeugResponse = client.post(
            f"/{job_id}/delete", follow_redirects=True
        )

        assert response.status_code == 200
        print(f"Response data for delete_job: {response.data.decode()}")
        assert b"Job application deleted successfully!" in response.data
        assert b"Meta" not in response.data


class TestStatusUpdate:
    """Test AJAX status update functionality."""

    def add_test_job(
        self,
        client: FlaskClient,
        company: str = "Amazon",
        position: str = "Full Stack Developer",
        status: str = "Applied",
    ) -> Optional[int]:
        """Helper method to add a test job directly to the database and return its ID."""
        flask_app: Flask = app
        with flask_app.app_context():
            db: sqlite3.Connection = get_db()
            db.execute(
                "INSERT INTO jobs (company, position, status) VALUES (?, ?, ?)",
                (company, position, status),
            )
            db.commit()
            cursor: sqlite3.Cursor = db.execute(
                "SELECT id FROM jobs WHERE company = ? AND position = ?",
                (company, position),
            )
            job: Optional[sqlite3.Row] = cursor.fetchone()
            return job["id"] if job else None

    def test_update_status_success(self, client: FlaskClient) -> None:
        """Test successfully updating job status via AJAX."""
        job_id: Optional[int] = self.add_test_job(client)
        assert job_id is not None

        response: WerkzeugResponse = client.post(
            f"/update_status/{job_id}",
            json={"status": "Interviewed"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data: Dict[str, Any] = json.loads(response.data)
        assert data["message"] == "Status updated successfully"

        flask_app: Flask = app
        with flask_app.app_context():
            db: sqlite3.Connection = get_db()
            cursor: sqlite3.Cursor = db.execute(
                "SELECT status FROM jobs WHERE id = ?", (job_id,)
            )
            job: Optional[sqlite3.Row] = cursor.fetchone()
            assert job is not None
            assert job["status"] == "Interviewed"


class TestFiltering:
    """Test job filtering and sorting functionality."""

    def add_sample_jobs(
        self, client: FlaskClient, sample_jobs_data: List[Dict[str, str]]
    ) -> None:
        """Add sample jobs for filtering tests."""
        for job in sample_jobs_data:
            client.post("/add", data=job)

    def test_filter_by_status(
        self, client: FlaskClient, sample_jobs: List[Dict[str, str]]
    ) -> None:
        """Test filtering jobs by status."""
        self.add_sample_jobs(client, sample_jobs)

        response: WerkzeugResponse = client.get("/?status=Applied")
        assert response.status_code == 200
        assert b"Google" in response.data
        assert b"Microsoft" not in response.data

        response = client.get("/?status=Interviewed")
        assert response.status_code == 200
        assert b"Microsoft" in response.data
        assert b"Google" not in response.data

    def test_sorting(
        self, client: FlaskClient, sample_jobs: List[Dict[str, str]]
    ) -> None:
        """Test sorting jobs."""
        self.add_sample_jobs(client, sample_jobs)

        response: WerkzeugResponse = client.get("/?sort=company&order=asc")
        assert response.status_code == 200
        content: str = response.data.decode()

        amazon_position: int = content.find("Amazon")
        google_position: int = content.find("Google")
        assert amazon_position != -1
        assert google_position != -1
        assert amazon_position < google_position


if __name__ == "__main__":
    pytest.main(["-v", "--tb=short", __file__])
