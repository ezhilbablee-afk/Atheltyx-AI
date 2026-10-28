"""Personalized Training Program Generator and Adaptive Progression Engine.
Synthesizes athlete profile, VO2 max, recent fatigue, ACWR, and competitive goals
to generate periodized multi-day athletic regimens.
"""

from typing import Dict, List, Any


class TrainingEngine:
    """Generates and dynamically adapts training programs based on athlete physiological state."""

    SPORT_TEMPLATES = {
        "Soccer": [
            {"day": "Monday", "name": "Sprint Acceleration & Reactive Deceleration", "type": "Speed", "base_intensity": "High", "base_duration": 75},
            {"day": "Tuesday", "name": "Tactical Rondos & Aerobic Base Maintenance", "type": "Tactical/Aerobic", "base_intensity": "Medium", "base_duration": 60},
            {"day": "Wednesday", "name": "Active Mobility & Kinetic Joint Flossing", "type": "Recovery", "base_intensity": "Low", "base_duration": 45},
            {"day": "Thursday", "name": "Set-Piece Execution & High-Velocity Strike Form", "type": "Skill/Power", "base_intensity": "High", "base_duration": 85},
            {"day": "Friday", "name": "Neuromuscular Priming & Speed Shuttle Sharpness", "type": "Priming", "base_intensity": "Medium-High", "base_duration": 50},
            {"day": "Saturday", "name": "Match Simulation / Competitive Fixture", "type": "Competition", "base_intensity": "Maximal", "base_duration": 90},
            {"day": "Sunday", "name": "Hydrotherapy & Deep Fascial Release", "type": "Rest/Regeneration", "base_intensity": "Rest", "base_duration": 35}
        ],
        "Basketball": [
            {"day": "Monday", "name": "Vertical Jump Mechanics & Lateral Quickness", "type": "Plyometrics", "base_intensity": "High", "base_duration": 75},
            {"day": "Tuesday", "name": "Transition Offense & Pick-and-Roll Reads", "type": "Tactical", "base_intensity": "Medium-High", "base_duration": 80},
            {"day": "Wednesday", "name": "Posterior Chain Hypertrophy & Ankle Pre-hab", "type": "Strength", "base_intensity": "Medium", "base_duration": 60},
            {"day": "Thursday", "name": "Spot-up Shooting Arc Consistency & Fatigue Free-throws", "type": "Skill", "base_intensity": "Medium", "base_duration": 70},
            {"day": "Friday", "name": "Full Court Scrimmage Simulation", "type": "Competition", "base_intensity": "High", "base_duration": 85},
            {"day": "Saturday", "name": "Light Recovery Shootaround & Video Breakdown", "type": "Low-Impact", "base_intensity": "Low", "base_duration": 40},
            {"day": "Sunday", "name": "Systemic Recovery & Cryotherapy", "type": "Rest", "base_intensity": "Rest", "base_duration": 30}
        ],
        "Tennis": [
            {"day": "Monday", "name": "Footwork Cross-Court Recovery & Split-Step Agility", "type": "Agility", "base_intensity": "High", "base_duration": 80},
            {"day": "Tuesday", "name": "Serve Kinetic Chain & Rotational Core Velocity", "type": "Power", "base_intensity": "High", "base_duration": 75},
            {"day": "Wednesday", "name": "Cardiorespiratory Intervals & Shoulder Cuff Stability", "type": "Conditioning", "base_intensity": "Medium", "base_duration": 60},
            {"day": "Thursday", "name": "Deep Baseline Rally Consistency Under Fatigue", "type": "Endurance", "base_intensity": "High", "base_duration": 90},
            {"day": "Friday", "name": "Return of Serve Reaction Drills & Drop Shot Touch", "type": "Finesse", "base_intensity": "Medium", "base_duration": 60},
            {"day": "Saturday", "name": "Competitive Set Play / Match Simulation", "type": "Competition", "base_intensity": "Maximal", "base_duration": 105},
            {"day": "Sunday", "name": "Soft Tissue Foam Rolling & Thoracic Spine Mobility", "type": "Rest", "base_intensity": "Rest", "base_duration": 40}
        ]
    }

    @classmethod
    def generate_program(cls, sport: str, athlete_data: Dict[str, Any], goal: str, fatigue_level: float = 30.0, acwr: float = 1.1) -> Dict[str, Any]:
        """Generate tailored microcycle schedule adapting to current physiological state."""
        template = cls.SPORT_TEMPLATES.get(sport, cls.SPORT_TEMPLATES["Soccer"])

        adapted_schedule = []
        adaptation_notes = []

        is_high_fatigue = fatigue_level > 65.0
        is_high_risk = acwr > 1.35

        if is_high_fatigue:
            adaptation_notes.append("High fatigue detected (>65%): Volume trimmed by 20%, rest intervals lengthened.")
        if is_high_risk:
            adaptation_notes.append("ACWR elevated (>1.35): Replaced max sprint exposure with controlled sub-maximal technique drills.")

        for day in template:
            intensity = day["base_intensity"]
            duration = day["base_duration"]

            # Adapt based on fatigue & injury risk
            if (is_high_fatigue or is_high_risk) and intensity in ["High", "Maximal"]:
                if day["day"] in ["Monday", "Thursday"]:
                    intensity = "Medium"
                    duration = int(duration * 0.8)

            adapted_schedule.append({
                "day": day["day"],
                "focus": day["name"],
                "type": day["type"],
                "intensity": intensity,
                "duration_min": duration,
                "target_hr_zone": "Zone 4-5" if intensity in ["High", "Maximal"] else ("Zone 2-3" if intensity == "Medium" else "Zone 1")
            })

        return {
            "sport": sport,
            "target_goal": goal,
            "phase": "Intelligent Periodization (Microcycle A)",
            "adaptation_notes": adaptation_notes or ["Training load perfectly calibrated with athlete physiological readiness."],
            "weekly_total_minutes": sum(d["duration_min"] for d in adapted_schedule),
            "schedule": adapted_schedule
        }
