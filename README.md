# News Application Capstone

## Overview

A Django-based news platform with role-based authentication and article management.

## Features

- Reader, Journalist, and Editor roles
- Article creation, editing, and approval workflow
- Publisher and journalist subscriptions
- Newsletter system
- REST API support
- Docker support
- Sphinx documentation

---

## Running with Virtual Environment (venv)

### 1. Clone repository

```bash
git clone https://github.com/tractionctr/News-Application-Capstone.git
cd News-Application-Capstone
```

### 2. Create and activate virtual environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=news_db
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Start server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Running with Docker

### 1. Create Docker network

```bash
docker network create news-net
```

### 2. Start MySQL container

```bash
docker run -d \
  --name mysql-db \
  --network news-net \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=news_db \
  mysql:8
```

### 3. Build Django image

```bash
docker build -t news-app .
```

### 4. Run migrations inside container

```bash
docker run -it --rm \
  --network news-net \
  -e DB_NAME=news_db \
  -e DB_USER=root \
  -e DB_PASSWORD=root \
  -e DB_HOST=mysql-db \
  -e DB_PORT=3306 \
  news-app \
  python manage.py migrate
```

### 5. Run Django container

```bash
docker run -p 8000:8000 \
  --network news-net \
  -e DB_NAME=news_db \
  -e DB_USER=root \
  -e DB_PASSWORD=root \
  -e DB_HOST=mysql-db \
  -e DB_PORT=3306 \
  news-app
```

Visit: http://127.0.0.1:8000/

---

## Documentation

Sphinx documentation is included in the `docs/` folder.

Build docs manually:

```bash
cd docs
python -m sphinx -b html . _build
```

Open:

```bash
_build/index.html
```

---

## Notes

- Do not commit `.env`, secrets, or tokens.
- `.gitignore` excludes virtual environments and sensitive files.
- Docker setup requires Docker Desktop or Docker support in GitHub Codespaces.
