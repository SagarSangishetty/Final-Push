🏗 Architecture

Services included:

backend – Application API
frontend – User interface
db – PostgreSQL database
redis – Caching / session store
nginx – Reverse proxy serving frontend and routing API requests

Docker internal networking allows services to communicate using their service names:

db
redis
backend
frontend

📦 Requirements

Make sure you have installed:

Docker
Docker Compose


.
├── backend/
├── frontend/
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
