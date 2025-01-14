from flask import Blueprint, render_template

bp = Blueprint(
    "dashboard",
    __name__,
    static_folder="static",
    static_url_path="static",
    template_folder="templates",
    url_prefix="/dashboard",
)


@bp.route("/", methods=["GET"])
def get_dashboard() -> str:
    return render_template("dashboard/dashboard.html")


@bp.route("/test-dashboard", methods=["GET"])
def test_get_dashboard() -> str:
    return render_template("dashboard/test_dashboard.html")
