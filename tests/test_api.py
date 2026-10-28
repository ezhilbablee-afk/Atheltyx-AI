"""Integration tests for REST API endpoints using in-memory request simulation."""

import unittest
import io
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.server import SportsAIRequestHandler
from app.db import init_db


class MockHTTPClient:
    """Simulates HTTP requests into SportsAIRequestHandler without opening network sockets."""

    @classmethod
    def invoke(cls, method: str, path: str, payload: dict = None):
        body_bytes = json.dumps(payload).encode("utf-8") if payload else b""
        req_stream = io.BytesIO(body_bytes)
        resp_stream = io.BytesIO()

        class SimulatedHandler(SportsAIRequestHandler):
            def __init__(self):
                self.rfile = req_stream
                self.wfile = resp_stream
                self.path = path
                self.command = method
                self.headers = {}
                if body_bytes:
                    self.headers["Content-Length"] = str(len(body_bytes))
                    self.headers["Content-Type"] = "application/json"

            def send_response(self, code, message=None):
                self.status_code = code

            def send_header(self, keyword, value):
                pass

            def end_headers(self):
                pass

        handler = SimulatedHandler()
        if method == "GET":
            handler.do_GET()
        elif method == "POST":
            handler.do_POST()
        
        resp_stream.seek(0)
        resp_body = resp_stream.read().decode("utf-8")
        parsed_body = json.loads(resp_body) if resp_body else {}
        return getattr(handler, "status_code", 200), parsed_body


class TestAPIEndpoints(unittest.TestCase):
    """In-memory integration test suite for REST API."""

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_health_check(self):
        status, data = MockHTTPClient.invoke("GET", "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "AI Sports Coaching Platform")

    def test_get_users(self):
        status, data = MockHTTPClient.invoke("GET", "/api/users")
        self.assertEqual(status, 200)
        self.assertIn("users", data)
        self.assertGreater(len(data["users"]), 0)
        roles = [u["role"] for u in data["users"]]
        self.assertIn("athlete", roles)
        self.assertIn("coach", roles)

    def test_get_athletes(self):
        status, data = MockHTTPClient.invoke("GET", "/api/athletes")
        self.assertEqual(status, 200)
        self.assertIn("athletes", data)
        self.assertGreater(len(data["athletes"]), 0)

    def test_get_athlete_overview(self):
        status, data = MockHTTPClient.invoke("GET", "/api/athlete/2/overview")
        self.assertEqual(status, 200)
        self.assertEqual(data["user"]["full_name"], "Leo Silva")
        self.assertIsNotNone(data["training_program"])
        self.assertIsNotNone(data["injury_assessment"])
        self.assertIsNotNone(data["skills"])
        self.assertIsNotNone(data["gamification"])

    def test_post_telemetry(self):
        payload = {
            "heart_rate": 156,
            "hrv_ms": 64.2,
            "speed_kmh": 22.4,
            "cadence_spm": 172,
            "muscle_load_pct": 68.0,
            "fatigue_index": 27.0,
            "power_watts": 280.0
        }
        status, data = MockHTTPClient.invoke("POST", "/api/athlete/2/telemetry", payload)
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "recorded")

    def test_post_biomechanics_analyze(self):
        payload = {
            "movement_type": "Soccer Strike",
            "user_id": 2,
            "sport": "Soccer",
            "keypoints": {
                "right_shoulder": {"x": 0.5, "y": 0.2},
                "right_elbow": {"x": 0.5, "y": 0.4},
                "right_wrist": {"x": 0.7, "y": 0.4},
                "right_hip": {"x": 0.5, "y": 0.5},
                "right_knee": {"x": 0.5, "y": 0.7},
                "right_ankle": {"x": 0.5, "y": 0.9}
            }
        }
        status, data = MockHTTPClient.invoke("POST", "/api/biomechanics/analyze", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("form_score", data["analysis"])

    def test_post_training_generate(self):
        payload = {
            "sport": "Soccer",
            "goal": "Match Fitness",
            "fatigue_level": 40.0,
            "acwr": 1.15,
            "user_id": 2
        }
        status, data = MockHTTPClient.invoke("POST", "/api/training/generate", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("schedule", data["program"])

    def test_post_injury_assess(self):
        payload = {
            "acute_load": 2500,
            "chronic_load": 2100,
            "user_id": 2
        }
        status, data = MockHTTPClient.invoke("POST", "/api/injury/assess", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("risk_score", data["injury_assessment"])

    def test_post_strategy_simulate(self):
        payload = {
            "sport": "Soccer",
            "opponent_name": "Red Stars FC",
            "opponent_style": "4-3-3 High Press"
        }
        status, data = MockHTTPClient.invoke("POST", "/api/strategy/simulate", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("win_probability_pct", data["result"]["simulation"])

    def test_post_coach_chat(self):
        payload = {
            "message": "What should I eat after my intense match?",
            "user_id": 2
        }
        status, data = MockHTTPClient.invoke("POST", "/api/coach/chat", payload)
        self.assertEqual(status, 200)
        self.assertTrue(data["success"])
        self.assertIn("reply", data)
        self.assertIn("actionable_tip", data)


if __name__ == "__main__":
    unittest.main()
