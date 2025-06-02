import sqlite3
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    g,
    flash,
    abort,
    jsonify,
)
import click
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional, Any, Union
import pytz
from pytz import timezone

app = Flask(__name__)

load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY not set in .env file")

app.config["DATABASE"] = "database.db"

APP_TIMEZONE = os.getenv("FLASK_APP_TIMEZONE", "UTC")


@app.template_filter("format_datetime")
def format_datetime_filter(timestamp: Optional[str]) -> str:
    """Format UTC datetime to a configurable local timezone."""
    if timestamp:
        utc_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        utc_dt = pytz.utc.localize(utc_dt)
        try:
            local_tz = timezone(APP_TIMEZONE)
            local_dt = utc_dt.astimezone(local_tz)
            return local_dt.strftime(f"%Y/%m/%d %H:%M:%S %Z%z")
        except pytz.exceptions.UnknownTimeZoneError:
            return utc_dt.strftime(f"%Y/%m/%d %H:%M:%S UTC")
    return ""


def get_db() -> sqlite3.Connection:
    """Connect to the database."""
    if not app.config["DATABASE"]:
        raise RuntimeError("Database not configured")
    if not hasattr(app, "config"):
        raise RuntimeError("App configuration not found")
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e: Optional[Any] = None) -> None:
    """Close the database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.cli.command("init-db")
def init_db() -> None:
    """CLI to initialise the database based upon /schema.sql."""
    db = get_db()
    with app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()
    click.echo("Initialised the database.")


def get_jobs(
    status: Optional[str] = None, sort_by: str = "id", order: str = "asc"
) -> list[sqlite3.Row]:
    """Fetch job applications with optional filtering and sorting."""
    db = get_db()
    query = "SELECT id, company, position, status, last_modified FROM jobs"
    params = []

    if status and status != "All":
        query += " WHERE status = ?"
        params.append(status)

    if sort_by not in ["id", "company", "position", "status", "last_modified"]:
        sort_by = "id"
    if order not in ["asc", "desc"]:
        order = "asc"

    query += f" ORDER BY {sort_by} {order}"
    cur = db.execute(query, params)
    return cur.fetchall()


@app.route("/")
def index() -> str:
    """Display all job applications with optional sorting and status filtering."""
    status = request.args.get("status", "All")
    sort_by = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    jobs = get_jobs(status, sort_by, order)
    return render_template(
        "index.html", jobs=jobs, current_status=status, sort_by=sort_by, order=order
    )


@app.route("/job/<int:job_id>")
def get_job(job_id: int) -> Any:
    """Fetch a single job application by id."""
    db = get_db()
    cur = db.execute(
        "SELECT id, company, position, status, last_modified FROM jobs WHERE id = ?",
        (job_id,),
    )
    job = cur.fetchone()
    if job is None:
        abort(404)
    return job


@app.route("/add", methods=["GET", "POST"])
def add_job() -> Union[str, redirect]:
    """Add a new job application."""
    if request.method == "POST":
        company = request.form["company"].strip()
        position = request.form["position"].strip()
        status = request.form["status"].strip()
        if not company or not position:
            flash("Company and position are required!")
        elif status not in ["Applied", "Interviewed", "Accepted", "Declined"]:
            flash("Invalid status!")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO jobs (company, position, status) VALUES (?, ?, ?)",
                (company, position, status),
            )
            db.commit()
            flash("Job application added successfully!")
            return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_job(id: int) -> str:
    """Edit an exisiting job application."""
    job = get_job(id)
    if job is None:
        abort(404)

    if request.method == "POST":
        company = request.form["company"].strip()
        position = request.form["position"].strip()
        status = request.form["status"].strip()
        if not company or not position:
            flash("Company and position are required!")
        elif status not in ["Applied", "Interviewed", "Accepted", "Declined"]:
            flash("Invalid status!")
        else:
            db = get_db()
            db.execute(
                "UPDATE jobs SET company = ?, position = ?, status = ?, last_modified = CURRENT_TIMESTAMP WHERE id = ?",
                (company, position, status, id),
            )
            db.commit()
            flash("Job application updated successfully!")
            return redirect(url_for("index"))
    return render_template("edit.html", job=job)


@app.route("/<int:id>/delete", methods=["POST"])
def delete_job(id: int) -> str:
    """Delete a job application."""
    job = get_job(id)
    if job is None:
        abort(404)

    db = get_db()
    db.execute("DELETE FROM jobs WHERE id = ?", (id,))
    db.commit()
    flash("Job application deleted successfully!")
    return redirect(url_for("index"))


@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id: int) -> tuple[Any, int] | Any:
    """Update the status of a job application."""
    job = get_job(id)
    if job is None:
        abort(404)

    new_status = request.json.get("status")
    if new_status not in ["Applied", "Interviewed", "Accepted", "Declined"]:
        return jsonify({"error": "Invalid status"}), 400

    db = get_db()
    db.execute(
        "UPDATE jobs SET status = ?, last_modified = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, id),
    )
    db.commit()
    return jsonify({"message": "Status updated successfully"}), 200


@app.errorhandler(404)
def not_found(error: Any) -> tuple[str, int]:
    return render_template("404.html"), 404
