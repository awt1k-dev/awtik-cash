# Awtik Cash 💸

Awtik Cash is a full-stack web application built with FastAPI that provides authentication, profile management, and a basic financial transaction system with admin functionality.

---

## 🚀 Features

- User registration & authentication (session-based)
- Profile management
- Transaction handling
- Admin panel with role-based access
- Server-side rendering with Jinja2
- Static frontend (HTML, CSS, JS)
- Dockerized environment
- Database migrations via Alembic

---

## 🛠 Tech Stack

- **Backend:** FastAPI (async)
- **Database:** PostgreSQL + SQLAlchemy (async)
- **Templating:** Jinja2
- **Auth:** Session-based
- **Migrations:** Alembic
- **DevOps:** Docker / Docker Compose

---

## 📁 Project Structure

```
app/
 ├── core/           # Config, security, utils
 ├── db/             # DB models & session
 ├── routes/         # Endpoints & views
 ├── templates/      # HTML templates
 ├── static/         # CSS, JS, images
 ├── schemas.py      # Pydantic schemas
 ├── crud.py         # Database logic
main.py              # Entry point
alembic/             # DB migrations
Dockerfile
docker-compose.yaml
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```
# App
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
SECRET_KEY=your_secret_key

# Database (REQUIRED)
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/db_name
```

---

## 🐳 Run with Docker (Recommended)

```
docker-compose up --build
```

This will:
- Start PostgreSQL
- Run migrations (if configured)
- Launch FastAPI app

App will be available at:
```
http://localhost:8000
```

---

## 💻 Run Locally

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Set environment variables
Create `.env` (see above)

### 3. Run database
Make sure PostgreSQL is running and matches `DATABASE_URL`

### 4. Run migrations
```
alembic upgrade head
```

### 5. Start server
```
uvicorn main:app --reload
```

---

## 🔐 Authentication

- Uses session-based authentication
- Role-based access control (admin/user)
- Sessions handled via middleware

---

## 📈 Improvements (for production)

- JWT + refresh token authentication
- Add unit/integration tests (pytest)
- Logging system
- Service layer (business logic separation)
- Better error handling & validation
- CI/CD pipeline

---

## 👨‍💻 Author Notes

This project demonstrates:

- Solid backend fundamentals
- Understanding of async Python
- Experience with real-world tools (Docker, Alembic)
- Full-stack integration basics