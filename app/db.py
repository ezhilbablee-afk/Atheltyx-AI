"""Database management module for AI-Powered Sports Coaching Platform.
Handles SQLite schema creation, migrations, connection management, and default seed data.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sports_coaching.db")


def get_db_connection():
    """Establish and return a connection with row dict factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables with complete constraints and indices."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'coach', 'analyst', 'athlete')),
        sport TEXT NOT NULL,
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS athlete_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        age INTEGER NOT NULL,
        height_cm REAL NOT NULL,
        weight_kg REAL NOT NULL,
        dominant_hand TEXT DEFAULT 'Right',
        primary_position TEXT NOT NULL,
        vo2_max REAL DEFAULT 54.0,
        resting_hr INTEGER DEFAULT 52,
        max_hr INTEGER DEFAULT 198
    );

    CREATE TABLE IF NOT EXISTS biometric_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        heart_rate INTEGER NOT NULL,
        hrv_ms REAL NOT NULL,
        speed_kmh REAL NOT NULL,
        cadence_spm INTEGER NOT NULL,
        muscle_load_pct REAL NOT NULL,
        fatigue_index REAL NOT NULL,
        power_watts REAL DEFAULT 240.0
    );

    CREATE TABLE IF NOT EXISTS training_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        coach_id INTEGER REFERENCES users(id),
        title TEXT NOT NULL,
        sport TEXT NOT NULL,
        phase TEXT NOT NULL,
        target_goal TEXT NOT NULL,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused')),
        schedule_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS injury_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        risk_score REAL NOT NULL,
        risk_level TEXT NOT NULL CHECK(risk_level IN ('Low', 'Moderate', 'High', 'Critical')),
        acwr_ratio REAL NOT NULL,
        acute_load REAL NOT NULL,
        chronic_load REAL NOT NULL,
        flagged_body_parts TEXT NOT NULL,
        recommendations_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS video_analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        video_title TEXT NOT NULL,
        sport TEXT NOT NULL,
        movement_type TEXT NOT NULL,
        form_score REAL NOT NULL,
        biomechanics_summary_json TEXT NOT NULL,
        key_moments_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS game_strategies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sport TEXT NOT NULL,
        match_title TEXT NOT NULL,
        opponent_name TEXT NOT NULL,
        formation_setup TEXT NOT NULL,
        tactical_analysis_json TEXT NOT NULL,
        counter_tactics_json TEXT NOT NULL,
        simulation_result_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS skill_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        sport TEXT NOT NULL,
        overall_score REAL NOT NULL,
        speed_score REAL NOT NULL,
        agility_score REAL NOT NULL,
        endurance_score REAL NOT NULL,
        technique_score REAL NOT NULL,
        tactical_score REAL NOT NULL,
        benchmark_comparison_json TEXT NOT NULL,
        assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS gamification (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak_days INTEGER DEFAULT 0,
        badges_json TEXT NOT NULL,
        challenges_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS coaching_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
        message TEXT NOT NULL,
        intent TEXT,
        actionable_tip TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    seed_default_data(conn)
    conn.close()


def seed_default_data(conn):
    """Seed initial realistic test data if users table is empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return

    # Seed Users
    users_data = [
        (1, "coach_alex", "alex.miller@sportai.io", "Coach Alex Miller", "coach", "All Sports", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"),
        (2, "leo_silva", "leo.silva@sportai.io", "Leo Silva", "athlete", "Soccer", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"),
        (3, "elena_rostova", "elena.rostova@sportai.io", "Elena Rostova", "athlete", "Tennis", "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"),
        (4, "marcus_vance", "marcus.vance@sportai.io", "Marcus Vance", "athlete", "Basketball", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"),
        (5, "dr_jordan", "jordan.reyes@sportai.io", "Dr. Jordan Reyes", "analyst", "Biomechanics", "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150"),
        (6, "admin_coaching", "admin@sportai.io", "Admin Director", "admin", "System", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150")
    ]
    cursor.executemany("INSERT INTO users (id, username, email, full_name, role, sport, avatar_url) VALUES (?, ?, ?, ?, ?, ?, ?)", users_data)

    # Seed Athlete Profiles
    profiles = [
        (2, 22, 182.5, 76.0, "Right", "Attacking Midfielder", 61.5, 48, 196),
        (3, 24, 178.0, 68.5, "Right", "Singles Baselliner", 58.2, 50, 194),
        (4, 21, 198.0, 94.0, "Left", "Point Guard / Shooting Guard", 57.0, 52, 192)
    ]
    cursor.executemany("INSERT INTO athlete_profiles (user_id, age, height_cm, weight_kg, dominant_hand, primary_position, vo2_max, resting_hr, max_hr) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", profiles)

    # Seed Biometric Telemetry (Leo Silva - recent stream)
    now = datetime.now()
    telemetry_records = []
    for i in range(15):
        t = (now - timedelta(minutes=15 - i)).strftime("%Y-%m-%d %H:%M:%S")
        hr = 142 + (i % 5) * 6
        hrv = 68.0 - (i * 0.8)
        speed = 18.5 + (i % 4) * 2.2
        cadence = 168 + (i % 3) * 4
        mload = 65.0 + (i * 1.5)
        fatigue = 22.0 + (i * 2.1)
        telemetry_records.append((2, t, hr, round(hrv, 1), round(speed, 1), cadence, round(mload, 1), round(fatigue, 1), 260.0 + (i * 5)))

    cursor.executemany("""
    INSERT INTO biometric_telemetry (user_id, timestamp, heart_rate, hrv_ms, speed_kmh, cadence_spm, muscle_load_pct, fatigue_index, power_watts)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, telemetry_records)

    # Seed Training Program
    schedule_leo = {
        "microcycle": "Sprint Conditioning & Deceleration Mechanics",
        "duration_weeks": 4,
        "current_week": 2,
        "daily_schedule": [
            {"day": "Monday", "focus": "High Intensity Acceleration & Agility", "intensity": "High", "duration_min": 75, "exercises": ["10m Acceleration Drills (6 reps)", "Slalom Cone Cuts (8 reps)", "Weighted Sled Pushes 3x20m"]},
            {"day": "Tuesday", "focus": "Aerobic Capacity & Ball Mastery", "intensity": "Medium", "duration_min": 60, "exercises": ["Zone 3 Interval Runs 4x800m", "1v1 Dribble Escapes", "Core Anti-Rotation Holds"]},
            {"day": "Wednesday", "focus": "Active Recovery & Mobility", "intensity": "Low", "duration_min": 45, "exercises": ["Hip Flexor Mobility", "Nordic Hamstring Eccentrics", "Contrast Bath Protocol"]},
            {"day": "Thursday", "focus": "Kicking Biomechanics & Tactical Positioning", "intensity": "High", "duration_min": 90, "exercises": ["Striking Technique Analysis", "Half-Space Penetration Runs", "Plyometric Box Jumps 4x5"]},
            {"day": "Friday", "focus": "Match Prep & Speed Endurance", "intensity": "Medium-High", "duration_min": 60, "exercises": ["Short Sprint Sharpness", "Set Piece Rehearsal", "Reaction Shuttle Runs"]},
            {"day": "Saturday", "focus": "Match Day / Simulated Competitive Scrimmage", "intensity": "Maximal", "duration_min": 90, "exercises": ["Competitive 90-min Full Pitch Match"]},
            {"day": "Sunday", "focus": "Systemic Recovery & Wellness Scan", "intensity": "Rest", "duration_min": 30, "exercises": ["Cryotherapy", "Foam Roll Quadriceps & Calf", "Sleep Optimization Review"]}
        ]
    }
    cursor.execute("""
    INSERT INTO training_programs (user_id, coach_id, title, sport, phase, target_goal, status, schedule_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (2, 1, "Elite Match Speed & Kinetic Chain Optimization", "Soccer", "In-Season Competition", "Maximize top sprint speed to 33.5 km/h while reducing hamstring shear stress", "active", json.dumps(schedule_leo)))

    # Seed Injury Assessment
    injury_recs = [
        "Incorporate eccentric Nordic hamstring curls (3 sets x 6 reps) twice weekly.",
        "Cap sprint velocity exposures above 90% top speed to 4 repetitions per session.",
        "Right knee valgus angle during deceleration is slightly elevated (14 deg) - enforce glute medius activation.",
        "Increase post-training hydrations and magnesium recovery protocol."
    ]
    cursor.execute("""
    INSERT INTO injury_assessments (user_id, risk_score, risk_level, acwr_ratio, acute_load, chronic_load, flagged_body_parts, recommendations_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (2, 28.5, "Low", 1.12, 2450.0, 2180.0, "Right Biceps Femoris (Hamstring), Patellar Tendon", json.dumps(injury_recs)))

    # Seed Video Analysis
    key_moments = [
        {"timestamp_sec": 4.2, "label": "Plant Foot Placement", "status": "optimal", "note": "Plant foot aligned 15cm lateral to ball, allowing ideal hip torque."},
        {"timestamp_sec": 7.8, "label": "Knee Flexion on Impact", "status": "warning", "note": "Knee angle 38 deg (target: 45-50 deg), causing slight quadriceps overload."},
        {"timestamp_sec": 12.1, "label": "Follow-through Deceleration", "status": "optimal", "note": "Smooth rotational dissipation through thoracic spine and opposite arm balance."}
    ]
    bio_summary = {
        "hip_rotation_velocity_deg_s": 420.5,
        "knee_flexion_deg": 41.2,
        "trunk_lean_deg": 14.8,
        "kinetic_chain_efficiency_pct": 89.4,
        "ground_reaction_force_bw": 2.85
    }
    cursor.execute("""
    INSERT INTO video_analyses (user_id, video_title, sport, movement_type, form_score, biomechanics_summary_json, key_moments_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (2, "High-Velocity Instep Strike Kinematics", "Soccer", "Instep Drive Shot", 88.5, json.dumps(bio_summary), json.dumps(key_moments)))

    # Seed Game Strategy
    tactical_analysis = {
        "opponent_formation": "4-3-3 High Press",
        "weakness_identified": "Significant gap between fullbacks and center-backs during high defensive transitions",
        "possession_profile": "Prefers central buildup (64%), vulnerable to wide rapid counter-attacks",
        "key_threat_player": "#9 Striker (High aerial duel win rate 73%)"
    }
    counter_tactics = [
        "Deploy quick vertical diagonals into the right half-space behind their left-back.",
        "Double-team aerial duels on set pieces using zonal-man hybrid marker.",
        "Bypass central midfield block with swift 2-touch third-man runs.",
        "Trigger pressing traps when opponent #6 receives the ball facing his own goal."
    ]
    sim_result = {
        "win_probability_pct": 68.4,
        "expected_goals_for": 2.15,
        "expected_goals_against": 0.88,
        "simulated_scenarios_count": 5000,
        "recommended_pace": "High tempo vertical direct"
    }
    cursor.execute("""
    INSERT INTO game_strategies (sport, match_title, opponent_name, formation_setup, tactical_analysis_json, counter_tactics_json, simulation_result_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Soccer", "League Semifinal vs Red Stars FC", "Red Stars FC", "4-2-3-1 Asymmetric Dynamic", json.dumps(tactical_analysis), json.dumps(counter_tactics), json.dumps(sim_result)))

    # Seed Skill Assessment
    benchmarks = {
        "speed": {"player": 91.0, "peer_avg": 78.5, "pro_standard": 94.0, "unit": "Percentile"},
        "agility": {"player": 88.0, "peer_avg": 75.0, "pro_standard": 92.0, "unit": "Percentile"},
        "endurance": {"player": 86.5, "peer_avg": 80.0, "pro_standard": 95.0, "unit": "Percentile"},
        "technique": {"player": 93.0, "peer_avg": 72.0, "pro_standard": 96.0, "unit": "Percentile"},
        "tactical": {"player": 85.0, "peer_avg": 70.0, "pro_standard": 90.0, "unit": "Percentile"}
    }
    cursor.execute("""
    INSERT INTO skill_assessments (user_id, sport, overall_score, speed_score, agility_score, endurance_score, technique_score, tactical_score, benchmark_comparison_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (2, "Soccer", 88.7, 91.0, 88.0, 86.5, 93.0, 85.0, json.dumps(benchmarks)))

    # Seed Gamification
    badges = [
        {"id": "speed_demon", "name": "Speed Demon", "icon": "⚡", "description": "Exceeded 32 km/h top sprint in 3 consecutive matches", "unlocked": True, "date": "2026-10-15"},
        {"id": "iron_form", "name": "Biomechanic Perfectionist", "icon": "🎯", "description": "Achieved Form Score > 90% in 5 consecutive technique drills", "unlocked": True, "date": "2026-10-22"},
        {"id": "tactical_master", "name": "Field Commander", "icon": "🧠", "description": "Complete 10 interactive game strategy counter-simulations", "unlocked": True, "date": "2026-10-25"},
        {"id": "recovery_guru", "name": "Recovery Master", "icon": "🛡️", "description": "Maintained ACWR in optimal sweet spot (0.8 - 1.3) for 4 straight weeks", "unlocked": False, "progress": "75%"}
    ]
    challenges = [
        {"title": "Weekly Kinetic Sprint Challenge", "xp": 250, "progress": 85, "target": "Accumulate 1200m at > 28 km/h", "days_left": 3},
        {"title": "Knee Stability Form Drill", "xp": 180, "progress": 100, "target": "Complete 4 sets of single-leg drop landings", "status": "Claimable"}
    ]
    cursor.execute("""
    INSERT INTO gamification (user_id, points, level, streak_days, badges_json, challenges_json)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (2, 3450, 7, 14, json.dumps(badges), json.dumps(challenges)))

    # Seed Initial Chat Messages
    chat_logs = [
        (2, "user", "Coach, my right hamstring feels slightly tight after yesterday's high-speed transition runs. Should I alter today's drill?", "injury_query", None),
        (2, "assistant", "Good call flagging this early, Leo. Your ACWR is currently 1.12 (safe zone), but your muscle load spiked by 18% during the 85th minute. Let's modify today: replace 100% sprint intervals with high-tempo 70% aerobic striders, and complete 3 sets of eccentric Nordic curls plus 10 minutes of hip flexor release. How does your passive knee extension feel?", "injury_recommendation", "Switch sprints to 70% striders + eccentric hamstring protocol.")
    ]
    cursor.executemany("INSERT INTO coaching_messages (user_id, role, message, intent, actionable_tip) VALUES (?, ?, ?, ?, ?)", chat_logs)

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
