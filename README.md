# SWE-Assignment
2024-08-13 Coding Assignment

**Flask App with SQLite and Docker
**
This repository contains a Flask application that uses SQLite as the database and is containerized using Docker. The application provides an API for managing administrators, applicants, households, schemes, applications, and scheme-related information such as benefits and criteria.

**Prerequisites**

Before running the application, ensure that you have the following installed:

Docker: You can download and install Docker from here: https://docs.docker.com/engine/install/

Docker Compose: This should come pre-installed with Docker Desktop. If not, follow the Docker Compose installation instructions.

**How to Run the Application
**
To run the Flask application using Docker, follow these steps:

Clone this repository:
git clone https://github.com/testanalysis/SWE-Assignment.git

cd SWE-Assignment-main

## Docker Setup Instructions

### 1. Configuring File Sharing for Docker

If Docker cannot access the project directory, you may need to configure Docker to share the required folder. Here's how you can do it based on your operating system:

#### macOS / Windows
1. Open **Docker Desktop**.
2. Navigate to **Preferences** (macOS) or **Settings** (Windows).
3. Go to the **Resources** section and then select **File Sharing** (macOS) or **Shared Drives** (Windows).
4. Add the path to your project directory:
   - macOS: Click the **`+` button** and select path to the git cloned folder. Click the **`+` button** so that the path is registered for file sharing. 
   - Windows: Ensure the appropriate drive (e.g., `C:` or `D:`) is checked.
5. Click **Apply & Restart**.
6. Open a terminal, cd to the folder where the it has been git cloned.
7. Run "docker-compose up --build".
8. The Flask app should be listening on http://localhost:5001
9. Stopping the containers: To stop the Docker containers, press Ctrl + C in the terminal or run:
bash

Available APIs

Once the app is running, the following APIs will be available at http://localhost:5001/:

1. Administrators:
GET /administrators: Retrieve all administrators.
POST /administrators: Create a new administrator.

3. Applicants:
GET /applicants: Retrieve all applicants.
POST /applicants: Create a new applicant.

5. Household:
GET /household: Retrieve household information.

6. Schemes:
GET /schemes: Retrieve all schemes.
GET /schemes/eligible?applicant={id}: Get all schemes an applicant is eligible for.

7. Applications:
GET /applications: Retrieve all applications.

8. Scheme Benefits:
GET /scheme_benefits: Retrieve all scheme benefits.

9. Scheme Criteria:
GET /scheme_criteria: Retrieve all scheme criteria.
