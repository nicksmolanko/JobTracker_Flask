# Job Tracker Flask App

A simple web app built with Flask to help users track their job application. 

This application allows users to add, view, edit and delete job application entries, as well as filter and sort them.

This project uses a SQLite database to store job entries with id, company, position, status, created_at and last_modified fields.

Job company and position names are truncated if they're longer than 30 characters.

## Features

- Add new job applications with company, position and status (Applied, Interviewed, Accepted, Declined)
- View and sort job applications by clicking the column title.
- Filter job applications by status through tabs.
- Edit and Delete job applications.
- Update job application status.
- Basic error handling (404 page).
- Pytest testing.

## Technologies

- **Backend:** Python, Flask, SQLite3
- **Frontend:** HTML, CSS, Jinja2
- **Testing:** pytest
- **Dependency management:** pip
- **Environment Variables:** python-dotenv
- **Timezone Handling:** pytz

## Setup and Installation

1. **Clone the repo**
    ```bash
    git clone https://github.com/nicksmolanko/JobTracker_Flask.git
    cd JobTracker_Flask
    ```

2. **Create a virtual python environment**
    ```bash
    pyhon -m venv venv
    ```

3. **Activate the virtual environment**
    ```bash
    ./venv/Scripts/activate
    ```

4. **Install the required dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables (.env)**
    Create a `.env` file in the root directory of the project.
    You can use the `.env.example` to structure your file.
    ```
    SECRET_KEY='your_secret_key'
    FLASK_APP_TIMEZONE='Australia/Adelaide' # examples: 'Australia/Sydney', 'Australia/Melbourne'
    ```

6. **Initialise the database**
    Create the `database.db` file based on the `schema.sql` definition.
    ```bash
    flask --app app init-db
    ```

## Running Tests

This project includes pytest to ensure the application is correctly functioning.

1. **Run the tests**
    The following script will run the tests and provide a summary of test results.
    ```bash
    python run_tests.py
    ```

## Usage

To run the flask app run the following script.
```bash
flask --app app run
```

## API Endpoints

Examples of how to interact with the app's API endpoints.

### GET /job/<int:job_id>

Fetch a single job application by id.

**Example Request:**

```http
GET /job/1 HTTP/1.1
Host: localhost:5000
```

**Example Response:**

```json
{
  "id": 1,
  "company": "Google",
  "position": "Software Engineer",
  "status": "Applied",
  "last_modified": "2025-06-02 10:00:00"
}
```

### POST /update_status/<int:id>

Update the status of a job application.

**Example Request:**

```http
POST /update_status/1 HTTP/1.1
Content-Type: application/json
Host: localhost:5000

{
    "status": "Interviewed"
}
```

**Example Response (Success):**

```json
{
  "message": "Status updated successfully"
}
```

**Example Response (Error - Invalid Status):**

```json
{
  "error": "Invalid status"
}
```

## Credits
- **Bulma.io** used for styling the application (CSS).
