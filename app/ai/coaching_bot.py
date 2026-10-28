"""AI Virtual Coaching Assistant Engine.
Provides contextual sports science insights, real-time motivational prompts,
injury recovery advisories, and biomechanical feedback.
"""

from typing import Dict, Any


class VirtualCoachEngine:
    """Intelligent coaching assistant tailored for athletes and coaches."""

    INTENT_RESPONSES = {
        "fatigue": {
            "intent": "Fatigue & Workload Management",
            "reply": "Your physiological telemetry indicates elevated central nervous system fatigue. With an elevated heart rate recovery slope, I recommend shifting today's session to low-impact Zone 2 aerobic cycling, followed by 15 minutes of diaphragmatic breathing and 500ml electrolyte replenishment.",
            "actionable_tip": "Reduce intensity to Zone 2; complete 15 min mobility flossing."
        },
        "hamstring": {
            "intent": "Injury Assessment / Muscle Strain",
            "reply": "Hamstring stiffness often stems from high deceleration eccentric stress or hip flexor over-tightness pulling the pelvis into anterior tilt. Immediately refrain from maximum sprint efforts today. Perform 3 sets of slow eccentric slider curls, gentle pigeon pose stretches, and apply cold therapy for 15 minutes.",
            "actionable_tip": "Avoid sprint spikes >85%; do 3x6 slow eccentric hamstring sliders."
        },
        "sprint": {
            "intent": "Speed & Acceleration Mechanics",
            "reply": "To optimize your initial 10-meter acceleration, focus on a positive forward shin angle (42-45 degrees) and violent backward ground drive through the balls of your feet. Ensure your torso projects out at 45 degrees rather than popping upright prematurely.",
            "actionable_tip": "Maintain forward shin angle on first 3 drive steps."
        },
        "shot": {
            "intent": "Technique / Strike Optimization",
            "reply": "When executing your strike, keep your non-kicking plant foot approximately 15cm lateral to the ball, point your knee directly toward the target, and lock your ankle downwards with rigid plantar flexion. The torso must lean slightly forward to keep ball trajectory controlled.",
            "actionable_tip": "Lock ankle firm and ensure plant foot points straight at target."
        },
        "nutrition": {
            "intent": "Sports Nutrition & Hydration",
            "reply": "For high-output match readiness: Consume 1.2g of carbohydrates per kg of body weight within 45 minutes post-workout, paired with 25-30g of fast-absorbing leucine-rich protein to stimulate muscle protein synthesis (MPS). Hydrate with 150% of fluid lost through sweat.",
            "actionable_tip": "3:1 Carb-to-Protein intake within 45 min post-session."
        },
        "strategy": {
            "intent": "Tactical Counter-play",
            "reply": "Against a compact mid-block press, our data suggests overloading the wide corridors. By drawing their double pivot to one flank, we open direct diagonal passing lanes for our inside forward to attack the blind spot of the center-backs.",
            "actionable_tip": "Exploit half-spaces via diagonal switch of play."
        }
    }

    DEFAULT_RESPONSE = {
        "intent": "General Athletic Guidance",
        "reply": "I'm tracking your real-time performance markers and biomechanical profiles. Stay consistent with your kinetic chain drills and ensure you log your post-session perceived exertion (RPE). What specific facet of your training would you like to refine today?",
        "actionable_tip": "Record RPE score post-session and check your ACWR."
    }

    @classmethod
    def respond_to_query(cls, user_message: str, athlete_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate tailored conversational coaching advice."""
        msg_lower = user_message.lower()

        matched = None
        for keyword, data in cls.INTENT_RESPONSES.items():
            if keyword in msg_lower:
                matched = data
                break

        if not matched:
            matched = cls.DEFAULT_RESPONSE

        # Tailor with athlete context if available
        athlete_name = athlete_context.get("name", "Athlete") if athlete_context else "Athlete"
        sport = athlete_context.get("sport", "Athletics") if athlete_context else "Athletics"

        personalized_reply = f"Hey {athlete_name}, regarding your {sport} development: {matched['reply']}"

        return {
            "intent": matched["intent"],
            "reply": personalized_reply,
            "actionable_tip": matched["actionable_tip"],
            "athlete_name": athlete_name,
            "sport": sport
        }
