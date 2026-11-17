import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from werkzeug.utils import secure_filename
from xml.sax.saxutils import escape

from src.ai_summary import generate_summary
from src.anomaly_detection import detect_anomalies
from src.data_cleaning import clean_data
from src.data_loader import load_data
from src.eda import perform_eda
from src.email_alert import send_email
from src.gemini_summary import generate_ai_summary
from src.visualization import create_visualizations


BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "instance" / "datasets"
MAX_UPLOAD_BYTES = 32 * 1024 * 1024
DATASET_ID_PATTERN = re.compile(r"^web_[a-f0-9]{32}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_bytes(32)
app.config.update(
    MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _owner_token():
    token = session.get("owner_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["owner_token"] = token
    return token


def _owner_hash():
    return hashlib.sha256(_owner_token().encode("utf-8")).hexdigest()


def _dataset_dir(dataset_id):
    if not DATASET_ID_PATTERN.fullmatch(dataset_id or ""):
        abort(404)
    return DATASETS_DIR / dataset_id


def _manifest_path(dataset_id):
    return _dataset_dir(dataset_id) / "manifest.json"


def _save_manifest(manifest):
    path = _manifest_path(manifest["id"])
    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    temporary_path.replace(path)


def _get_dataset(dataset_id):
    path = _manifest_path(dataset_id)
    if not path.is_file():
        abort(404)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Could not read dataset metadata for %s", dataset_id)
        abort(500)
    if not hmac.compare_digest(manifest.get("owner_hash", ""), _owner_hash()):
        abort(404)
    return manifest


def _read_source(dataset_id):
    source_path = _dataset_dir(dataset_id) / "source.csv"
    dataframe = load_data(str(source_path))
    if dataframe is None or dataframe.empty:
        raise ValueError(
            "The uploaded CSV could not be read or contains no data rows."
        )
    return dataframe


def _read_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except (OSError, UnicodeError, pd.errors.ParserError) as error:
        logger.exception("Could not read generated dataset %s", path)
        raise RuntimeError("The generated dataset could not be read.") from error


def _format_table(dataframe):
    return dataframe.to_html(
        classes="data-table",
        index=False,
        border=0,
        escape=True,
        na_rep="—",
    )


def _create_pdf_report(summary, destination):
    styles = {
        "title": ParagraphStyle(
            "ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=colors.HexColor("#132638"),
            spaceAfter=12,
        ),
        "body": ParagraphStyle(
            "ReportBody",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#263746"),
            wordWrap="CJK",
        ),
    }
    story = []
    for index, line in enumerate(summary.splitlines()):
        safe_line = escape(line.encode("latin-1", "replace").decode("latin-1"))
        if not safe_line:
            story.append(Spacer(1, 5))
        else:
            story.append(Paragraph(safe_line, styles["title" if index == 0 else "body"]))
    document = SimpleDocTemplate(
        str(destination),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title="Anomaly Intelligence Analysis Report",
        author="ANOMALY INTELLIGENCE",
    )
    document.build(story)


def _wants_json_response():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def _style_figure(figure):
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#c5d3e2", "family": "Inter, sans-serif", "size": 11},
        margin={"l": 18, "r": 18, "t": 24, "b": 18},
        colorway=["#49e7f2", "#9d7bff", "#64e0b2", "#f7bd66", "#fb7299"],
        legend={"font": {"color": "#c5d3e2"}},
    )
    return figure


def _build_charts(dataframe):
    charts = []
    numeric_columns = [
        column
        for column in dataframe.select_dtypes(include="number").columns
        if column != "Anomaly" and dataframe[column].nunique(dropna=True) > 1
    ]
    categorical_columns = dataframe.select_dtypes(
        include=["object", "category", "bool", "str"]
    ).columns.tolist()

    for column in numeric_columns[:3]:
        values = dataframe[column].replace([np.inf, -np.inf], np.nan)
        chart = px.histogram(
            x=values.dropna(),
            nbins=28,
            title=f"{column} · distribution",
            labels={"x": column, "y": "Records"},
        )
        charts.append(
            {
                "title": f"{column} distribution",
                "figure": pio.to_json(_style_figure(chart), validate=True),
            }
        )

    for column in categorical_columns[:3]:
        counts = dataframe[column].fillna("Missing").astype(str).value_counts().head(8)
        chart = px.bar(
            x=counts.index.tolist(),
            y=counts.values.tolist(),
            title=f"{column} · top values",
            labels={"x": column, "y": "Records"},
        )
        chart.update_layout(xaxis={"tickangle": -25})
        charts.append(
            {
                "title": f"{column} categories",
                "figure": pio.to_json(_style_figure(chart), validate=True),
            }
        )

    if len(numeric_columns) >= 2:
        correlation = dataframe[numeric_columns[:12]].corr(numeric_only=True)
        chart = px.imshow(
            correlation,
            text_auto=".2f",
            color_continuous_scale="Teal",
            zmin=-1,
            zmax=1,
            title="Feature correlation",
        )
        charts.append(
            {
                "title": "Feature correlation",
                "figure": pio.to_json(_style_figure(chart), validate=True),
            }
        )

    if "Anomaly" in dataframe.columns:
        counts = dataframe["Anomaly"].value_counts().sort_index()
        labels = ["Anomaly" if value == -1 else "Normal" for value in counts.index]
        chart = px.bar(
            x=labels,
            y=counts.values,
            title="Isolation Forest classification",
            labels={"x": "Record class", "y": "Records"},
            color=labels,
            color_discrete_map={"Anomaly": "#9d7bff", "Normal": "#49e7f2"},
        )
        chart.update_layout(showlegend=False)
        charts.insert(
            0,
            {
                "title": "Anomaly classification",
                "figure": pio.to_json(_style_figure(chart), validate=True),
            },
        )

    return charts


def _owned_datasets():
    if not DATASETS_DIR.is_dir():
        return []
    owner_hash = _owner_hash()
    datasets = []
    for directory in DATASETS_DIR.iterdir():
        path = directory / "manifest.json"
        if not directory.is_dir() or not path.is_file():
            continue
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("Skipping unreadable dataset manifest %s", path)
            continue
        if hmac.compare_digest(manifest.get("owner_hash", ""), owner_hash):
            datasets.append(manifest)
    return sorted(datasets, key=lambda item: item.get("created_at", ""), reverse=True)


def _dashboard_context(manifest):
    dataframe = _read_source(manifest["id"])
    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
    categorical_columns = dataframe.select_dtypes(
        include=["object", "category", "bool", "str"]
    ).columns.tolist()
    missing = dataframe.isna().sum()
    missing = missing[missing > 0].to_dict()
    charts = _build_charts(dataframe)
    analysis_frame = dataframe
    cleaned_path = BASE_DIR / "data" / "processed" / manifest["id"] / "cleaned_data.csv"
    if cleaned_path.is_file():
        analysis_frame = _read_csv(cleaned_path)
        charts = _build_charts(analysis_frame)
    analyzed_path = (
        BASE_DIR / "data" / "processed" / manifest["id"] / "analysis_data.csv"
    )
    if manifest.get("status") == "analyzed" and analyzed_path.is_file():
        analysis_frame = _read_csv(analyzed_path)
        charts = _build_charts(analysis_frame)

    anomaly_preview = ""
    normal_preview = ""
    if manifest.get("status") == "analyzed" and "Anomaly" in analysis_frame.columns:
        anomaly_preview = _format_table(
            analysis_frame.loc[analysis_frame["Anomaly"] == -1].head(8)
        )
        normal_preview = _format_table(
            analysis_frame.loc[analysis_frame["Anomaly"] == 1].head(8)
        )

    numerical_summary = None
    if numeric_columns:
        summary_frame = analysis_frame.select_dtypes(include="number")
        summary_frame = summary_frame.drop(
            columns=["Anomaly"], errors="ignore"
        )
        if not summary_frame.empty:
            numerical_summary = _format_table(
                summary_frame.describe().round(2).transpose().reset_index()
            )

    categorical_summary = []
    for column in categorical_columns[:8]:
        counts = dataframe[column].fillna("Missing").astype(str).value_counts().head(6)
        categorical_summary.append(
            {"column": column, "values": list(zip(counts.index, counts.values))}
        )

    report_path = BASE_DIR / "reports" / manifest["id"]
    summary_path = report_path / "summary.txt"
    ai_summary_path = report_path / "ai_summary.txt"
    graphs_dir = report_path / "graphs"
    graphs = []
    if manifest.get("status") == "analyzed" and graphs_dir.is_dir():
        graphs = sorted(
            path.name for path in graphs_dir.iterdir() if path.is_file()
        )

    return {
        "manifest": manifest,
        "columns": dataframe.columns.tolist(),
        "preview": _format_table(dataframe.head(8)),
        "rows": len(dataframe),
        "column_count": len(dataframe.columns),
        "missing": missing,
        "missing_total": int(dataframe.isna().sum().sum()),
        "duplicates": int(dataframe.duplicated().sum()),
        "numeric_count": len(numeric_columns),
        "categorical_count": len(categorical_columns),
        "charts": charts,
        "anomaly_preview": anomaly_preview,
        "normal_preview": normal_preview,
        "numerical_summary": numerical_summary,
        "categorical_summary": categorical_summary,
        "summary": (
            summary_path.read_text(encoding="utf-8")
            if manifest.get("status") == "analyzed" and summary_path.is_file()
            else ""
        ),
        "ai_summary": (
            ai_summary_path.read_text(encoding="utf-8")
            if ai_summary_path.is_file()
            else ""
        ),
        "graphs": graphs,
    }


@app.context_processor
def inject_csrf_token():
    return {
        "csrf_token": lambda: session.setdefault(
            "csrf_token", secrets.token_urlsafe(32)
        )
    }


@app.before_request
def validate_csrf_token():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        expected = session.get("csrf_token", "")
        provided = request.form.get("csrf_token", "")
        if not expected or not hmac.compare_digest(expected, provided):
            abort(400, description="The form expired. Reload the page and try again.")


@app.get("/")
def home():
    datasets = _owned_datasets()
    analyzed = [item for item in datasets if item.get("status") == "analyzed"]
    records = sum(item.get("rows", 0) for item in analyzed)
    anomalies = sum(item.get("anomaly_count", 0) for item in analyzed)
    return render_template(
        "home.html",
        datasets=datasets[:4],
        dataset_count=len(datasets),
        analyzed_count=len(analyzed),
        records=records,
        anomalies=anomalies,
    )


@app.post("/upload")
def upload_dataset():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        flash("Choose a CSV file to begin.", "error")
        return redirect(url_for("home"))
    if Path(uploaded_file.filename).suffix.lower() != ".csv":
        flash("Only CSV files are supported.", "error")
        return redirect(url_for("home"))

    filename = secure_filename(uploaded_file.filename) or "dataset.csv"
    dataset_id = f"web_{uuid.uuid4().hex}"
    dataset_dir = _dataset_dir(dataset_id)
    dataset_dir.mkdir(parents=True, exist_ok=False)
    source_path = dataset_dir / "source.csv"
    uploaded_file.save(source_path)

    try:
        dataframe = load_data(str(source_path))
        if dataframe is None or dataframe.empty:
            raise ValueError(
                "The CSV could not be parsed or contains no data rows."
            )
    except Exception as error:
        source_path.unlink(missing_ok=True)
        dataset_dir.rmdir()
        if isinstance(error, ValueError):
            flash(str(error), "error")
        else:
            logger.exception("CSV upload validation failed")
            flash("The CSV could not be validated. Check its encoding and format.", "error")
        return redirect(url_for("home"))

    manifest = {
        "id": dataset_id,
        "owner_hash": _owner_hash(),
        "filename": filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "uploaded",
        "rows": int(len(dataframe)),
        "columns": int(len(dataframe.columns)),
    }
    _save_manifest(manifest)
    flash(f"{filename} is ready to explore.", "success")
    return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))


@app.get("/datasets/<dataset_id>")
def dataset_dashboard(dataset_id):
    manifest = _get_dataset(dataset_id)
    try:
        context = _dashboard_context(manifest)
    except (ValueError, RuntimeError):
        logger.exception("Could not build dashboard for %s", dataset_id)
        flash("The dataset could not be loaded. Please upload it again.", "error")
        return redirect(url_for("home"))
    return render_template("dashboard.html", **context)


@app.post("/datasets/<dataset_id>/clean")
def clean_dataset(dataset_id):
    manifest = _get_dataset(dataset_id)
    try:
        original = _read_source(dataset_id)
        cleaned = clean_data(original, dataset_id)
        if cleaned is None or cleaned.empty:
            raise ValueError("Cleaning did not produce any data rows.")
        manifest.update(
            {
                "status": "cleaned",
                "cleaning": {
                    "input_rows": int(len(original)),
                    "output_rows": int(len(cleaned)),
                    "duplicates_removed": int(original.duplicated().sum()),
                    "missing_before": int(original.isna().sum().sum()),
                    "missing_after": int(cleaned.isna().sum().sum()),
                },
            }
        )
        for key in ("anomaly_count", "normal_count", "anomaly_percent", "graphs"):
            manifest.pop(key, None)
        _save_manifest(manifest)
        flash("Data cleaning completed. Review the results below.", "success")
    except (ValueError, OSError, RuntimeError) as error:
        logger.exception("Cleaning failed for dataset %s", dataset_id)
        flash(f"Cleaning failed: {error}", "error")
    return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))


@app.post("/datasets/<dataset_id>/analyze")
def analyze_dataset(dataset_id):
    manifest = _get_dataset(dataset_id)
    stage = "loading the uploaded CSV"
    cleaned = None
    try:
        original = _read_source(dataset_id)
        stage = "cleaning the dataset"
        cleaned = clean_data(original, dataset_id)
        if cleaned is None or cleaned.empty:
            raise ValueError("Cleaning did not produce any data rows.")
        manifest.update(
            {
                "status": "analyzing",
                "cleaning": {
                    "input_rows": int(len(original)),
                    "output_rows": int(len(cleaned)),
                    "duplicates_removed": int(original.duplicated().sum()),
                    "missing_before": int(original.isna().sum().sum()),
                    "missing_after": int(cleaned.isna().sum().sum()),
                },
            }
        )
        for key in ("anomaly_count", "normal_count", "anomaly_percent", "graphs"):
            manifest.pop(key, None)
        _save_manifest(manifest)
        old_ai_summary = BASE_DIR / "reports" / dataset_id / "ai_summary.txt"
        if old_ai_summary.is_file():
            old_ai_summary.unlink()

        stage = "running exploratory data analysis"
        perform_eda(cleaned)
        stage = "running Isolation Forest"
        analyzed = detect_anomalies(cleaned, dataset_id)
        processed_dir = BASE_DIR / "data" / "processed" / dataset_id
        analyzed.to_csv(processed_dir / "analysis_data.csv", index=False)

        stage = "generating visualization files"
        graph_paths = create_visualizations(analyzed, dataset_id)
        if not graph_paths or any(not Path(path).is_file() for path in graph_paths):
            raise RuntimeError(
                "The visualization pipeline did not produce its graph files."
            )

        stage = "generating the text summary"
        summary = generate_summary(analyzed, dataset_id)
        if not summary:
            raise RuntimeError("The analysis summary was empty.")
        report_dir = BASE_DIR / "reports" / dataset_id
        summary_path = report_dir / "summary.txt"
        if not summary_path.is_file():
            raise RuntimeError("The analysis summary file was not created.")

        anomaly_count = int((analyzed["Anomaly"] == -1).sum())
        normal_count = int((analyzed["Anomaly"] == 1).sum())
        anomaly_path = processed_dir / "anomalies.csv"
        if not anomaly_path.is_file():
            raise RuntimeError("The anomaly CSV was not created.")
        exported_anomalies = _read_csv(anomaly_path)
        if len(exported_anomalies) != anomaly_count:
            raise RuntimeError("The anomaly CSV does not match the model results.")

        stage = "generating the PDF report"
        pdf_path = report_dir / "analysis_report.pdf"
        _create_pdf_report(summary, pdf_path)
        if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
            raise RuntimeError("The PDF report was not created.")

        manifest.update(
            {
                "status": "analyzed",
                "rows": int(len(analyzed)),
                "anomaly_count": anomaly_count,
                "normal_count": normal_count,
                "anomaly_percent": round(anomaly_count / len(analyzed) * 100, 2),
                "graphs": [Path(path).name for path in graph_paths],
            }
        )
        _save_manifest(manifest)
        message = (
            f"Analysis complete: {anomaly_count:,} anomalies found in "
            f"{len(analyzed):,} records. Reports and charts are ready."
        )
        flash(message, "success")
        if _wants_json_response():
            return jsonify(
                ok=True,
                status=manifest["status"],
                message=message,
                redirect_url=url_for("dataset_dashboard", dataset_id=dataset_id),
            )
    except Exception as error:
        logger.exception("Analysis failed while %s for dataset %s", stage, dataset_id)
        manifest["status"] = "cleaned" if cleaned is not None else "uploaded"
        for key in ("anomaly_count", "normal_count", "anomaly_percent", "graphs"):
            manifest.pop(key, None)
        _save_manifest(manifest)
        if isinstance(error, (ValueError, OSError, RuntimeError)):
            message = f"Analysis could not be completed: {error}"
            status_code = 422
        else:
            message = f"Analysis failed while {stage}. Check the server log for details."
            status_code = 500
        flash(message, "error")
        if _wants_json_response():
            return jsonify(
                ok=False,
                status=manifest["status"],
                message=message,
            ), status_code
    return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))


@app.post("/datasets/<dataset_id>/ai-summary")
def create_ai_summary(dataset_id):
    manifest = _get_dataset(dataset_id)
    if manifest.get("status") != "analyzed":
        flash("Run dataset analysis before generating an AI report.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    summary_path = BASE_DIR / "reports" / dataset_id / "summary.txt"
    if not summary_path.is_file():
        flash("The analysis report is unavailable. Run analysis again.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    try:
        summary = summary_path.read_text(encoding="utf-8")
        ai_summary = generate_ai_summary(summary, dataset_id, strict=True)
        if not ai_summary or ai_summary == summary:
            raise RuntimeError("Gemini did not generate a distinct AI report.")
        flash("Gemini intelligence report generated.", "success")
    except RuntimeError as error:
        logger.exception("AI summary generation failed for dataset %s", dataset_id)
        flash(str(error), "error")
    return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))


@app.post("/datasets/<dataset_id>/email")
def email_report(dataset_id):
    manifest = _get_dataset(dataset_id)
    if manifest.get("status") != "analyzed":
        flash("Run dataset analysis before sending a report.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    recipient = request.form.get("recipient", "").strip()
    if len(recipient) > 254 or not EMAIL_PATTERN.fullmatch(recipient):
        flash("Enter a valid recipient email address.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    report_dir = BASE_DIR / "reports" / dataset_id
    ai_path = report_dir / "ai_summary.txt"
    summary_path = report_dir / "summary.txt"
    report_path = ai_path if ai_path.is_file() else summary_path
    if not report_path.is_file():
        flash("There is no generated report to send yet.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    try:
        sent = send_email(
            report_path.read_text(encoding="utf-8"),
            recipient_email=recipient,
        )
    except Exception:
        logger.exception("Email delivery failed for dataset %s", dataset_id)
        flash("Email delivery failed. Check the SMTP configuration and try again.", "error")
    else:
        if sent:
            flash(f"Report sent to {recipient}.", "success")
        else:
            flash(
                "Email was not sent. Configure SENDER_EMAIL and EMAIL_APP_PASSWORD.",
                "error",
            )
    return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))


@app.get("/datasets/<dataset_id>/download/<kind>")
def download_report(dataset_id, kind):
    manifest = _get_dataset(dataset_id)
    if kind == "cleaned":
        if manifest.get("status") not in {"cleaned", "analyzed"}:
            abort(404)
    elif manifest.get("status") != "analyzed":
        abort(404)
    report_dir = BASE_DIR / "reports" / dataset_id
    processed_dir = BASE_DIR / "data" / "processed" / dataset_id
    files = {
        "cleaned": (processed_dir / "cleaned_data.csv", "cleaned_data.csv"),
        "anomalies": (processed_dir / "anomalies.csv", "anomalies.csv"),
        "summary": (report_dir / "summary.txt", "analysis_summary.txt"),
        "pdf": (report_dir / "analysis_report.pdf", "analysis_report.pdf"),
        "ai-summary": (report_dir / "ai_summary.txt", "ai_summary.txt"),
    }
    if kind not in files:
        abort(404)
    path, download_name = files[kind]
    if not path.is_file():
        flash("That report is not available yet.", "error")
        return redirect(url_for("dataset_dashboard", dataset_id=dataset_id))
    return send_file(path, as_attachment=True, download_name=download_name)


@app.get("/datasets/<dataset_id>/graphs/<filename>")
def dataset_graph(dataset_id, filename):
    manifest = _get_dataset(dataset_id)
    if manifest.get("status") != "analyzed" or filename not in manifest.get(
        "graphs", []
    ):
        abort(404)
    return send_from_directory(
        BASE_DIR / "reports" / dataset_id / "graphs",
        filename,
        as_attachment=False,
    )


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(413)
def handle_request_error(error):
    messages = {
        400: "This form is invalid or has expired. Reload the page and try again.",
        404: "That page or report could not be found.",
        413: "This CSV is larger than the 32 MB upload limit.",
    }
    return (
        render_template(
            "error.html",
            status_code=error.code,
            message=messages.get(error.code, "The request could not be completed."),
        ),
        error.code,
    )


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "").lower() == "true",
    )
