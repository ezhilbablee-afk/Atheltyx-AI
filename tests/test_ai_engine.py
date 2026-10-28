"""Unit tests for AI Models and Biomechanical Algorithms."""

import unittest
import math
import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.biomechanics import BiomechanicsEngine, calculate_angle_2d
from app.ai.injury_predictor import InjuryPredictor
from app.ai.training_engine import TrainingEngine
from app.ai.game_strategy import GameStrategyEngine
from app.ai.coaching_bot import VirtualCoachEngine


class TestAIEngine(unittest.TestCase):
    """Test suite for sports coaching AI algorithms."""

    def test_calculate_angle_2d(self):
        # 90 degree right angle test
        p1 = {"x": 0.0, "y": 1.0}
        p2 = {"x": 0.0, "y": 0.0}
        p3 = {"x": 1.0, "y": 0.0}
        angle = calculate_angle_2d(p1, p2, p3)
        self.assertAlmostEqual(angle, 90.0, places=1)

        # 180 degree straight line
        p1 = {"x": -1.0, "y": 0.0}
        p2 = {"x": 0.0, "y": 0.0}
        p3 = {"x": 1.0, "y": 0.0}
        angle = calculate_angle_2d(p1, p2, p3)
        self.assertAlmostEqual(angle, 180.0, places=1)

    def test_biomechanics_analysis(self):
        sample_keypoints = {
            "right_shoulder": {"x": 0.5, "y": 0.2},
            "right_elbow": {"x": 0.5, "y": 0.4},
            "right_wrist": {"x": 0.7, "y": 0.4},
            "right_hip": {"x": 0.5, "y": 0.5},
            "right_knee": {"x": 0.5, "y": 0.7},
            "right_ankle": {"x": 0.5, "y": 0.9},
            "left_hip": {"x": 0.55, "y": 0.5},
            "left_knee": {"x": 0.55, "y": 0.7},
            "left_ankle": {"x": 0.55, "y": 0.9}
        }
        res = BiomechanicsEngine.analyze_pose("Soccer Strike", sample_keypoints)
        self.assertIn("form_score", res)
        self.assertIn("joint_angles", res)
        self.assertIn("cues", res)
        self.assertTrue(0 <= res["form_score"] <= 100)

    def test_acwr_sweet_spot(self):
        # 2200 / 2000 = 1.10 (Sweet spot: 0.8 - 1.3)
        acwr = InjuryPredictor.calculate_acwr(2200, 2000)
        self.assertEqual(acwr, 1.1)

        eval_res = InjuryPredictor.evaluate_injury_risk(
            acute_load=2200,
            chronic_load=2000,
            resting_hr=50,
            baseline_resting_hr=48,
            hrv_current=65.0,
            hrv_baseline=68.0,
            recent_muscle_load=60.0,
            biomechanical_asymmetry_pct=4.0
        )
        self.assertEqual(eval_res["risk_level"], "Low")
        self.assertTrue(eval_res["risk_score"] < 35.0)

    def test_acwr_danger_zone(self):
        # 3600 / 2000 = 1.80 (> 1.5 is Danger Zone)
        eval_res = InjuryPredictor.evaluate_injury_risk(
            acute_load=3600,
            chronic_load=2000,
            resting_hr=62,
            baseline_resting_hr=50,
            hrv_current=42.0,
            hrv_baseline=68.0,
            recent_muscle_load=88.0,
            biomechanical_asymmetry_pct=18.0
        )
        self.assertIn(eval_res["risk_level"], ["High", "Critical"])
        self.assertTrue(eval_res["risk_score"] >= 50.0)
        self.assertGreater(len(eval_res["flagged_factors"]), 0)

    def test_adaptive_training_generator(self):
        program = TrainingEngine.generate_program(
            sport="Soccer",
            athlete_data={"user_id": 2},
            goal="Acceleration Dynamics",
            fatigue_level=75.0,
            acwr=1.45
        )
        self.assertEqual(len(program["schedule"]), 7)
        self.assertGreater(len(program["adaptation_notes"]), 0)
        # Verify adaptation trimmed intensity due to high fatigue
        mon_intensity = program["schedule"][0]["intensity"]
        self.assertIn(mon_intensity, ["Medium", "High"])

    def test_tactical_strategy_simulation(self):
        res = GameStrategyEngine.analyze_and_simulate("Soccer", "Test Opponent FC", "4-3-3 High Press", num_simulations=500)
        self.assertIn("simulation", res)
        self.assertIn("win_probability_pct", res["simulation"])
        self.assertGreater(res["simulation"]["win_probability_pct"], 0.0)
        self.assertIn("counter_tactics", res)

    def test_virtual_coach_engine(self):
        res = VirtualCoachEngine.respond_to_query("My hamstring feels very tight after sprinting", {"name": "Leo", "sport": "Soccer"})
        self.assertIn("Leo", res["reply"])
        self.assertIn("Injury", res["intent"])
        self.assertIsNotNone(res["actionable_tip"])


if __name__ == "__main__":
    unittest.main()
