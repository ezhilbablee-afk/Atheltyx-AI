"""Injury Prediction and Workload Analytics Engine.
Calculates Acute:Chronic Workload Ratio (ACWR), fatigue index,
asymmetry-based biomechanical strain, and injury risk mitigation protocols.
"""

from typing import Dict, List, Any


class InjuryPredictor:
    """Predictive model for athletic injury risk based on workload modeling (Tim Gabbett model)."""

    @staticmethod
    def calculate_acwr(acute_load: float, chronic_load: float) -> float:
        """Calculate Acute:Chronic Workload Ratio (ACWR).
        acute_load: Workload of current week (7 days)
        chronic_load: 4-week average weekly workload (28 days)
        """
        if chronic_load <= 0:
            return 1.0
        return round(acute_load / chronic_load, 2)

    @classmethod
    def evaluate_injury_risk(cls,
                             acute_load: float,
                             chronic_load: float,
                             resting_hr: int,
                             baseline_resting_hr: int,
                             hrv_current: float,
                             hrv_baseline: float,
                             recent_muscle_load: float,
                             biomechanical_asymmetry_pct: float) -> Dict[str, Any]:
        """Comprehensive risk evaluation incorporating Gabbett ACWR, autonomic markers, and kinematics."""
        acwr = cls.calculate_acwr(acute_load, chronic_load)

        # Baseline score: 0 (No risk) to 100 (Extremely high injury risk)
        risk_score = 15.0
        flagged_factors = []
        actionable_recommendations = []

        # 1. ACWR Analysis (Gabbett's Sweet Spot: 0.8 - 1.3)
        if acwr > 1.5:
            risk_score += 45.0
            risk_category = "Danger Zone (> 1.5)"
            flagged_factors.append(f"ACWR ({acwr}) is in the high danger zone. 2-4x higher soft tissue injury probability.")
            actionable_recommendations.append("Reduce high-speed running volume by 35% for the next 72 hours.")
        elif acwr > 1.3:
            risk_score += 25.0
            risk_category = "Elevated Risk (1.3 - 1.5)"
            flagged_factors.append(f"ACWR ({acwr}) is creeping above optimal sweet spot.")
            actionable_recommendations.append("Cap max-intensity sprint repetitions to 3 reps per session.")
        elif acwr < 0.8:
            risk_score += 15.0
            risk_category = "Under-prepared (< 0.8)"
            flagged_factors.append("Chronic load is low relative to sudden match exposure.")
            actionable_recommendations.append("Gradually ramp up progressive loading to build chronic resilience.")
        else:
            risk_category = "Optimal Sweet Spot (0.8 - 1.3)"
            actionable_recommendations.append("Current loading stimulates fitness adaptation with minimal fatigue spike.")

        # 2. Autonomic Nervous System / HRV Suppression
        hrv_suppression_pct = ((hrv_baseline - hrv_current) / max(hrv_baseline, 1.0)) * 100.0
        if hrv_suppression_pct > 18.0:
            risk_score += 20.0
            flagged_factors.append(f"HRV suppressed by {hrv_suppression_pct:.1f}% vs baseline (parasympathetic fatigue).")
            actionable_recommendations.append("Prioritize sleep hygiene, 20-min contrast hydrotherapy, and reduce neural CNS load.")
        elif hrv_suppression_pct > 10.0:
            risk_score += 10.0
            flagged_factors.append("Mild autonomic fatigue detected.")

        # 3. Resting HR Elevation
        hr_delta = resting_hr - baseline_resting_hr
        if hr_delta >= 6:
            risk_score += 12.0
            flagged_factors.append(f"Elevated resting heart rate (+{hr_delta} bpm). Potential systemic inflammation.")

        # 4. Biomechanical Asymmetry (from pose analysis)
        if biomechanical_asymmetry_pct > 15.0:
            risk_score += 15.0
            flagged_factors.append(f"Bilateral mechanical asymmetry of {biomechanical_asymmetry_pct:.1f}%. Compensatory movement pattern.")
            actionable_recommendations.append("Perform unilateral eccentric calf/hamstring isolation before full squad drills.")

        # Final Risk Level determination
        risk_score = round(max(5.0, min(98.0, risk_score)), 1)
        if risk_score >= 70.0:
            level = "Critical"
        elif risk_score >= 45.0:
            level = "High"
        elif risk_score >= 25.0:
            level = "Moderate"
        else:
            level = "Low"

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "acwr_ratio": acwr,
            "acwr_category": risk_category,
            "flagged_factors": flagged_factors,
            "recommendations": actionable_recommendations,
            "vulnerable_tissues": ["Hamstring (biceps femoris)", "Patellar tendon", "Adductor longus"] if acwr > 1.3 else ["General lower limb"]
        }
