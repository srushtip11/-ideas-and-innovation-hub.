import os
import sqlite3
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    send_from_directory
)

from werkzeug.security import generate_password_hash, check_password_hash


# ==========================================================
# 1. APPLICATION CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATABASE = os.path.join(BASE_DIR, "database.db")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=None
)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key-change-before-deployment"
)


# ==========================================================
# 2. DATABASE CONNECTION
# ==========================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    connection = get_db()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            department TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            problem TEXT NOT NULL,
            solution TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            faculty_feedback TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS collaborations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (idea_id) REFERENCES ideas(id),
            FOREIGN KEY (student_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create a demo faculty account if it does not exist.
    faculty = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        ("faculty@college.edu",)
    ).fetchone()

    if faculty is None:
        connection.execute("""
            INSERT INTO users
                (name, email, password_hash, department, role)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Faculty Member",
            "faculty@college.edu",
            generate_password_hash("Faculty@123"),
            "Innovation Cell",
            "faculty"
        ))

    connection.commit()
    connection.close()


# ==========================================================
# 3. LOGIN AND ACCESS CONTROL
# ==========================================================

def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        return view_function(*args, **kwargs)

    return wrapped_view


def student_required(view_function):
    @wraps(view_function)
    @login_required
    def wrapped_view(*args, **kwargs):
        if session.get("user_role") != "student":
            abort(403)

        return view_function(*args, **kwargs)

    return wrapped_view


def faculty_required(view_function):
    @wraps(view_function)
    @login_required
    def wrapped_view(*args, **kwargs):
        if session.get("user_role") != "faculty":
            abort(403)

        return view_function(*args, **kwargs)

    return wrapped_view


# ==========================================================
# 4. CSS, JAVASCRIPT AND IMAGE FILES
# ==========================================================

@app.route("/css/<path:filename>")
def css_files(filename):
    return send_from_directory(
        os.path.join(STATIC_DIR, "css"),
        filename
    )


@app.route("/js/<path:filename>")
def js_files(filename):
    return send_from_directory(
        os.path.join(STATIC_DIR, "js"),
        filename
    )


@app.route("/images/<path:filename>")
def image_files(filename):
    return send_from_directory(
        os.path.join(STATIC_DIR, "images"),
        filename
    )


# ==========================================================
# 5. HOME PAGE
# ==========================================================

@app.route("/")
def index():
    connection = get_db()

    approved_count = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE status = 'Approved'
    """).fetchone()[0]

    student_count = connection.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'student'
    """).fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        approved_count=approved_count,
        student_count=student_count
    )


# ==========================================================
# 6. ABOUT PAGE
# ==========================================================

@app.route("/about")
def about():
    return render_template("about.html")


# ==========================================================
# 7. CONTACT PAGE
# ==========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            return render_template(
                "contact.html",
                error="Please complete all fields."
            )

        connection = get_db()

        connection.execute("""
            INSERT INTO contact_messages (name, email, message)
            VALUES (?, ?, ?)
        """, (name, email, message))

        connection.commit()
        connection.close()

        return render_template(
            "contact.html",
            success="Your message has been submitted successfully."
        )

    return render_template("contact.html")


# ==========================================================
# 8. STUDENT REGISTRATION
# ==========================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        department = request.form.get("department", "").strip()
        password = request.form.get("password", "")

        if not all([name, email, department, password]):
            return render_template(
                "register.html",
                error="Please complete all fields."
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must contain at least 8 characters."
            )

        connection = get_db()

        try:
            cursor = connection.execute("""
                INSERT INTO users
                    (name, email, password_hash, department, role)
                VALUES (?, ?, ?, ?, 'student')
            """, (
                name,
                email,
                generate_password_hash(password),
                department
            ))

            connection.commit()
            new_user_id = cursor.lastrowid

        except sqlite3.IntegrityError:
            connection.close()

            return render_template(
                "register.html",
                error="This email is already registered."
            )

        connection.close()

        session.clear()
        session["user_id"] = new_user_id
        session["user_name"] = name
        session["user_role"] = "student"

        flash("Registration successful!", "success")

        return redirect(url_for("student_dashboard"))

    return render_template("register.html")


# ==========================================================
# 9. LOGIN
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        connection = get_db()

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            if user["role"] == "faculty":
                return redirect(url_for("faculty_dashboard"))

            return redirect(url_for("student_dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# ==========================================================
# 10. LOGOUT
# ==========================================================

@app.route("/logout")
def logout():
    session.clear()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("index"))


# ==========================================================
# 11. PUBLIC IDEAS PAGE
# ==========================================================

@app.route("/ideas")
def ideas():
    connection = get_db()

    all_ideas = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.status = 'Approved'
        ORDER BY ideas.created_at DESC
    """).fetchall()

    connection.close()

    return render_template(
        "ideas/ideas.html",
        ideas=all_ideas
    )


# ==========================================================
# 12. IDEA DETAILS
# ==========================================================

@app.route("/ideas/<int:idea_id>")
def idea_details(idea_id):
    connection = get_db()

    idea = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.id = ?
    """, (idea_id,)).fetchone()

    connection.close()

    if idea is None:
        abort(404)

    if idea["status"] != "Approved":

        is_owner = (
            session.get("user_role") == "student"
            and session.get("user_id") == idea["student_id"]
        )

        is_faculty = session.get("user_role") == "faculty"

        if not is_owner and not is_faculty:
            abort(403)

    return render_template(
        "ideas/idea-details.html",
        idea=idea
    )


# ==========================================================
# 13. STUDENT DASHBOARD
# ==========================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():
    student_id = session["user_id"]

    connection = get_db()

    my_total = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE student_id = ?
    """, (student_id,)).fetchone()[0]

    my_pending = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE student_id = ?
        AND status = 'Pending'
    """, (student_id,)).fetchone()[0]

    my_approved = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE student_id = ?
        AND status = 'Approved'
    """, (student_id,)).fetchone()[0]

    recent_ideas = connection.execute("""
        SELECT *
        FROM ideas
        WHERE student_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (student_id,)).fetchall()

    connection.close()

    return render_template(
        "student/dashboard.html",
        my_total=my_total,
        my_pending=my_pending,
        my_approved=my_approved,
        recent_ideas=recent_ideas
    )


# ==========================================================
# 14. SUBMIT AN IDEA
# ==========================================================

@app.route("/student/submit-idea", methods=["GET", "POST"])
@student_required
def submit_idea():
    if request.method == "POST":

        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        problem = request.form.get("problem", "").strip()
        solution = request.form.get("solution", "").strip()
        description = request.form.get("description", "").strip()

        if not all([
            title,
            category,
            problem,
            solution,
            description
        ]):
            return render_template(
                "student/submit-idea.html",
                error="Please complete all fields."
            )

        connection = get_db()

        connection.execute("""
            INSERT INTO ideas (
                student_id,
                title,
                category,
                problem,
                solution,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            title,
            category,
            problem,
            solution,
            description
        ))

        connection.commit()
        connection.close()

        flash(
            "Your idea has been submitted for review.",
            "success"
        )

        return redirect(url_for("my_ideas"))

    return render_template("student/submit-idea.html")


# ==========================================================
# 15. STUDENT'S IDEAS
# ==========================================================

@app.route("/student/my-ideas")
@student_required
def my_ideas():
    connection = get_db()

    ideas_list = connection.execute("""
        SELECT *
        FROM ideas
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template(
        "student/my-ideas.html",
        ideas=ideas_list
    )


# ==========================================================
# 16. STUDENT PROFILE
# ==========================================================

@app.route("/student/profile", methods=["GET", "POST"])
@student_required
def student_profile():
    connection = get_db()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not name or not department:

            user = connection.execute("""
                SELECT *
                FROM users
                WHERE id = ?
            """, (session["user_id"],)).fetchone()

            connection.close()

            return render_template(
                "student/profile.html",
                user=user,
                error="Name and department are required."
            )

        connection.execute("""
            UPDATE users
            SET name = ?, department = ?
            WHERE id = ?
        """, (
            name,
            department,
            session["user_id"]
        ))

        connection.commit()

        session["user_name"] = name

        flash("Your profile has been updated.", "success")

    user = connection.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (session["user_id"],)).fetchone()

    connection.close()

    return render_template(
        "student/profile.html",
        user=user
    )


# ==========================================================
# 17. COLLABORATION REQUEST
# ==========================================================

@app.route(
    "/ideas/<int:idea_id>/collaboration",
    methods=["GET", "POST"]
)
@student_required
def collaboration(idea_id):
    connection = get_db()

    idea = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.id = ?
        AND ideas.status = 'Approved'
    """, (idea_id,)).fetchone()

    if idea is None:
        connection.close()
        abort(404)

    if request.method == "POST":

        message = request.form.get("message", "").strip()

        if not message:
            connection.close()

            return render_template(
                "ideas/collaboration.html",
                idea=idea,
                error="Please enter a collaboration message."
            )

        connection.execute("""
            INSERT INTO collaborations (
                idea_id,
                student_id,
                message
            )
            VALUES (?, ?, ?)
        """, (
            idea_id,
            session["user_id"],
            message
        ))

        connection.commit()
        connection.close()

        return render_template(
            "ideas/collaboration.html",
            idea=idea,
            success="Your collaboration request has been submitted."
        )

    connection.close()

    return render_template(
        "ideas/collaboration.html",
        idea=idea
    )


# ==========================================================
# 18. FACULTY DASHBOARD
# ==========================================================

@app.route("/faculty/dashboard")
@faculty_required
def faculty_dashboard():
    connection = get_db()

    total_ideas = connection.execute("""
        SELECT COUNT(*) FROM ideas
    """).fetchone()[0]

    pending_count = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE status = 'Pending'
    """).fetchone()[0]

    approved_count = connection.execute("""
        SELECT COUNT(*)
        FROM ideas
        WHERE status = 'Approved'
    """).fetchone()[0]

    total_students = connection.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'student'
    """).fetchone()[0]

    connection.close()

    return render_template(
        "faculty/dashboard.html",
        total_ideas=total_ideas,
        pending_count=pending_count,
        approved_count=approved_count,
        total_students=total_students
    )


# ==========================================================
# 19. FACULTY: PENDING IDEAS
# ==========================================================

@app.route("/faculty/pending-ideas")
@faculty_required
def pending_ideas():
    connection = get_db()

    ideas_list = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.status = 'Pending'
        ORDER BY ideas.created_at ASC
    """).fetchall()

    connection.close()

    return render_template(
        "faculty/pending-ideas.html",
        ideas=ideas_list
    )


# ==========================================================
# 20. FACULTY: REVIEW AN IDEA
# ==========================================================

@app.route(
    "/faculty/idea-review/<int:idea_id>",
    methods=["GET", "POST"]
)
@faculty_required
def idea_review(idea_id):
    connection = get_db()

    if request.method == "POST":

        status = request.form.get("status", "").strip()

        faculty_feedback = request.form.get(
            "faculty_feedback",
            ""
        ).strip()

        if status not in ["Pending", "Approved", "Rejected"]:
            connection.close()
            abort(400)

        cursor = connection.execute("""
            UPDATE ideas
            SET status = ?, faculty_feedback = ?
            WHERE id = ?
        """, (
            status,
            faculty_feedback,
            idea_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            connection.close()
            abort(404)

        connection.close()

        flash("The idea review has been saved.", "success")

        return redirect(url_for("pending_ideas"))

    idea = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.id = ?
    """, (idea_id,)).fetchone()

    connection.close()

    if idea is None:
        abort(404)

    return render_template(
        "faculty/idea-review.html",
        idea=idea
    )


# ==========================================================
# 21. FACULTY: APPROVED IDEAS
# ==========================================================

@app.route("/faculty/approved-ideas")
@faculty_required
def approved_ideas():
    connection = get_db()

    ideas_list = connection.execute("""
        SELECT
            ideas.*,
            users.name AS student_name,
            users.department AS student_department
        FROM ideas
        JOIN users ON ideas.student_id = users.id
        WHERE ideas.status = 'Approved'
        ORDER BY ideas.created_at DESC
    """).fetchall()

    connection.close()

    return render_template(
        "faculty/approved-ideas.html",
        ideas=ideas_list
    )


# ==========================================================
# 22. ERROR HANDLERS
# ==========================================================

@app.errorhandler(403)
def forbidden(error):
    return """
        <h1>403 - Access Denied</h1>
        <p>You do not have permission to access this page.</p>
        <a href="/">Return to Home</a>
    """, 403


@app.errorhandler(404)
def page_not_found(error):
    return """
        <h1>404 - Page Not Found</h1>
        <p>The requested page could not be found.</p>
        <a href="/">Return to Home</a>
    """, 404


# ==========================================================
# 23. START THE APPLICATION
# ==========================================================

if __name__ == "__main__":
    init_db()

    print("College Idea Innovation Hub is starting...")
    print("Open http://127.0.0.1:5000 in your browser.")

    app.run(debug=True)