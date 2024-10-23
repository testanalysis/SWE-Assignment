# SWE-Assignment
2024-08-13 Coding Assignment

Flask App with SQLite and Docker

This repository contains a Flask application that uses SQLite as the database and is containerized using Docker. The application provides a simple API for managing administrators, applicants, households, schemes, applications, and scheme-related information such as benefits and criteria.

Prerequisites

Before running the application, ensure that you have the following installed:

Docker: You can download and install Docker from here: https://docs.docker.com/engine/install/

Docker Compose: This should come pre-installed with Docker Desktop. If not, follow the Docker Compose installation instructions.
How to Run the Application

To run the Flask application using Docker, follow these steps:

Clone this repository:
git clone https://github.com/your-repo/flask-sqlite-docker-app.git

cd SWE-Assignment-main

Open Docker Desktop Preferences:
Open Docker Desktop on your Mac.
Click on the Docker icon in the macOS menu bar.
Select Preferences (or Settings depending on your version).
Go to the Resources Section:
In the Preferences window, select Resources from the left sidebar.
Then, select File Sharing.
Add the Path to Your Shared Directories:
In the File Sharing tab, you’ll see a list of directories that are shared with Docker.
Click the + button to add a new directory.
Navigate to /Downloads/SWE-Assignment-main and add it to the shared paths.
Click Apply & Restart to save the changes and restart Docker.
Verify Permissions:
Once Docker restarts, it should have access to the /Downloads/SWE-Assignment-main directory.
Run your Docker commands again, and the error should be resolved.

Run Docker Compose: Docker Compose will build the image and run the application along with the necessary environment setup.
bash
docker-compose up

This will start the application on http://localhost:5001.

Stopping the containers: To stop the Docker containers, press Ctrl + C in the terminal or run:
bash
docker-compose down

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
