# Athelytix AI — REST API Documentation

Base URL: `http://localhost:8080`

All request and response bodies use standard `application/json` with CORS enabled.

---

## 1. Health & System
### `GET /api/health`
Returns the operational health and version status.

**Sample Response:**
```json
{
  "status": "healthy",
  "service": "AI Sports Coaching Platform",
  "version": "1.0.0",
  "timestamp": "2026-10-28T22:30:00.000000"
}
```

---

## 2. User & Athlete Management
### `GET /api/users`
Lists all registered users and their RBAC roles (`admin`, `coach`, `analyst`, `athlete`).

### `GET /api/athletes`
Lists all active athlete profiles including age, VO2 max, primary position, resting/max HR.

### `GET /api/athlete/{id}/overview`
Returns the 360-degree athletic profile for athlete with user id `{id}`:
- User metadata
- Recent 15 telemetry data points
- Active periodized training program
- Injury assessment and ACWR ratio
- 5-axis skill breakdown
- Gamification status (XP, level, streak, badges)

---

## 3. Wearable IoT Telemetry Stream
### `POST /api/athlete/{id}/telemetry`
Ingests a live telemetry sensor packet.

**Request Body:**
```json
{
  "heart_rate": 158,
  "hrv_ms": 61.2,
  "speed_kmh": 26.4,
  "cadence_spm": 174,
  "muscle_load_pct": 74.5,
  "fatigue_index": 29.0,
  "power_watts": 275.0
}
```

---

## 4. Computer Vision Biomechanics
### `GET /api/biomechanics/simulation?movement=Soccer+Strike`
Returns animated 12-keyframe skeletal coordinates for the visualizer.

### `POST /api/biomechanics/analyze`
Submits 2D/3D skeleton keypoints for kinematic angle and form evaluation.

**Request Body:**
```json
{
  "movement_type": "Soccer Strike",
  "user_id": 2,
  "sport": "Soccer",
  "keypoints": {
    "right_hip": {"x": 0.5, "y": 0.5},
    "right_knee": {"x": 0.5, "y": 0.7},
    "right_ankle": {"x": 0.5, "y": 0.9}
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "movement_type": "Soccer Strike",
    "joint_angles": {"right_knee_flexion": 44.2},
    "metrics": {"kinetic_chain_efficiency": "89.4%"},
    "cues": ["Optimal strike knee alignment within optimal 42-52° corridor."],
    "form_score": 89.4,
    "status": "Optimal"
  }
}
```

---

## 5. Adaptive Training Generator
### `POST /api/training/generate`
Generates an AI-calibrated weekly microcycle adapting to recent athlete fatigue and ACWR.

**Request Body:**
```json
{
  "sport": "Soccer",
  "goal": "Speed & Kinetic Chain Optimization",
  "fatigue_level": 68.0,
  "acwr": 1.38,
  "user_id": 2
}
```

---

## 6. Injury Risk & ACWR Assessment
### `POST /api/injury/assess`
Calculates injury risk index and Acute:Chronic Workload Ratio.

**Request Body:**
```json
{
  "acute_load": 2500,
  "chronic_load": 2100,
  "resting_hr": 52,
  "baseline_resting_hr": 48,
  "hrv_current": 60.0,
  "hrv_baseline": 68.0,
  "muscle_load_pct": 65.0,
  "asymmetry_pct": 8.5,
  "user_id": 2
}
```

---

## 7. Tactical Game Strategy & Simulation
### `POST /api/strategy/simulate`
Executes Monte Carlo simulation of match scenarios against specific opponent tactics.

**Request Body:**
```json
{
  "sport": "Soccer",
  "opponent_name": "Red Stars FC",
  "opponent_style": "4-3-3 High Press"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "simulation": {
      "simulations_run": 2000,
      "win_probability_pct": 68.4,
      "expected_score_team": 2.15,
      "expected_score_opponent": 0.88
    },
    "counter_tactics": [
      "Direct vertical balls into the channels over the pressing fullback."
    ],
    "recommended_formation": "4-2-3-1 Asymmetric Counter"
  }
}
```

---

## 8. Virtual AI Coach & Voice Assistant
### `POST /api/coach/chat`
Interacts with the domain-specific sports science coach.

**Request Body:**
```json
{
  "message": "My right hamstring feels stiff after sprint intervals, what should I do?",
  "user_id": 2
}
```

**Response:**
```json
{
  "success": true,
  "reply": "Hey Leo Silva, regarding your Soccer development: Hamstring stiffness often stems from high deceleration eccentric stress...",
  "intent": "Injury Assessment / Muscle Strain",
  "actionable_tip": "Avoid sprint spikes >85%; do 3x6 slow eccentric hamstring sliders."
}
```
