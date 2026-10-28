"""High-performance zero-dependency HTTP REST API and Static File Server
for the AI-Powered Sports Coaching Platform.
"""

import http.server
import json
import mimetypes
import os
import re
import urllib.parse
from datetime import datetime

from app.db import get_db_connection, init_db
from app.ai.biomechanics import BiomechanicsEngine
from app.ai.injury_predictor import InjuryPredictor
from app.ai.training_engine import TrainingEngine
from app.ai.game_strategy import GameStrategyEngine
from app.ai.coaching_bot import VirtualCoachEngine

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


class SportsAIRequestHandler(http.server.BaseHTTPRequestHandler):
    """Custom HTTP request handler serving REST APIs and single-page web UI."""

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        """Respond to CORS preflight requests."""
        self._set_headers(200)

    def _read_json_body(self):
        """Read and parse JSON from request payload."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body)
        return {}

    def _send_json(self, data, status=200):
        self._set_headers(status, "application/json")
        self.wfile.write(json.dumps(data, default=str).encode("utf-8"))

    def do_GET(self):
        """Route GET requests for both REST endpoints and static assets."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        try:
            # 1. API Routes
            if path == "/api/health":
                self._send_json({"status": "healthy", "service": "AI Sports Coaching Platform", "version": "1.0.0", "timestamp": datetime.now().isoformat()})
                return

            if path == "/api/users":
                conn = get_db_connection()
                users = conn.execute("SELECT id, username, email, full_name, role, sport, avatar_url FROM users").fetchall()
                conn.close()
                self._send_json({"users": [dict(u) for u in users]})
                return

            if path == "/api/athletes":
                conn = get_db_connection()
                athletes = conn.execute("""
                    SELECT u.id, u.username, u.full_name, u.sport, u.avatar_url,
                           p.age, p.height_cm, p.weight_kg, p.dominant_hand, p.primary_position, p.vo2_max, p.resting_hr, p.max_hr
                    FROM users u
                    JOIN athlete_profiles p ON u.id = p.user_id
                    WHERE u.role = 'athlete'
                """).fetchall()
                conn.close()
                self._send_json({"athletes": [dict(a) for a in athletes]})
                return

            # Match /api/athlete/{id}/overview
            athlete_match = re.match(r"^/api/athlete/(\d+)/overview$", path)
            if athlete_match:
                user_id = int(athlete_match.group(1))
                conn = get_db_connection()
                user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                if not user:
                    conn.close()
                    self._send_json({"error": "Athlete not found"}, status=404)
                    return

                profile = conn.execute("SELECT * FROM athlete_profiles WHERE user_id = ?", (user_id,)).fetchone()
                telemetry = conn.execute("SELECT * FROM biometric_telemetry WHERE user_id = ? ORDER BY id DESC LIMIT 15", (user_id,)).fetchall()
                training = conn.execute("SELECT * FROM training_programs WHERE user_id = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
                injury = conn.execute("SELECT * FROM injury_assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
                skills = conn.execute("SELECT * FROM skill_assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
                gamification = conn.execute("SELECT * FROM gamification WHERE user_id = ?", (user_id,)).fetchone()
                conn.close()

                resp = {
                    "user": dict(user),
                    "profile": dict(profile) if profile else None,
                    "recent_telemetry": [dict(t) for t in reversed(telemetry)],
                    "training_program": {
                        "id": training["id"],
                        "title": training["title"],
                        "sport": training["sport"],
                        "phase": training["phase"],
                        "target_goal": training["target_goal"],
                        "schedule": json.loads(training["schedule_json"])
                    } if training else None,
                    "injury_assessment": {
                        "risk_score": injury["risk_score"],
                        "risk_level": injury["risk_level"],
                        "acwr_ratio": injury["acwr_ratio"],
                        "acute_load": injury["acute_load"],
                        "chronic_load": injury["chronic_load"],
                        "flagged_body_parts": injury["flagged_body_parts"],
                        "recommendations": json.loads(injury["recommendations_json"])
                    } if injury else None,
                    "skills": {
                        "overall_score": skills["overall_score"],
                        "speed": skills["speed_score"],
                        "agility": skills["agility_score"],
                        "endurance": skills["endurance_score"],
                        "technique": skills["technique_score"],
                        "tactical": skills["tactical_score"],
                        "benchmarks": json.loads(skills["benchmark_comparison_json"])
                    } if skills else None,
                    "gamification": {
                        "points": gamification["points"],
                        "level": gamification["level"],
                        "streak_days": gamification["streak_days"],
                        "badges": json.loads(gamification["badges_json"]),
                        "challenges": json.loads(gamification["challenges_json"])
                    } if gamification else None
                }
                self._send_json(resp)
                return

            # Match /api/athlete/{id}/telemetry
            telemetry_match = re.match(r"^/api/athlete/(\d+)/telemetry$", path)
            if telemetry_match:
                user_id = int(telemetry_match.group(1))
                conn = get_db_connection()
                records = conn.execute("SELECT * FROM biometric_telemetry WHERE user_id = ? ORDER BY id DESC LIMIT 30", (user_id,)).fetchall()
                conn.close()
                self._send_json({"telemetry": [dict(r) for r in reversed(records)]})
                return

            if path == "/api/biomechanics/simulation":
                sport = query_params.get("movement", ["Soccer Strike"])[0]
                frames = BiomechanicsEngine.get_simulation_frames(sport)
                self._send_json({"movement": sport, "frames": frames})
                return

            if path == "/api/strategy":
                conn = get_db_connection()
                strategies = conn.execute("SELECT * FROM game_strategies ORDER BY id DESC").fetchall()
                conn.close()
                parsed_strategies = []
                for s in strategies:
                    item = dict(s)
                    item["tactical_analysis"] = json.loads(item["tactical_analysis_json"])
                    item["counter_tactics"] = json.loads(item["counter_tactics_json"])
                    item["simulation_result"] = json.loads(item["simulation_result_json"])
                    parsed_strategies.append(item)
                self._send_json({"strategies": parsed_strategies})
                return

            # Match /api/video-analysis/{user_id}
            video_match = re.match(r"^/api/video-analysis/(\d+)$", path)
            if video_match:
                user_id = int(video_match.group(1))
                conn = get_db_connection()
                analyses = conn.execute("SELECT * FROM video_analyses WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
                conn.close()
                results = []
                for a in analyses:
                    item = dict(a)
                    item["biomechanics_summary"] = json.loads(item["biomechanics_summary_json"])
                    item["key_moments"] = json.loads(item["key_moments_json"])
                    results.append(item)
                self._send_json({"video_analyses": results})
                return

            if path == "/api/leaderboard":
                conn = get_db_connection()
                leaders = conn.execute("""
                    SELECT u.id, u.full_name, u.sport, u.avatar_url, g.points, g.level, g.streak_days
                    FROM users u
                    JOIN gamification g ON u.id = g.user_id
                    ORDER BY g.points DESC
                """).fetchall()
                conn.close()
                self._send_json({"leaderboard": [dict(l) for l in leaders]})
                return

            # 2. Static File Serving
            if path in ["", "/"]:
                file_path = os.path.join(STATIC_DIR, "index.html")
            else:
                rel_path = path.lstrip("/")
                file_path = os.path.join(STATIC_DIR, rel_path)

            if os.path.exists(file_path) and os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
                content_type = content_type or "text/plain"
                with open(file_path, "rb") as f:
                    content = f.read()
                self._set_headers(200, content_type)
                self.wfile.write(content)
                return

            self._send_json({"error": "Resource not found"}, status=404)

        except Exception as e:
            self._send_json({"error": str(e)}, status=500)

    def do_POST(self):
        """Route POST actions: ingest telemetry, run biomechanics, predict injury, chat with coach."""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        try:
            body = self._read_json_body()

            # 1. Ingest Wearable Telemetry
            telemetry_post_match = re.match(r"^/api/athlete/(\d+)/telemetry$", path)
            if telemetry_post_match:
                user_id = int(telemetry_post_match.group(1))
                hr = int(body.get("heart_rate", 150))
                hrv = float(body.get("hrv_ms", 65.0))
                speed = float(body.get("speed_kmh", 18.0))
                cadence = int(body.get("cadence_spm", 170))
                muscle_load = float(body.get("muscle_load_pct", 70.0))
                fatigue = float(body.get("fatigue_index", 25.0))
                power = float(body.get("power_watts", 250.0))

                conn = get_db_connection()
                conn.execute("""
                    INSERT INTO biometric_telemetry (user_id, heart_rate, hrv_ms, speed_kmh, cadence_spm, muscle_load_pct, fatigue_index, power_watts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, hr, hrv, speed, cadence, muscle_load, fatigue, power))
                conn.commit()
                conn.close()

                self._send_json({"status": "recorded", "user_id": user_id, "data": body})
                return

            # 2. Analyze Biomechanical Movement (Computer Vision Keypoints)
            if path == "/api/biomechanics/analyze":
                movement = body.get("movement_type", "Soccer Strike")
                keypoints = body.get("keypoints", {})
                analysis = BiomechanicsEngine.analyze_pose(movement, keypoints)

                # Persist to video_analyses if user_id provided
                user_id = body.get("user_id")
                if user_id:
                    conn = get_db_connection()
                    conn.execute("""
                        INSERT INTO video_analyses (user_id, video_title, sport, movement_type, form_score, biomechanics_summary_json, key_moments_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        f"Live CV Kinematics Session - {movement}",
                        body.get("sport", "Athletics"),
                        movement,
                        analysis["form_score"],
                        json.dumps(analysis["metrics"]),
                        json.dumps([{"timestamp_sec": 1.0, "label": "Key Point Evaluation", "status": "analyzed", "note": "; ".join(analysis["cues"])}])
                    ))
                    conn.commit()
                    conn.close()

                self._send_json({"success": True, "analysis": analysis})
                return

            # 3. Dynamic Training Program Generation
            if path == "/api/training/generate":
                sport = body.get("sport", "Soccer")
                goal = body.get("goal", "Speed & Kinetic Chain Optimization")
                fatigue = float(body.get("fatigue_level", 35.0))
                acwr = float(body.get("acwr", 1.15))
                user_id = body.get("user_id", 2)

                program = TrainingEngine.generate_program(
                    sport=sport,
                    athlete_data={"user_id": user_id},
                    goal=goal,
                    fatigue_level=fatigue,
                    acwr=acwr
                )

                conn = get_db_connection()
                # Deactivate previous active programs
                conn.execute("UPDATE training_programs SET status = 'completed' WHERE user_id = ? AND status = 'active'", (user_id,))
                conn.execute("""
                    INSERT INTO training_programs (user_id, coach_id, title, sport, phase, target_goal, status, schedule_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, 1, f"AI-Adaptive {sport} Plan", sport, program["phase"], goal, "active", json.dumps(program["schedule"])))
                conn.commit()
                conn.close()

                self._send_json({"success": True, "program": program})
                return

            # 4. Assess Injury Risk & Workload
            if path == "/api/injury/assess":
                acute = float(body.get("acute_load", 2400.0))
                chronic = float(body.get("chronic_load", 2100.0))
                resting_hr = int(body.get("resting_hr", 52))
                base_resting_hr = int(body.get("baseline_resting_hr", 48))
                hrv = float(body.get("hrv_current", 60.0))
                hrv_base = float(body.get("hrv_baseline", 68.0))
                muscle_load = float(body.get("muscle_load_pct", 65.0))
                asymmetry = float(body.get("asymmetry_pct", 8.5))

                evaluation = InjuryPredictor.evaluate_injury_risk(
                    acute_load=acute,
                    chronic_load=chronic,
                    resting_hr=resting_hr,
                    baseline_resting_hr=base_resting_hr,
                    hrv_current=hrv,
                    hrv_baseline=hrv_base,
                    recent_muscle_load=muscle_load,
                    biomechanical_asymmetry_pct=asymmetry
                )

                user_id = body.get("user_id")
                if user_id:
                    conn = get_db_connection()
                    conn.execute("""
                        INSERT INTO injury_assessments (user_id, risk_score, risk_level, acwr_ratio, acute_load, chronic_load, flagged_body_parts, recommendations_json)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        evaluation["risk_score"],
                        evaluation["risk_level"],
                        evaluation["acwr_ratio"],
                        acute,
                        chronic,
                        ", ".join(evaluation["vulnerable_tissues"]),
                        json.dumps(evaluation["recommendations"])
                    ))
                    conn.commit()
                    conn.close()

                self._send_json({"success": True, "injury_assessment": evaluation})
                return

            # 5. Game Strategy Simulation
            if path == "/api/strategy/simulate":
                sport = body.get("sport", "Soccer")
                opponent = body.get("opponent_name", "Red Stars FC")
                style = body.get("opponent_style", "4-3-3 High Press")
                sim_result = GameStrategyEngine.analyze_and_simulate(sport, opponent, style)

                conn = get_db_connection()
                conn.execute("""
                    INSERT INTO game_strategies (sport, match_title, opponent_name, formation_setup, tactical_analysis_json, counter_tactics_json, simulation_result_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sport,
                    f"Match Simulation vs {opponent}",
                    opponent,
                    sim_result["recommended_formation"],
                    json.dumps({"vulnerabilities": sim_result["tactical_vulnerabilities"]}),
                    json.dumps(sim_result["counter_tactics"]),
                    json.dumps(sim_result["simulation"])
                ))
                conn.commit()
                conn.close()

                self._send_json({"success": True, "result": sim_result})
                return

            # 6. Virtual AI Coach Chat
            if path == "/api/coach/chat":
                message = body.get("message", "")
                user_id = body.get("user_id", 2)

                conn = get_db_connection()
                user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                user_context = {"name": user["full_name"], "sport": user["sport"]} if user else {}

                coach_response = VirtualCoachEngine.respond_to_query(message, user_context)

                conn.execute("""
                    INSERT INTO coaching_messages (user_id, role, message, intent, actionable_tip)
                    VALUES (?, 'user', ?, NULL, NULL)
                """, (user_id, message))

                conn.execute("""
                    INSERT INTO coaching_messages (user_id, role, message, intent, actionable_tip)
                    VALUES (?, 'assistant', ?, ?, ?)
                """, (user_id, coach_response["reply"], coach_response["intent"], coach_response["actionable_tip"]))
                conn.commit()
                conn.close()

                self._send_json({"success": True, "reply": coach_response["reply"], "intent": coach_response["intent"], "actionable_tip": coach_response["actionable_tip"]})
                return

            self._send_json({"error": "Endpoint not recognized"}, status=404)

        except Exception as e:
            self._send_json({"error": str(e)}, status=500)


def start_server(port=PORT):
    """Start HTTP server."""
    init_db()
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, SportsAIRequestHandler)
    print(f"🚀 AI Sports Coaching Server listening on port {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    start_server()
