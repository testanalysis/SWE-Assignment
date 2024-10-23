# SWE-Assignment
2024-08-13 Coding Assignment

**Flask App with SQLite and Docker
**
This repository contains a Flask application that uses SQLite as the database and is containerized using Docker. The application provides an API for managing administrators, applicants, households, schemes, applications, and scheme-related information such as benefits and criteria.

**Prerequisites**

   Before running the application, ensure that you have the following installed:
   
   Docker: You can download and install Docker from here: https://docs.docker.com/engine/install/

   Docker Compose: This should come pre-installed with Docker Desktop. If not, follow the Docker Compose installation
   instructions.
   
   Postman: You can download and install Postman from here: https://www.postman.com/downloads/

**How to Run the Application**

   To run the Flask application using Docker, follow these steps:
   
   Clone this repository:
   git clone https://github.com/testanalysis/SWE-Assignment.git
   
   cd to SWE-Assignment-main

## Docker Setup Instructions

### 1. Configuring File Sharing for Docker

If Docker cannot access the project directory, you may need to configure Docker to share the required folder. Here's how you can do it based on your operating system:

#### macOS / Windows
1. Open **Docker Desktop**.
2. Navigate to **Preferences** (macOS) or **Settings** (Windows).
3. Go to the **Resources** section and then select **File Sharing** (macOS) or **Shared Drives** (Windows).
4. Add the path to your project directory:
   - macOS: Click the **`+` button** and select path to the git cloned folder. Click the **`+` button** so that the path is registered for file sharing. 
   - Windows: Go to bottom right of Windows, right click docker.
      - Select "Switch to linux containers" and "Switch"
      - You should now see "File Sharing" Option. 
      - Ensure the appropriate drive (e.g., `C:` or `D:`) is checked.
      - A video guide here for you if you cant find: https://go.screenpal.com/watch/cFjIljq6db
5. Click **Apply & Restart**.
6. Open a terminal, cd to SWE-Assignment-main. You should see app.py & dockerfile etc when you list the directory.
7. Run "docker-compose up --build".
8. The Flask app should be listening on http://localhost:5001
9. Stopping the containers: To stop the Docker containers, press Ctrl + C in the terminal

## System API Usage Guide

This README will guide you through the process of using the system API for registering, logging in, and managing applicants, schemes, and applications. The steps include user registration, login, and making authenticated API calls.

**Prerequisites**

A tool like Postman or curl to make HTTP requests.
Base URL for API calls: http://localhost:5001/

Steps

1. Register a New User
First, register a new user account by sending a POST request to the /register endpoint with the following JSON body:

json
{
  "username": "account1",
  "password": "1"
}

2. Login to the System
Next, log in using the same account credentials. Send a POST request to the /login endpoint with the following body:

json
{
  "username": "account1",
  "password": "1"
}

In response, you will receive an access_token. Copy this token for the next step.

3. Authenticate with Bearer Token
To authenticate future requests, include the access_token in the header of all API requests that require authorization:

In Postman:
Go to the Authorization tab.
Select Bearer Token from the dropdown.
Paste the access_token into the Token field.

4. View All Schemes
As a system administrator, you can view all schemes by sending a GET request to:

GET /schemes
Ensure the request contains the Bearer token from the previous step in the header.

5. Add New Applicants
Before creating an application, you need to save applicant data. Send a POST request to /applicants with an example JSON body like this:

json
{
  "date_of_birth": "1984-10-06",
  "employment_status": "unemployed",
  "household": [
    {
      "date_of_birth": "2016-02-01",
      "employment_status": "unemployed",
      "name": "Gwen",
      "relation": "daughter",
      "sex": "female"
    },
    {
      "date_of_birth": "2018-03-15",
      "employment_status": "unemployed",
      "name": "Jayden",
      "relation": "son",
      "sex": "male"
    }
  ],
  "marital_status": "married",
  "name": "Mary",
  "sex": "female"
}

6. Create a New Application
Once an applicant is registered, you can create a new application for them by sending a POST request to /applications with the following JSON body:

json
{
  "name": "Mary",
  "date_of_birth": "1984-10-06",
  "scheme_applied": "Retrenchment Assistance Scheme (families)"
}

7. Check Eligibility for Schemes
To check an applicant's eligibility for various schemes, use the applicant's id and send a GET request to:

GET /schemes/eligible?applicant={id}
Make sure to replace {id} with the actual applicant's ID.

8. Additional APIs
Administrators Management: Manage administrator accounts with the following endpoints:
GET /administrators: View all administrators.
DELETE /administrators/{id}: Delete an administrator by their ID.
Scheme Management:
POST /add_scheme: Add a new scheme.
DELETE /delete_scheme/{id}: Delete a scheme by its ID.
Applications Management:
GET /applications: View all applications.



## Available APIs

Once the app is running, the following APIs will be available at http://localhost:5001/:

1. Login:

POST /login: Authenticate a user and provide access tokens.

2. Administrators:

GET /administrators: Retrieve all administrators.

POST /register: Create a new administrator.

DELETE /administrators/{id}: Delete a specific administrator by its ID.

3. Applicants:
   
GET /applicants: Retrieve all applicants.

POST /applicants: Create a new applicant.

4. Household:
   
GET /household: Retrieve household information.

5. Schemes:
   
GET /schemes: Retrieve all schemes.

GET /schemes/eligible?applicant={id}: Get all schemes an applicant is eligible for.

DELETE /delete_scheme/{id}: Delete a specific scheme by its ID.

POST /add_scheme: Add a new scheme.

6. Scheme Benefits:
 
GET /scheme_benefits: Retrieve all scheme benefits.

7. Scheme Criteria:
   
GET /scheme_criteria: Retrieve all scheme criteria.

8. Applications:

GET /applications: Retrieve all applications.

POST /applications: Create a new application.
