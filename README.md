StudyDeck Forum is a Django REST API for course resources and discussion forums. Features include resource sharing, ratings, threaded discussions, likes, moderation, and reporting.

---

## Quick Start

### Local Development

```bash
git clone https://github.com/diptansuroy/studydeck-forum
cd studydeck-forum
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
python manage.py runserver
```

**Local Base URL**: `http://127.0.0.1:8000`  
**Production Base URL**: `https://studydeck-forum-2r1n.onrender.com`

---

## Authentication

The API uses JWT (JSON Web Tokens) via Django SimpleJWT + Allauth.

### Register & Login

```bash
# Register (via Allauth)
POST /accounts/signup/

# Login (get JWT token)
POST /api/token/
Body: { "username": "user", "password": "pass" }

# Refresh token
POST /api/token/refresh/
Body: { "refresh": "refresh-token" }
```

### Using Tokens

Include JWT in all authenticated requests:

```bash
curl -H "Authorization: Bearer <your-jwt-token>" https://studydeck-forum-2r1n.onrender.com/api/courses/
```

---

## Complete API Endpoint Reference

### 1. Courses

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/courses/` | ❌ | List all active courses |
| `GET` | `/api/courses/?q=python` | ❌ | Search courses by code/title/description |

**Example**:
```bash
curl https://studydeck-forum-2r1n.onrender.com/api/courses/

# Search
curl https://studydeck-forum-2r1n.onrender.com/api/courses/?q=python
```

---

### 2. Resources

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/resources/` | ❌ | List all resources |
| `GET` | `/api/resources/?course=CS101` | ❌ | Filter by course code |
| `POST` | `/api/resources/` | ✅ | Upload new resource |
| `POST` | `/api/resources/{id}/rate/` | ✅ | Rate a resource (1-5 stars) |
| `GET` | `/api/resources/{id}/ratings/` | ❌ | Get all ratings for resource |
| `POST` | `/api/resources/{id}/view/` | ❌ | Increment view count |

**Example - Upload Resource**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/resources/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics",
    "description": "Introduction to Python",
    "resource_type": "pdf",
    "course": 1,
    "url": "https://example.com/python.pdf"
  }'
```

**Example - Rate Resource**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/resources/1/rate/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5, "comment": "Great resource!"}'
```

---

### 3. Categories

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/categories/` | ❌ | List all categories + thread count |
| `GET` | `/api/categories/{slug}/?page=1` | ❌ | Get threads in category (paginated) |

**Response**:
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "name": "General Discussion",
      "slug": "general",
      "thread_count": 42
    }
  ]
}
```

**Example**:
```bash
curl https://studydeck-forum-2r1n.onrender.com/api/categories/
curl https://studydeck-forum-2r1n.onrender.com/api/categories/general/?page=1
```

---

### 4. Tags

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/tags/` | ❌ | List all tags |
| `GET` | `/api/tags/{slug}/?page=1` | ❌ | Threads with tag (paginated) |

**Example**:
```bash
curl https://studydeck-forum-2r1n.onrender.com/api/tags/
curl https://studydeck-forum-2r1n.onrender.com/api/tags/homework/?page=1
```

---

### 5. Threads (Forum Posts)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/threads/` | ❌ | List all threads (paginated) |
| `GET` | `/api/threads/?q=help&category=general&page=1` | ❌ | Search & filter threads |
| `GET` | `/api/threads/{id}/` | ❌ | Get thread + all replies |
| `POST` | `/api/threads/` | ✅ | Create new thread |
| `PATCH` | `/api/threads/{id}/` | ✅ | Update thread (owner only) |
| `DELETE` | `/api/threads/{id}/` | ✅ | Delete thread (owner/mod) |
| `POST` | `/api/threads/{id}/lock/` | ✅ (mod) | Lock thread (no new replies) |
| `POST` | `/api/threads/{id}/pin/` | ✅ (mod) | Pin/unpin thread |
| `POST` | `/api/threads/{id}/like/` | ✅ | Like/unlike thread |

**Example - Create Thread**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/threads/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to learn Django?",
    "content": "I'm new to Django. Any good resources?",
    "category": 1,
    "tags": [1, 2]
  }'
```

**Example - Search Threads**:
```bash
curl https://studydeck-forum-2r1n.onrender.com/api/threads/?q=django&category=general&page=1
```

**Example - Like Thread**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/threads/5/like/ \
  -H "Authorization: Bearer your-token"

# Response: { "message": "Thread liked", "like_count": 10, "user_liked": true }
```

---

### 6. Replies (Forum Responses)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/threads/{id}/replies/` | ✅ | Create reply (locked threads blocked) |
| `PATCH` | `/api/replies/{id}/` | ✅ | Update reply (owner only) |
| `DELETE` | `/api/replies/{id}/` | ✅ | Soft delete reply (owner/mod) |
| `POST` | `/api/replies/{id}/mark-answer/` | ✅ | Mark as solution (thread owner) |
| `POST` | `/api/replies/{id}/like/` | ✅ | Like/unlike reply |

**Example - Create Reply**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/threads/5/replies/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "You can learn Django from the official docs!"
  }'
```

**Example - Mark as Answer**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/replies/23/mark-answer/ \
  -H "Authorization: Bearer your-token"
```

---

### 7. Moderation & Reports

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/reports/` | ✅ | Report inappropriate content |
| `GET` | `/api/reports/pending/?page=1` | ✅ (mod) | View pending reports |
| `PATCH` | `/api/reports/{id}/` | ✅ (mod) | Resolve report |
| `GET` | `/api/reports/` | ✅ | Get user's own reports |

**Example - Report Content**:
```bash
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/reports/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "thread",
    "thread": 5,
    "reason": "spam",
    "description": "This is spam content"
  }'
```

**Example - Resolve Report (Moderator)**:
```bash
curl -X PATCH https://studydeck-forum-2r1n.onrender.com/api/reports/1/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "notes": "Content removed"
  }'
```

---

### 8. Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users/` | ❌ | List all users (public profiles) |
| `GET` | `/api/profile/` | ✅ | Get current user's profile |

**Example**:
```bash
curl https://studydeck-forum-2r1n.onrender.com/api/users/
curl -H "Authorization: Bearer your-token" https://studydeck-forum-2r1n.onrender.com/api/profile/
```


## Setup Instructions

### Prerequisites
- Python 3.9+
- pip
- Git

### 1. Clone Repository

```bash
git clone https://github.com/diptansuroy/studydeck-forum.git
cd studydeck-forum
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file (optional):

```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/api/courses/`

---

## Design Decisions

### Database Models

**CustomUser**
- Extends Django's User model
- Added `is_moderator` flag for permission handling
- Supports future profile customization

**Course & Resource**
- Separated to allow multiple resources per course
- Resource tracking: view counts, ratings
- Supports multiple file types (PDF, video, article, etc.)

**Thread & Reply**
- Classic forum structure: threads contain replies
- Threads belong to categories and have tags (M2M)
- Replies support soft-delete for moderation
- `is_answer` flag marks best response
- Denormalized counters (`like_count`, `reply_count`) for performance

**Like**
- Generic like system for threads and replies
- Denormalized `like_count` on Thread/Reply (avoids COUNT queries)
- User can only like once (get_or_create pattern)

**Report**
- Moderation system with status workflow
- Tracks reporter, moderator, resolution notes
- Supports reporting threads and replies

### API Design

- **Function-based views** with DRF decorators: Simple, readable, testable
- **Manual pagination**: Query params (`?page=1`) instead of heavy abstractions
- **Soft delete for replies**: Preserves content for audit trails
- **Permission classes**: `IsAuthenticatedOrReadOnly` default (open reading, auth for writes)
- **Denormalized counters**: `like_count`, `view_count` avoid expensive COUNT queries

### Technology Choices

- **Django + DRF**: Rapid development, built-in serialization & permissions
- **SimpleJWT**: Token-based auth, stateless, mobile-friendly
- **Allauth**: Social login ready (Google OAuth configured)
- **SQLite locally, PostgreSQL on Render**: Scales without code changes
- **WhiteNoise**: Serves static files without external CDN
- **Gunicorn**: Production WSGI server, multi-worker support

### Deployment

- **Render.com**: Simple, free tier, auto-deploys from GitHub
- **Environment variables**: `DEBUG=False`, `ALLOWED_HOSTS` in production
- **Static files**: Collected via WhiteNoise, served efficiently
- **Migrations**: Auto-run in build command


## Production Deployment

Production is deployed at: **https://studydeck-forum-2r1n.onrender.com**


### Deploy Your Own Fork

1. Push code to GitHub
2. Create Render account
3. New Web Service → Connect GitHub repo
4. Build: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
5. Start: `gunicorn studydeck_forum.wsgi:application`
6. Environment vars: `DJANGO_SECRET_KEY`, `DEBUG=False`
7. Deploy!

---

## API Testing

### Using curl

```bash
# Get courses
curl https://studydeck-forum-2r1n.onrender.com/api/courses/

# Create thread (requires token)
curl -X POST https://studydeck-forum-2r1n.onrender.com/api/threads/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "content": "Test thread", "category": 1}'
```

### Using Postman

1. Import collection from repo (if provided)
2. Set `{{base_url}}` = `https://studydeck-forum-2r1n.onrender.com`
3. Set `{{token}}` in authorization header
4. Test endpoints directly

### Using Python

```python
import requests

BASE_URL = "https://studydeck-forum-2r1n.onrender.com"

# Get courses
response = requests.get(f"{BASE_URL}/api/courses/")
print(response.json())

# Get threads with auth
token = "your-jwt-token"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/threads/", headers=headers)
print(response.json())
```

**Happy learning with StudyDeck Forum!** 🎓
