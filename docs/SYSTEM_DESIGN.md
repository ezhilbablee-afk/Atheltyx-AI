# Athelytix AI — System Architecture & Design Specification

This document details the end-to-end system architecture, data flows, AI/ML pipelines, database schema, and deployment topology for the AI-Powered Sports Coaching Platform.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Data Sources & Edge Devices
        Wearables["Wearables & IoT Sensors\n(Polar H10, Catapult, WHOOP)\nHeart Rate, HRV, Speed, sEMG"]
        Cameras["Optical Cameras & Video\n(High-speed 120-240 FPS)\nBiomechanical footage"]
        TacticalData["Tactical Match Feeds\n(Event data, Tracking data)"]
    end

    subgraph Ingestion & Edge Gateway
        EdgeIngest["IoT Gateway & Video Ingestion\n(BLE 5.3, RTSP / WebRTC, REST API)"]
    end

    subgraph Core AI & Analytics Engine
        PoseEngine["Computer Vision / Pose Engine\n- BlazePose 33 Keypoints\n- Joint Angle Kinematics\n- Bilateral Symmetry"]
        WorkloadEngine["Injury Prediction & ACWR Engine\n- Tim Gabbett Acute:Chronic Ratio\n- Autonomic Fatigue (HRV)\n- Anomaly Detection"]
        TrainingEngine["Adaptive Training Engine\n- Dynamic Periodization\n- Workload Modulation\n- Recovery Feedback Loop"]
        TacticalEngine["Tactical Strategy Simulator\n- Opponent Vulnerability Matrix\n- Monte Carlo Match Simulation"]
        VirtualCoach["Virtual AI Coach\n- Natural Language Dialog\n- Speech Synthesis & Voice Cues\n- Domain Sports Science RAG"]
    end

    subgraph Data Storage
        RDBMS[("Relational Database (SQLite / PostgreSQL)\n- Users & RBAC\n- Biometrics & Telemetry\n- Periodized Regimens\n- Video Kinematics\n- Match Simulations")]
    end

    subgraph Application & User Presentation Layer
        REST["REST API Service / WebSockets"]
        WebUI["Modern Reactive Dashboard\n- Athlete Hub\n- Coach Training Center\n- Analyst Tactical Room\n- Admin Console"]
    end

    Wearables --> EdgeIngest
    Cameras --> EdgeIngest
    TacticalData --> EdgeIngest

    EdgeIngest --> REST
    REST --> PoseEngine
    REST --> WorkloadEngine
    REST --> TrainingEngine
    REST --> TacticalEngine
    REST --> VirtualCoach

    PoseEngine --> RDBMS
    WorkloadEngine --> RDBMS
    TrainingEngine --> RDBMS
    TacticalEngine --> RDBMS
    VirtualCoach --> RDBMS

    RDBMS --> REST
    REST --> WebUI
```

---

## 2. Data Flow Pipeline

### 2.1 Wearable IoT Telemetry Pipeline
1. **Sensor Ingestion**: Wearable sensors stream ECG/PPG, inertial measurement unit (IMU), and GPS data at 50 Hz.
2. **Filtering & Preprocessing**: Noise removal, Kalman filtering for GPS speed and acceleration peaks.
3. **Feature Extraction**: Computes rolling 7-day acute load and 28-day chronic load, RMSSD heart rate variability, and mechanical sEMG load.
4. **Real-time Alerting**: If ACWR exceeds 1.35 or HRV drops > 15%, alerts coach and automatically calibrates next training session.

### 2.2 Computer Vision Biomechanics Pipeline
```mermaid
sequenceDiagram
    participant Athlete as Athlete / Camera
    participant CV as Pose Estimation Engine
    participant Kinematics as Kinematic Analyzer
    participant DB as System Database
    participant Coach as Virtual Coach UI

    Athlete->>CV: Stream Video Frame / Skeletal Keypoints
    CV->>Kinematics: Extract 33 3D Spatial Landmarks
    Kinematics->>Kinematics: Calculate Joint Angles (Knee, Hip, Elbow, Trunk)
    Kinematics->>Kinematics: Compute Bilateral Symmetry & Kinetic Chain Score
    Kinematics->>DB: Store Frame Moment & Biomechanical Metrics
    Kinematics->>Coach: Display Visual Skeleton Overlay & Actionable Cues
```

---

## 3. Database Schema (Entity-Relationship)

```mermaid
erDiagram
    USERS ||--|| ATHLETE_PROFILES : has
    USERS ||--o{ BIOMETRIC_TELEMETRY : streams
    USERS ||--o{ TRAINING_PROGRAMS : assigned
    USERS ||--o{ INJURY_ASSESSMENTS : receives
    USERS ||--o{ VIDEO_ANALYSES : logs
    USERS ||--|| GAMIFICATION : tracks
    USERS ||--o{ COACHING_MESSAGES : exchanges

    USERS {
        int id PK
        string username
        string email
        string full_name
        string role
        string sport
        string avatar_url
    }

    ATHLETE_PROFILES {
        int id PK
        int user_id FK
        int age
        float height_cm
        float weight_kg
        string primary_position
        float vo2_max
        int resting_hr
        int max_hr
    }

    BIOMETRIC_TELEMETRY {
        int id PK
        int user_id FK
        timestamp timestamp
        int heart_rate
        float hrv_ms
        float speed_kmh
        int cadence_spm
        float muscle_load_pct
        float fatigue_index
    }

    INJURY_ASSESSMENTS {
        int id PK
        int user_id FK
        float risk_score
        string risk_level
        float acwr_ratio
        float acute_load
        float chronic_load
        string flagged_body_parts
        string recommendations_json
    }

    TRAINING_PROGRAMS {
        int id PK
        int user_id FK
        int coach_id FK
        string title
        string sport
        string phase
        string target_goal
        string schedule_json
    }

    GAME_STRATEGIES {
        int id PK
        string sport
        string match_title
        string opponent_name
        string formation_setup
        string tactical_analysis_json
        string counter_tactics_json
        string simulation_result_json
    }
```

---

## 4. Non-Functional Architecture & Scaling

1. **Sub-100ms Latency**: Real-time sensor stream ingestion uses asynchronous processing and in-memory caches for rolling telemetry.
2. **Scalability**: Stateless microservices architecture for AI inference. The model inference nodes can scale horizontally behind load balancers.
3. **Data Privacy & Compliance**: Health metrics and biometric data conform to HIPAA / GDPR requirements; data is encrypted in transit (TLS 1.3) and at rest (AES-256).
4. **Role-Based Access Control (RBAC)**:
   - **Athlete**: Access to own profile, telemetry, adaptive workouts, coach chat, and badges.
   - **Coach / Trainer**: Full access to all team athletes, ability to adjust workout prescriptions, review squad injury risk dashboard, run tactical scenarios.
   - **Sports Analyst**: In-depth biomechanics analysis, kinematic angles, telemetry data exports, and tactical simulation modeling.
   - **Admin**: Full system management, user role assignments, audit logs.
