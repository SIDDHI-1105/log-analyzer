
readme_content = """<div align="center">

# 🔍 Log Analyzer

**A Modern Full-Stack Log Management & Monitoring Platform**

[![Render Status](https://img.shields.io/badge/Render-Live-success?style=flat-square&logo=render)](https://log-analyzer-frontend-3pk8.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

[🌐 Live Demo](https://log-analyzer-frontend-3pk8.onrender.com) · [📖 API Docs](https://log-analyzer-kq8h.onrender.com/docs) · [📂 GitHub](https://github.com/SIDDHI-1105/log-analyzer)

</div>

---

## 📋 Table of Contents

- [What is Log Analyzer?](#-what-is-log-analyzer)
- [Why We Built This](#-why-we-built-this)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Live Demo](#-live-demo)
- [How to Use](#-how-to-use)
  - [Getting Started](#getting-started)
  - [Dashboard](#dashboard)
  - [Log Explorer](#log-explorer)
  - [Alerts](#alerts)
  - [Settings](#settings)
- [Screenshots](#-screenshots)
- [Local Development](#-local-development)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🤔 What is Log Analyzer?

**Log Analyzer** is a production-ready, full-stack web application designed to help developers and DevOps teams **collect, analyze, monitor, and visualize application logs** in real-time.

Think of it as a lightweight, self-hosted alternative to expensive log management services like Splunk, Datadog, or Loggly — but built with modern open-source technologies and deployable anywhere.

### What It Does

| Feature | Description |
|---------|-------------|
| 📥 **Log Ingestion** | Accept logs via REST API with support for Plain Text, JSON, and Nginx formats |
| 🔎 **Log Explorer** | Search, filter, and paginate through millions of log entries with full-text search |
| 📊 **Dashboard** | Visualize error trends, severity distribution, service health, and volume over time |
| 🚨 **Alerting** | Create custom alert rules based on log patterns, thresholds, and time windows |
| 🔑 **API Keys** | Generate secure API keys for programmatic log ingestion |
| 🌙 **Dark Mode** | Beautiful dark/light theme with system preference detection |
| 📱 **Responsive** | Works on desktop, tablet, and mobile devices |

---

## 💡 Why We Built This

Modern applications generate massive amounts of log data. Existing solutions are either:
- **Too expensive** for small teams and side projects
- **Too complex** to set up and maintain
- **Too limited** in features for real-world use

**Log Analyzer solves these problems by providing:**

✅ **Free & Open Source** — No licensing fees, full source code access  
✅ **Easy Deployment** — One-click deploy to Render, Docker, or any cloud provider  
✅ **Modern Stack** — Built with FastAPI, React 19, PostgreSQL, and Tailwind CSS  
✅ **Real-time Monitoring** — WebSocket live tail for watching logs as they happen  
✅ **Beautiful UI** — Professional interface with charts, animations, and dark mode  

---

## ✨ Key Features

### 🔐 Authentication & Security
- JWT-based authentication with secure token storage
- Password hashing with Argon2
- API key management for service-to-service authentication
- Role-based access control (RBAC) ready

### 📊 Interactive Dashboard
- **KPI Cards** — Total logs, errors, warnings, unique services
- **Time Range Selector** — Filter data by last 24h, 7d, or 30d
- **Bar Chart** — Logs grouped by severity level
- **Line Chart** — Log volume trends over time
- **Pie Chart** — Service distribution breakdown
- **Recent Activity** — Latest logs and active alerts at a glance

### 🔍 Log Explorer
- **Full-text Search** — Search across log messages, services, and metadata
- **Level Filtering** — Filter by DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Service Filtering** — Filter by application service name
- **Pagination** — Navigate through large result sets
- **Log Detail Dialog** — View full message, metadata, trace_id, host, and copy to clipboard
- **Skeleton Loading** — Smooth loading states for better UX

### 🚨 Alert Management
- **Create Alert Rules** — Define conditions based on log count, level, or patterns
- **Toggle Active/Inactive** — Enable or disable rules on demand
- **Alert History** — View when alerts were triggered
- **Search & Filter** — Find rules by name or status

### ⚙️ Settings & Profile
- **Avatar Upload** — Upload profile pictures (base64 storage)
- **Password Change** — Secure password update flow
- **API Keys** — Create, copy, and revoke API keys
- **Theme Toggle** — Switch between light, dark, and system themes

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance Python web framework |
| **SQLAlchemy 2.0** | Modern ORM for database operations |
| **PostgreSQL** | Production-grade relational database |
| **Alembic** | Database migration management |
| **Pydantic** | Data validation and settings management |
| **Passlib + Argon2** | Secure password hashing |
| **python-jose** | JWT token generation and verification |
| **WebSockets** | Real-time live tail functionality |

### Frontend
| Technology | Purpose |
|------------|---------|
| **React 19** | Latest React with concurrent features |
| **TypeScript** | Type-safe development |
| **Vite** | Lightning-fast build tool |
| **Tailwind CSS v4** | Utility-first CSS framework |
| **shadcn/ui** | Beautiful, accessible UI components |
| **TanStack Query** | Powerful data fetching and caching |
| **Recharts** | Composable charting library |
| **Zustand** | Lightweight state management |
| **React Router v7** | Client-side routing |

### DevOps & Deployment
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization for consistent deployments |
| **Docker Compose** | Multi-service orchestration |
| **Render** | Cloud platform for hosting (free tier) |
| **GitHub Actions** | CI/CD pipeline (ready to configure) |

---

## 🌐 Live Demo

### Try It Now

🔗 **Frontend:** [https://log-analyzer-frontend-3pk8.onrender.com](https://log-analyzer-frontend-3pk8.onrender.com)

🔗 **API Documentation:** [https://log-analyzer-kq8h.onrender.com/docs](https://log-analyzer-kq8h.onrender.com/docs)

> **Note:** The application uses Render's free tier, so the backend may take 30-60 seconds to wake up if it has been idle. Please be patient on first load!

---

## 🚀 How to Use

### Getting Started

1. **Visit the Live Demo** — Click the link above
2. **Create an Account** — Click "Sign up" and register with your email
3. **Log In** — Use your credentials to access the dashboard

### Dashboard

After logging in, you'll see the **Dashboard** with:
- Summary statistics (total logs, errors, warnings)
- Interactive charts showing log trends
- Recent log entries
- Active alerts

Use the **time range buttons** (24h, 7d, 30d) to filter data.

### Log Explorer

Navigate to **Log Explorer** from the sidebar to:
- Browse all ingested logs
- Search by keyword in the search bar
- Filter by log level (ERROR, WARNING, INFO, etc.)
- Filter by service name
- Click on any log row to see full details

### Alerts

Go to **Alerts** to:
- View existing alert rules
- Create new rules (e.g., "Trigger if more than 10 ERROR logs in 5 minutes")
- Toggle rules on/off
- View alert trigger history

### Settings

In **Settings**, you can:
- Update your profile and avatar
- Change your password
- Generate API keys for programmatic access
- Switch between light/dark themes

---

## 📸 Screenshots

<div align="center">

| Login Page | Dashboard |
|:----------:|:---------:|
| Dark-themed login with form validation | KPI cards, charts, and recent activity |

| Log Explorer | Alert Manager |
|:----------:|:-----------:|
| Searchable table with filters and pagination | Create, edit, and manage alert rules |

</div>

---

## 💻 Local Development

### Prerequisites
- Node.js 22+
- Python 3.12+
- PostgreSQL 16+
- Docker (optional)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/SIDDHI-1105/log-analyzer.git
cd log-analyzer

# Copy environment variables
cp .env.example .env

# Start all services (backend, frontend, database)
./deploy.sh dev

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Start server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev

# Open http://localhost:5173
```

---

## 🚢 Deployment

### Deploy to Render (Recommended)

1. Fork/clone this repository to your GitHub account
2. Sign up at [render.com](https://render.com)
3. Click **New +** → **Blueprint**
4. Connect your GitHub repository
5. Render will automatically create:
   - PostgreSQL database
   - Backend web service
   - Frontend static site
6. Update `BACKEND_CORS_ORIGINS` with your frontend URL

See [RENDER_DEPLOY.md](./RENDER_DEPLOY.md) for detailed instructions.

### Deploy with Docker

```bash
# Production deployment
./deploy.sh prod

# Or manually
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 📚 API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register new user | Public |
| POST | `/api/v1/auth/login` | Login and get JWT token | Public |
| GET | `/api/v1/auth/me` | Get current user profile | JWT |
| PUT | `/api/v1/auth/me` | Update user profile | JWT |
| POST | `/api/v1/auth/change-password` | Change password | JWT |

### Log Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/logs/ingest` | Ingest new logs | API Key |
| GET | `/api/v1/logs/` | List logs with filters | JWT |

### Stats Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/stats/` | Get summary statistics | JWT |
| GET | `/api/v1/stats/timeseries` | Get time-series data | JWT |

### Alert Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/POST | `/api/v1/alerts/rules` | Manage alert rules | JWT |
| GET | `/api/v1/alerts/history` | View alert history | JWT |

### WebSocket

| Endpoint | Description | Auth |
|----------|-------------|------|
| `/api/v1/live-tail` | Real-time log streaming | JWT (query param) |

**Full API documentation available at:** `https://your-backend-url.onrender.com/docs`

---

## 🔮 Future Roadmap

### Phase 1: Critical Infrastructure
- [x] Docker & Docker Compose support
- [x] Render deployment
- [x] Production environment configuration
- [ ] Backend unit & integration tests
- [ ] Rate limiting on auth endpoints
- [ ] Global exception middleware

### Phase 2: Enhanced Features
- [ ] **AI-Powered Analysis**
  - Root cause analysis for errors
  - Automatic error explanation
  - Suggested fixes
  - Log pattern anomaly detection
  
- [ ] **Advanced Monitoring**
  - Slack/Discord webhook notifications
  - Email alerts
  - PagerDuty integration
  
- [ ] **Log Export**
  - Export logs as CSV, JSON, or PDF
  - Scheduled reports
  - Data retention policies

### Phase 3: Scale & Performance
- [ ] **Redis Integration**
  - WebSocket pub/sub scaling
  - API response caching
  - Session management
  
- [ ] **Database Optimization**
  - Full-text search indexes
  - Composite indexes for common queries
  - Log partitioning by date
  
- [ ] **Background Jobs**
  - Celery task queue
  - Scheduled alert evaluation
  - Automated log cleanup

### Phase 4: Enterprise Features
- [ ] **Multi-tenancy**
  - Organization/team support
  - Role-based permissions (RBAC)
  - Audit logging
  
- [ ] **Advanced Analytics**
  - Custom dashboards
  - Saved filters and queries
  - Performance metrics
  
- [ ] **Integrations**
  - AWS CloudWatch
  - Google Cloud Logging
  - Azure Monitor
  - Fluentd/Fluent Bit

### Phase 5: Developer Experience
- [ ] **CLI Tool Enhancement**
  - Real-time log streaming from CLI
  - Bulk log upload
  - Configuration management
  
- [ ] **SDKs**
  - Python SDK for log ingestion
  - JavaScript/Node.js SDK
  - Go SDK
  
- [ ] **Documentation**
  - Interactive API playground
  - Video tutorials
  - Deployment guides for AWS, GCP, Azure

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Siddhi Tripathi](https://github.com/SIDDHI-1105)**

⭐ Star this repository if you find it helpful!

</div>
"""

with open("/mnt/agents/output/README.md", "w") as f:
    f.write(readme_content)


