# College Idea Innovation Hub

## 1. Project Overview

The College Idea Innovation Hub is a web-based platform designed to encourage students to share innovative ideas, develop creative solutions, and collaborate with other students.

The platform allows students to submit their ideas and track their review status. Faculty members can review submitted ideas, provide feedback, and approve or reject proposals.

## 2. Objectives

- Encourage innovation and creativity among students.
- Provide a common platform for submitting ideas.
- Enable faculty members to evaluate student proposals.
- Promote collaboration among students.
- Maintain a database of ideas and their review status.

## 3. Features

### Student Features
- Student registration and login.
- Student dashboard.
- Submit innovative ideas.
- View submitted ideas and their statuses.
- Update profile information.
- Browse approved ideas.
- Submit collaboration requests.

### Faculty Features
- Faculty login.
- Faculty dashboard.
- View pending ideas.
- Review student proposals.
- Approve or reject ideas.
- Provide feedback on submissions.
- View approved ideas.

### General Features
- Home page.
- About page.
- Contact form.
- Search approved ideas.
- Database storage.

## 4. Technologies Used

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python and Flask
- **Database:** SQLite
- **Development Environment:** Visual Studio Code
- **Version Control:** Git and GitHub

## 5. Project Structure

```text
College-Idea-Innovation-Hub/
├── app.py
├── requirements.txt
├── README.md
├── database.db
├── index.html
├── about.html
├── contact.html
├── login.html
├── register.html
├── student/
├── ideas/
├── faculty/
├── css/
├── js/
└── images/
```

The `database.db` file is created automatically when the Flask application starts for the first time.

## 6. Installation and Setup

### Step 1: Install Python

Install Python on your computer if it is not already installed.

### Step 2: Open the Project

Open the `College-Idea-Innovation-Hub` folder in Visual Studio Code.

### Step 3: Open the Terminal

In VS Code, select:

**Terminal → New Terminal**

Make sure the terminal is open in the project folder.

### Step 4: Create a Virtual Environment

Run:

```powershell
python -m venv .venv
```

### Step 5: Install Dependencies

Run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Step 6: Start the Application

Run:

```powershell
.\.venv\Scripts\python.exe app.py
```

### Step 7: Open the Website

Open a browser and visit:

http://127.0.0.1:5000

## 7. Demo Faculty Login

For local development and testing:

- **Email:** faculty@college.edu
- **Password:** Faculty@123

The application creates this demo faculty account when the database is initialized for the first time.

Students can create their own accounts using the registration page.

## 8. Database

The application uses SQLite to store:

- User accounts.
- Student ideas.
- Idea review statuses and faculty feedback.
- Collaboration requests.
- Contact form submissions.

## 9. Future Enhancements

Possible future improvements include:

- Email notifications for idea reviews.
- File and image uploads for idea proposals.
- Advanced idea search and filtering.
- Collaboration request management.
- Student and faculty profile enhancements.
- An administrator dashboard.
- Improved authentication and deployment security.

## 10. Conclusion

The College Idea Innovation Hub provides a centralized platform for student innovation and faculty evaluation. It combines a simple web interface with a Python backend and a database to organize idea submissions and encourage collaboration within a college.