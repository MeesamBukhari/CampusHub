# CampusHub

CampusHub is a full-stack application designed to provide a seamless campus management experience. The backend is built using Flask (Python) and the frontend uses React with Vite for fast development.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Backend Setup & Run](#backend-setup--run)
4. [Frontend Setup & Run](#frontend-setup--run)
5. [Troubleshooting](#troubleshooting)
6. [License](#license)

## Features

- Full-stack application with REST API support
- User-friendly interface built with React
- MySQL database integration
- Modular project structure with separate backend and frontend

## Prerequisites

- **MySQL Server:** Ensure MySQL is installed and running.
  - Default configuration assumes user: `root`, password: `password`
- **Node.js & npm:** Required to run the frontend.
- **Python 3.x:** Required to run the backend.

Database name: `campushub` (will be created automatically).

## Backend Setup & Run

The backend handles the API and database connections.

1. Open a terminal in the project root.
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Activate the virtual environment:
   ```bash
   .\env\Scripts\activate  # Windows
   source env/bin/activate    # macOS/Linux
   ```
4. Initialize the database (required for first-time setup or if the DB is missing):
   ```bash
   python init_db.py
   ```
   **Note:** If this fails with `Error: 2003...`, your MySQL server is not running. Start it and try again.
5. Run the backend server:
   ```bash
   python app.py
   ```
6. The backend should now be running at [http://localhost:5000](http://localhost:5000).

## Frontend Setup & Run

The frontend is the user interface for CampusHub.

1. Open a new terminal (keep the backend running).
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```
5. Open the local URL displayed in the terminal (usually [http://localhost:5173](http://localhost:5173) or [http://127.0.0.1:5173](http://127.0.0.1:5173)).

## Troubleshooting

- **Database Connection:** Check `backend/config.py` if your MySQL credentials differ.
- **Browser Connectivity:** If `http://localhost:5173` doesn't work, try `http://127.0.0.1:5173`.
- **Port Conflicts:** If ports are busy, terminate other Python or Node processes using the same ports.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

