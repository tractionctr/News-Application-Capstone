# News Application Capstone

## Overview

A Django-based news platform with role-based authentication and article management.

### Features

* Reader, Journalist, and Editor roles
* Article creation, editing, and approval workflow
* Publisher and journalist subscriptions
* Newsletter system
* REST API support
* Docker support
* Sphinx documentation

## Running with Virtual Environment (venv)

### 1. Clone the repository

```bash
git clone https://github.com/tractionctr/News-Application-Capstone
cd News-Application-Capstone
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Create a `.env` file in the project root and add your own values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Run server

```bash
python manage.py runserver
```

## Running with Docker

### Build image

```bash
docker build -t news-app .
```

### Run container

```bash
docker run -p 8000:8000 news-app
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Documentation

Sphinx docs are located in the `docs/` folder.

Build docs manually:

```bash
cd docs
python -m sphinx -b html . _build
```

Open generated docs from:

```bash
_build/index.html
```

## Notes

* Do not commit `.env`, secrets, or tokens.
* `.gitignore` is configured to exclude sensitive files and virtual environments.
