import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Material

materials_bp = Blueprint("materials", __name__)


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@materials_bp.route("/")
@login_required
def list_materials():
    subject = request.args.get("subject", "").strip()
    query = Material.query
    if subject:
        query = query.filter(Material.subject.ilike(f"%{subject}%"))
    materials = query.order_by(Material.created_at.desc()).all()
    return render_template("materials/list.html", materials=materials, subject=subject)


@materials_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        subject = request.form.get("subject", "").strip()
        tags = request.form.get("tags", "").strip()
        file = request.files.get("file")

        if not title or not subject or not file or file.filename == "":
            flash("Title, subject and a file are all required", "error")
            return redirect(url_for("materials.upload"))

        if not allowed_file(file.filename):
            flash("File type not allowed", "error")
            return redirect(url_for("materials.upload"))

        safe_name = secure_filename(file.filename)
        unique_name = f"{datetime.utcnow().timestamp():.0f}_{safe_name}"
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))

        material = Material(
            title=title,
            subject=subject,
            tags=tags,
            filename=unique_name,
            uploaded_by=current_user.id,
        )
        db.session.add(material)
        db.session.commit()
        flash("Material uploaded", "success")
        return redirect(url_for("materials.list_materials"))

    return render_template("materials/upload.html")


@materials_bp.route("/download/<int:material_id>")
@login_required
def download(material_id):
    material = Material.query.get_or_404(material_id)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"], material.filename, as_attachment=True, download_name=material.title
    )
