from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Opportunity, Bookmark

opportunities_bp = Blueprint("opportunities", __name__)


@opportunities_bp.route("/")
@login_required
def list_opportunities():
    opp_type = request.args.get("type", "").strip()
    query = Opportunity.query
    if opp_type:
        query = query.filter(Opportunity.type == opp_type)
    opportunities = query.order_by(Opportunity.created_at.desc()).all()
    bookmarked_ids = {b.opportunity_id for b in current_user.bookmarks}
    return render_template(
        "opportunities/list.html", opportunities=opportunities, bookmarked_ids=bookmarked_ids, opp_type=opp_type
    )


@opportunities_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        opp_type = request.form.get("type", "").strip()
        location = request.form.get("location", "").strip()
        deadline = request.form.get("deadline", "").strip()
        link = request.form.get("link", "").strip()

        if not title or not opp_type:
            flash("Title and type are required", "error")
            return redirect(url_for("opportunities.add"))

        opportunity = Opportunity(
            title=title,
            company=company,
            type=opp_type,
            location=location,
            deadline=deadline,
            link=link,
            posted_by=current_user.id,
        )
        db.session.add(opportunity)
        db.session.commit()
        flash("Opportunity posted", "success")
        return redirect(url_for("opportunities.list_opportunities"))

    return render_template("opportunities/add.html")


@opportunities_bp.route("/<int:opp_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(opp_id):
    existing = Bookmark.query.filter_by(user_id=current_user.id, opportunity_id=opp_id).first()
    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Bookmark(user_id=current_user.id, opportunity_id=opp_id))
    db.session.commit()
    return redirect(request.referrer or url_for("opportunities.list_opportunities"))


@opportunities_bp.route("/bookmarks")
@login_required
def my_bookmarks():
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    return render_template("opportunities/bookmarks.html", bookmarks=bookmarks)
