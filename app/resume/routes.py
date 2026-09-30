from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app import db
from app.models import Resume

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/build", methods=["GET", "POST"])
@login_required
def build():
    resume = Resume.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        if not resume:
            resume = Resume(user_id=current_user.id)
            db.session.add(resume)

        resume.full_name = request.form.get("full_name", "").strip()
        resume.phone = request.form.get("phone", "").strip()
        resume.education = request.form.get("education", "").strip()
        resume.skills = request.form.get("skills", "").strip()
        resume.projects = request.form.get("projects", "").strip()
        resume.experience = request.form.get("experience", "").strip()

        db.session.commit()
        flash("Resume saved", "success")
        return redirect(url_for("resume.build"))

    return render_template("resume/build.html", resume=resume)


@resume_bp.route("/pdf")
@login_required
def download_pdf():
    resume = Resume.query.filter_by(user_id=current_user.id).first()
    if not resume:
        flash("Fill in your resume details first", "error")
        return redirect(url_for("resume.build"))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], spaceBefore=14, spaceAfter=6)
    name_style = ParagraphStyle("Name", parent=styles["Title"], alignment=0)

    story = [
        Paragraph(resume.full_name or current_user.name, name_style),
        Paragraph(f"{current_user.email} | {resume.phone or ''}", styles["Normal"]),
    ]

    sections = [
        ("Education", resume.education),
        ("Skills", resume.skills),
        ("Projects", resume.projects),
        ("Experience", resume.experience),
    ]
    for heading, content in sections:
        if content:
            story.append(Paragraph(heading, heading_style))
            for line in content.splitlines():
                if line.strip():
                    story.append(Paragraph(line.strip(), styles["Normal"]))
                    story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{(resume.full_name or current_user.name).replace(' ', '_')}_resume.pdf",
        mimetype="application/pdf",
    )
