import os
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from database import db

from models import (
    User,
    Resume,
    Job,
    Analysis
)

from analyzer.resume_parser import extract_text
from analyzer.skill_extractor import extract_skills
from analyzer.job_matcher import calculate_match
from analyzer.recommendation import get_recommendations
from analyzer.job_api import search_jobs


# Load environment variables
load_dotenv()


# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)


# ==========================================
# Configuration
# ==========================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key"
)

# Render MySQL compatibility fix
db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/ai_resume_db")
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# Create uploads folder if not exists
os.makedirs(
    app.config["UPLOAD_FOLDER"],
    exist_ok=True
)


# ==========================================
# Initialize Database
# ==========================================

db.init_app(app)


# ==========================================
# Flask Login
# ==========================================

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(
        User,
        int(user_id)
    )


# ==========================================
# Home
# ==========================================

@app.route("/")
def home():
    jobs = Job.query.all()
    return render_template(
        "home.html",
        jobs=jobs
    )


# ==========================================
# Register
# ==========================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check fields
        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("register"))

        # Check password match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        # Create user
        user = User(name=name, email=email)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error registering user: {e}", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ==========================================
# Login
# ==========================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# ==========================================
# Logout
# ==========================================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ==========================================
# Dashboard
# ==========================================

@app.route("/dashboard")
@login_required
def dashboard():

    resumes = Resume.query.filter_by(user_id=current_user.id).all()

    analyses = (
        Analysis.query
        .join(Resume, Analysis.resume_id == Resume.id)
        .filter(Resume.user_id == current_user.id)
        .all()
    )

    return render_template(
        "dashboard.html",
        resumes=resumes,
        analyses=analyses
    )


# ==========================================
# Upload Resume
# ==========================================

@app.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():

    if request.method == "POST":

        file = request.files.get("resume")

        if not file or not file.filename:
            flash("Please select a resume file.", "danger")
            return redirect(url_for("upload"))

        filename = secure_filename(file.filename)
        allowed_extensions = (".pdf", ".docx")

        if not filename.lower().endswith(allowed_extensions):
            flash("Only PDF and DOCX files are allowed.", "danger")
            return redirect(url_for("upload"))

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(filepath)

        try:
            text = extract_text(filepath)

            if not text.strip():
                flash("Could not extract text from the resume.", "danger")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(url_for("upload"))

            skills = extract_skills(text)

            resume = Resume(
                user_id=current_user.id,
                filename=filename,
                resume_text=text,
                skills=", ".join(skills)
            )

            db.session.add(resume)
            db.session.commit()

            flash("Resume analyzed successfully.", "success")
            return redirect(url_for("result", resume_id=resume.id))

        except Exception as e:
            db.session.rollback()  # Handled session rollback
            if os.path.exists(filepath):
                os.remove(filepath)

            flash(f"Error while processing resume: {e}", "danger")

    return render_template("upload.html")


# ==========================================
# Delete Resume
# ==========================================

@app.route(
    "/delete-resume/<int:resume_id>",
    methods=["POST"]
)
@login_required
def delete_resume(resume_id):

    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        return "Unauthorized", 403

    try:
        # Delete Related Analyses
        Analysis.query.filter_by(resume_id=resume.id).delete(synchronize_session=False)

        # Delete Physical File
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], resume.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete Resume From Database
        db.session.delete(resume)
        db.session.commit()

        flash("Resume deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting resume: {e}", "danger")

    return redirect(url_for("dashboard"))


# ==========================================
# Resume Result / Job Matching
# ==========================================

@app.route("/result/<int:resume_id>")
@login_required
def result(resume_id):

    resume = Resume.query.get_or_404(resume_id)

    if resume.user_id != current_user.id:
        return "Unauthorized", 403

    resume_skills = [
        skill.strip().lower()
        for skill in (resume.skills.split(",") if resume.skills else [])
        if skill.strip()
    ]

    try:
        online_jobs = search_jobs(
            resume_skills,
            location="India",
            results_per_page=20
        )
    except Exception as e:
        flash(f"Unable to fetch online jobs: {e}", "danger")
        online_jobs = []

    results = []

    for online_job in online_jobs:

        class OnlineJob:
            pass

        job = OnlineJob()
        job.title = online_job.get("title", "Unknown Job")

        company_data = online_job.get("company", {})
        job.company = company_data.get("display_name", "Unknown Company") if isinstance(company_data, dict) else str(company_data)

        location_data = online_job.get("location", {})
        job.location = location_data.get("display_name", "India") if isinstance(location_data, dict) else str(location_data)

        job.description = online_job.get("description", "")

        tags = online_job.get("tags", [])
        job.required_skills = ", ".join(str(tag) for tag in tags) if isinstance(tags, list) else str(tags)

        try:
            match = calculate_match(
                resume.resume_text,
                resume_skills,
                job
            )
        except Exception as e:
            continue

        job_url = online_job.get("redirect_url", "#")

        results.append({
            "job": job,
            "score": match["score"],
            "skill_score": match["skill_score"],
            "text_score": match["text_score"],
            "title_score": match["title_score"],
            "matched": match["matched_skills"],
            "missing": match["missing_skills"],
            "job_skills": match["job_skills"],
            "url": job_url
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:10]

    recommendations = get_recommendations(results[0]["missing"]) if results else []

    return render_template(
        "result.html",
        resume=resume,
        results=results,
        recommendations=recommendations
    )


# ==========================================
# Jobs Page
# ==========================================

@app.route("/jobs")
def jobs():
    jobs_list = Job.query.all()
    return render_template("jobs.html", jobs=jobs_list)


# ==========================================
# Create Database Tables safely
# ==========================================

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization note: {e}")


# ==========================================
# Run Flask Application
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)