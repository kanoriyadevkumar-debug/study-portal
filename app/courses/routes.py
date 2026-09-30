from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/")
@login_required
def list_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    my_course_ids = {e.course_id for e in current_user.enrollments}
    return render_template("courses/list.html", courses=courses, my_course_ids=my_course_ids)


@courses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        modules_text = request.form.get("modules", "").strip()

        if not title:
            flash("Course title is required", "error")
            return redirect(url_for("courses.add"))

        course = Course(title=title, description=description, modules_text=modules_text)
        db.session.add(course)
        db.session.commit()
        flash("Course created", "success")
        return redirect(url_for("courses.list_courses"))

    return render_template("courses/add.html")


@courses_bp.route("/<int:course_id>")
@login_required
def detail(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    return render_template("courses/detail.html", course=course, enrollment=enrollment)


@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll(course_id):
    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not existing:
        db.session.add(Enrollment(user_id=current_user.id, course_id=course_id))
        db.session.commit()
        flash("Enrolled in course", "success")
    return redirect(url_for("courses.detail", course_id=course_id))


@courses_bp.route("/<int:course_id>/progress", methods=["POST"])
@login_required
def update_progress(course_id):
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first_or_404()
    progress = request.form.get("progress", type=int, default=0)
    enrollment.progress = max(0, min(100, progress))
    db.session.commit()
    return redirect(url_for("courses.detail", course_id=course_id))
