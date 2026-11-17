import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import matplotlib

import app as web_app
from src import (
    ai_summary,
    anomaly_detection,
    data_cleaning,
    gemini_summary,
    visualization,
)


class DashboardWorkflowTests(unittest.TestCase):
    def test_matplotlib_uses_headless_backend_for_flask_requests(self):
        self.assertEqual(matplotlib.get_backend().lower(), "agg")

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        root = Path(self.temporary_directory.name)
        self.generated_root = root
        self.datasets_root = root / "instance" / "datasets"
        processed_root = root / "data" / "processed"
        reports_root = root / "reports"

        self.patches = [
            patch.object(web_app, "BASE_DIR", root),
            patch.object(web_app, "DATASETS_DIR", self.datasets_root),
            patch.object(data_cleaning, "PROCESSED_FOLDER", processed_root),
            patch.object(anomaly_detection, "PROCESSED_FOLDER", processed_root),
            patch.object(visualization, "REPORTS_FOLDER", reports_root),
            patch.object(ai_summary, "REPORTS_FOLDER", reports_root),
        ]
        for active_patch in self.patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)

        web_app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = web_app.app.test_client()
        self.client.get("/")
        with self.client.session_transaction() as browser_session:
            self.csrf_token = browser_session["csrf_token"]

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _upload(self, filename="transactions.csv"):
        rows = [
            {
                "amount": index + (index % 7) * 0.4,
                "margin": index * 0.5 + (-1) ** index,
                "segment": "retail" if index % 2 else "business",
            }
            for index in range(80)
        ]
        rows[10]["amount"] = None
        rows.append(rows[4].copy())
        csv_content = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        response = self.client.post(
            "/upload",
            data={
                "csrf_token": self.csrf_token,
                "file": (io.BytesIO(csv_content), filename),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DATASET EXPLORER", response.data)
        return response.request.path.rsplit("/", 1)[-1]

    def test_upload_explorer_and_dataset_isolation(self):
        first_id = self._upload("first.csv")
        second_id = self._upload("second.csv")

        self.assertNotEqual(first_id, second_id)
        self.assertTrue((self.datasets_root / first_id / "source.csv").is_file())
        self.assertTrue((self.datasets_root / second_id / "source.csv").is_file())
        response = self.client.get(f"/datasets/{second_id}")
        self.assertIn(b"AWAITING ANALYSIS", response.data)
        self.assertIn(b"LOCKED", response.data)
        self.assertIn(b"analysisProgress", response.data)

        other_browser = web_app.app.test_client()
        response = other_browser.get(f"/datasets/{first_id}")
        self.assertEqual(response.status_code, 404)

    def test_full_analysis_creates_downloadable_real_outputs(self):
        dataset_id = self._upload()

        with redirect_stdout(io.StringIO()):
            response = self.client.post(
                f"/datasets/{dataset_id}/analyze",
                data={"csrf_token": self.csrf_token},
                headers={"X-Requested-With": "XMLHttpRequest"},
            )

        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "analyzed")
        self.assertIn("Reports and charts are ready", result["message"])
        response = self.client.get(result["redirect_url"])
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Flagged anomaly records", response.data)
        self.assertIn(b"Normal records", response.data)
        self.assertIn(b"Analysis report", response.data)
        manifest_path = self.datasets_root / dataset_id / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "analyzed")
        self.assertEqual(manifest["rows"], 80)

        anomaly_file = (
            self.generated_root
            / "data"
            / "processed"
            / dataset_id
            / "anomalies.csv"
        )
        anomaly_rows = len(pd.read_csv(anomaly_file))
        self.assertEqual(anomaly_rows, manifest["anomaly_count"])
        self.assertGreater(anomaly_rows, 0)
        self.assertEqual(
            manifest["normal_count"] + manifest["anomaly_count"],
            manifest["rows"],
        )
        self.assertTrue(manifest["graphs"])

        anomaly_download = self.client.get(
            f"/datasets/{dataset_id}/download/anomalies"
        )
        cleaned_download = self.client.get(
            f"/datasets/{dataset_id}/download/cleaned"
        )
        pdf_download = self.client.get(f"/datasets/{dataset_id}/download/pdf")
        summary_download = self.client.get(
            f"/datasets/{dataset_id}/download/summary"
        )
        self.assertEqual(anomaly_download.status_code, 200)
        self.assertEqual(cleaned_download.status_code, 200)
        self.assertEqual(pdf_download.status_code, 200)
        self.assertEqual(summary_download.status_code, 200)
        self.assertIn(b"Anomaly", anomaly_download.data)
        self.assertTrue(pdf_download.data.startswith(b"%PDF"))
        self.assertIn(b"DATASET OVERVIEW", summary_download.data)
        anomaly_download.close()
        cleaned_download.close()
        pdf_download.close()
        summary_download.close()

        with patch.object(web_app, "send_email", return_value=True) as email_sender:
            response = self.client.post(
                f"/datasets/{dataset_id}/email",
                data={
                    "csrf_token": self.csrf_token,
                    "recipient": "analyst@example.com",
                },
                follow_redirects=True,
            )
        self.assertEqual(response.status_code, 200)
        email_sender.assert_called_once()
        self.assertEqual(
            email_sender.call_args.kwargs["recipient_email"],
            "analyst@example.com",
        )

    def test_cleaned_data_is_downloadable_before_model_analysis(self):
        dataset_id = self._upload()
        response = self.client.post(
            f"/datasets/{dataset_id}/clean",
            data={"csrf_token": self.csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        cleaned_download = self.client.get(
            f"/datasets/{dataset_id}/download/cleaned"
        )
        anomalies_download = self.client.get(
            f"/datasets/{dataset_id}/download/anomalies"
        )
        self.assertEqual(cleaned_download.status_code, 200)
        self.assertEqual(anomalies_download.status_code, 404)
        cleaned_download.close()
        anomalies_download.close()

    def test_anomaly_detection_rejects_non_numeric_dataset(self):
        with self.assertRaisesRegex(ValueError, "No suitable numerical features"):
            anomaly_detection.detect_anomalies(
                pd.DataFrame({"region": ["north", "south"]}),
                "non_numeric_test",
            )

    def test_analysis_does_not_report_fake_results_without_features(self):
        response = self.client.post(
            "/upload",
            data={
                "csrf_token": self.csrf_token,
                "file": (
                    io.BytesIO(b"region\nnorth\nsouth\nwest\n"),
                    "regions.csv",
                ),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )
        dataset_id = response.request.path.rsplit("/", 1)[-1]

        with self.assertLogs("app", level="ERROR"):
            with redirect_stdout(io.StringIO()):
                response = self.client.post(
                    f"/datasets/{dataset_id}/analyze",
                    data={"csrf_token": self.csrf_token},
                    headers={"X-Requested-With": "XMLHttpRequest"},
                )

        self.assertEqual(response.status_code, 422)
        self.assertFalse(response.get_json()["ok"])
        manifest = json.loads(
            (self.datasets_root / dataset_id / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["status"], "cleaned")
        self.assertNotIn("anomaly_count", manifest)
        self.assertIn("No suitable numerical features", response.get_json()["message"])

    def test_gemini_strict_mode_reports_missing_configuration(self):
        with patch.object(gemini_summary, "API_KEY", None):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY"):
                gemini_summary.generate_ai_summary("report", strict=True)

    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post("/upload", data={})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
