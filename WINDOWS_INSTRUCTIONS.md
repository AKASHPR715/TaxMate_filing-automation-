# Running TaxMate on Windows with Docker

This guide explains how to run the TaxMate application on Windows using Docker Desktop.

## Prerequisites

1.  **Install Docker Desktop for Windows**
    *   Download and install from [Docker Hub](https://www.docker.com/products/docker-desktop/).
    *   Ensure WSL 2 (Windows Subsystem for Linux) is enabled during installation (recommended).

2.  **Git (Optional)**
    *   Useful for cloning the repository if you haven't already.

## Steps to Run

1.  **Open PowerShell or Command Prompt**
    *   Navigate to the project root directory (where `docker-compose.yml` is located).
    ```powershell
    cd path/to/TaxMate_filing-automation-
    ```

2.  **Build and Start Containers**
    *   Run the following command to build the images and start the services:
    ```powershell
    docker compose up --build -d
    ```
    *   The `-d` flag runs the containers in the background (detached mode).

3.  **Access the Application**
    *   **Frontend**: Open your browser and go to `http://localhost:3000`.
    *   **Backend API Docs**: Open `http://localhost:8000/docs`.

4.  **Stopping the Application**
    *   To stop the containers, run:
    ```powershell
    docker compose down
    ```

## Troubleshooting

*   **Port Conflicts**: If ports 3000, 8000, or 27017 are already in use, you may need to stop other applications or modify the `ports` mapping in `docker-compose.yml`.
*   **Memory Issues**: If the build fails due to memory, increase the memory allocation in Docker Desktop settings.
*   **Database Persistence**: Data is stored in a Docker volume named `mongo-data`. This ensures your data persists even if you restart containers.
