/**
 * Main Application Orchestrator for Athelytix AI Sports Coaching Platform
 */

document.addEventListener('DOMContentLoaded', () => {
  let currentAthleteId = 2;
  let currentRole = 'athlete';
  let athleteData = null;

  // Initialize Sub-Systems
  const cvVisualizer = new BiomechanicsVisualizer('poseCanvas');
  const tacticalSimulator = new TacticalPitchSimulator('tacticalPitch');
  const voiceCoach = new VoiceCoachAssistant('chatMessages', 'chatInput', 'chatSendBtn', 'voiceToggleBtn');

  // Sparkline Canvases
  const hrCanvas = document.getElementById('hrChartCanvas');
  const hrCtx = hrCanvas ? hrCanvas.getContext('2d') : null;

  const iotStreamer = new IoTTelemetryStreamer(currentAthleteId, (packet, hrHist, speedHist) => {
    // Update live metrics cards
    const hrEl = document.getElementById('metric-hr');
    if (hrEl) hrEl.textContent = packet.heart_rate;
    const hrvEl = document.getElementById('metric-hrv');
    if (hrvEl) hrvEl.textContent = packet.hrv_ms;
    const speedEl = document.getElementById('metric-speed');
    if (speedEl) speedEl.textContent = packet.speed_kmh;
    const muscleEl = document.getElementById('metric-muscle');
    if (muscleEl) muscleEl.textContent = `${packet.muscle_load_pct}%`;
    const fatigueEl = document.getElementById('metric-fatigue');
    if (fatigueEl) fatigueEl.textContent = `${packet.fatigue_index}%`;

    // Render sparkline
    if (hrCtx && hrCanvas) {
      drawSparkline(hrCtx, hrCanvas, hrHist, '#00f2fe');
    }
  });

  // Tab Navigation Handling
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-tab');
      tabBtns.forEach((b) => b.classList.remove('active'));
      tabPanels.forEach((p) => p.classList.remove('active'));

      btn.classList.add('active');
      const activePanel = document.getElementById(`tab-${target}`);
      if (activePanel) activePanel.classList.add('active');

      if (target === 'biomechanics') {
        cvVisualizer.resizeCanvas();
      } else if (target === 'skills') {
        drawSkillRadar();
      }
    });
  });

  // Role Switching Logic
  const roleSelect = document.getElementById('roleSelector');
  if (roleSelect) {
    roleSelect.addEventListener('change', (e) => {
      currentRole = e.target.value;
      const roleBadge = document.getElementById('currentRoleDisplay');
      if (roleBadge) {
        roleBadge.textContent = `Role: ${currentRole.toUpperCase()}`;
      }
      applyRolePermissions(currentRole);
    });
  }

  function applyRolePermissions(role) {
    const coachOnlyElements = document.querySelectorAll('.coach-only');
    const analystOnlyElements = document.querySelectorAll('.analyst-only');

    coachOnlyElements.forEach(el => {
      el.style.display = (role === 'coach' || role === 'admin') ? '' : 'none';
    });
    analystOnlyElements.forEach(el => {
      el.style.display = (role === 'analyst' || role === 'coach' || role === 'admin') ? '' : 'none';
    });
  }

  // Athlete Switching
  const athleteSelect = document.getElementById('athleteSelector');
  if (athleteSelect) {
    athleteSelect.addEventListener('change', (e) => {
      currentAthleteId = parseInt(e.target.value);
      iotStreamer.setUserId(currentAthleteId);
      voiceCoach.setUserId(currentAthleteId);
      loadAthleteOverview(currentAthleteId);
    });
  }

  // Load Athlete Overview
  async function loadAthleteOverview(userId) {
    try {
      const resp = await fetch(`/api/athlete/${userId}/overview`);
      athleteData = await resp.json();
      renderAthleteDetails(athleteData);
    } catch (err) {
      console.error("Error loading athlete overview:", err);
    }
  }

  function renderAthleteDetails(data) {
    if (!data || !data.user) return;
    const u = data.user;
    const p = data.profile || {};

    // Banner
    const nameEl = document.getElementById('athleteBannerName');
    if (nameEl) nameEl.textContent = u.full_name;
    const sportEl = document.getElementById('athleteBannerSport');
    if (sportEl) sportEl.textContent = `${u.sport} • ${p.primary_position || 'Pro Player'}`;
    const avatarEl = document.getElementById('athleteBannerAvatar');
    if (avatarEl && u.avatar_url) avatarEl.src = u.avatar_url;

    // Stat boxes
    const vo2El = document.getElementById('bannerVo2');
    if (vo2El) vo2El.textContent = `${p.vo2_max || 56.0} ml/kg/min`;
    const restHrEl = document.getElementById('bannerRestHr');
    if (restHrEl) restHrEl.textContent = `${p.resting_hr || 50} bpm`;
    const maxHrEl = document.getElementById('bannerMaxHr');
    if (maxHrEl) maxHrEl.textContent = `${p.max_hr || 195} bpm`;

    // Training Schedule
    if (data.training_program) {
      renderTrainingSchedule(data.training_program);
    }

    // Injury
    if (data.injury_assessment) {
      renderInjury(data.injury_assessment);
    }

    // Gamification
    if (data.gamification) {
      renderGamification(data.gamification);
    }

    // Radar
    drawSkillRadar(data.skills);
  }

  function renderTrainingSchedule(program) {
    const titleEl = document.getElementById('trainingProgramTitle');
    if (titleEl) titleEl.textContent = program.title;
    const goalEl = document.getElementById('trainingGoalText');
    if (goalEl) goalEl.textContent = program.target_goal;

    const tbody = document.getElementById('trainingScheduleBody');
    if (!tbody || !program.schedule) return;

    const list = Array.isArray(program.schedule) ? program.schedule : (program.schedule.daily_schedule || []);
    tbody.innerHTML = '';
    list.forEach(item => {
      const row = document.createElement('tr');
      const exercisesStr = item.exercises ? item.exercises.join(', ') : (item.target_hr_zone || 'Core Focus');
      row.innerHTML = `
        <td><strong>${item.day}</strong></td>
        <td>${item.focus}</td>
        <td><span class="intensity-badge intensity-${item.intensity}">${item.intensity}</span></td>
        <td>${item.duration_min} min</td>
        <td style="color: var(--text-secondary); font-size: 12px;">${exercisesStr}</td>
      `;
      tbody.appendChild(row);
    });
  }

  function renderInjury(injury) {
    const acwrEl = document.getElementById('acwrDisplayVal');
    if (acwrEl) acwrEl.textContent = injury.acwr_ratio.toFixed(2);

    const riskEl = document.getElementById('injuryRiskLevel');
    if (riskEl) {
      riskEl.textContent = injury.risk_level.toUpperCase();
      riskEl.className = `trend-${injury.risk_level === 'Low' ? 'good' : (injury.risk_level === 'Moderate' ? 'warning' : 'danger')}`;
    }

    const recsList = document.getElementById('injuryRecsList');
    if (recsList && injury.recommendations) {
      recsList.innerHTML = '';
      injury.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.style.marginBottom = '8px';
        li.textContent = rec;
        recsList.appendChild(li);
      });
    }
  }

  function renderGamification(g) {
    const ptsEl = document.getElementById('gamificationPoints');
    if (ptsEl) ptsEl.textContent = g.points.toLocaleString();
    const lvlEl = document.getElementById('gamificationLevel');
    if (lvlEl) lvlEl.textContent = `Lvl ${g.level}`;
    const streakEl = document.getElementById('gamificationStreak');
    if (streakEl) streakEl.textContent = `${g.streak_days} Days`;

    const badgeContainer = document.getElementById('badgesContainer');
    if (badgeContainer && g.badges) {
      badgeContainer.innerHTML = '';
      g.badges.forEach(b => {
        const div = document.createElement('div');
        div.className = `badge-card ${b.unlocked ? 'unlocked' : ''}`;
        div.innerHTML = `
          <div class="badge-icon">${b.icon}</div>
          <div class="badge-name">${b.name}</div>
          <div class="badge-desc">${b.description}</div>
          ${b.unlocked ? '<div style="font-size:10px; color:var(--emerald); margin-top:6px;">UNLOCKED</div>' : '<div style="font-size:10px; color:var(--text-muted); margin-top:6px;">LOCKED</div>'}
        `;
        badgeContainer.appendChild(div);
      });
    }
  }

  // Draw Sparkline Graph
  function drawSparkline(ctx, canvas, values, strokeColor) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    if (values.length < 2) return;
    const minVal = Math.min(...values) - 5;
    const maxVal = Math.max(...values) + 5;
    const range = maxVal - minVal || 1;

    ctx.beginPath();
    values.forEach((v, idx) => {
      const x = (idx / (values.length - 1)) * w;
      const y = h - ((v - minVal) / range) * h;
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = strokeColor;
    ctx.shadowBlur = 8;
    ctx.stroke();
    ctx.shadowBlur = 0;
  }

  // Draw Skill Radar Chart on Canvas
  function drawSkillRadar(skillObj) {
    const radarCanvas = document.getElementById('skillRadarCanvas');
    if (!radarCanvas) return;
    const ctx = radarCanvas.getContext('2d');
    const w = radarCanvas.width = 360;
    const h = radarCanvas.height = 300;
    const cx = w / 2;
    const cy = h / 2;
    const radius = 105;

    ctx.clearRect(0, 0, w, h);

    const categories = ['Speed', 'Agility', 'Endurance', 'Technique', 'Tactical'];
    const count = categories.length;
    const step = (Math.PI * 2) / count;

    // Draw concentric polygons
    for (let level = 1; level <= 5; level++) {
      const r = (radius / 5) * level;
      ctx.beginPath();
      for (let i = 0; i < count; i++) {
        const angle = i * step - Math.PI / 2;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Draw radial axes and labels
    for (let i = 0; i < count; i++) {
      const angle = i * step - Math.PI / 2;
      const x = cx + radius * Math.cos(angle);
      const y = cy + radius * Math.sin(angle);

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
      ctx.stroke();

      // Label text
      const lx = cx + (radius + 24) * Math.cos(angle);
      const ly = cy + (radius + 16) * Math.sin(angle);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(categories[i], lx, ly + 4);
    }

    // Default or dynamic skill values (0-100)
    const vals = [
      (skillObj && skillObj.speed) || 91,
      (skillObj && skillObj.agility) || 88,
      (skillObj && skillObj.endurance) || 86,
      (skillObj && skillObj.technique) || 93,
      (skillObj && skillObj.tactical) || 85
    ];

    // Plot athlete data polygon
    ctx.beginPath();
    vals.forEach((v, i) => {
      const angle = i * step - Math.PI / 2;
      const r = (radius * (v / 100));
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 242, 254, 0.25)';
    ctx.fill();
    ctx.strokeStyle = '#00f2fe';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Peer average polygon (benchmark comparison)
    const peerVals = [78, 75, 80, 72, 70];
    ctx.beginPath();
    peerVals.forEach((v, i) => {
      const angle = i * step - Math.PI / 2;
      const r = (radius * (v / 100));
      const x = cx + r * Math.cos(angle);
      const y = cy + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(245, 158, 11, 0.12)';
    ctx.fill();
    ctx.strokeStyle = '#f59e0b';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Quick Chat Prompts click listeners
  document.querySelectorAll('.quick-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      const promptText = pill.getAttribute('data-prompt');
      voiceCoach.sendMessage(promptText);
    });
  });

  // Movement Preset Selector
  const movementSelect = document.getElementById('movementSelect');
  if (movementSelect) {
    movementSelect.addEventListener('change', (e) => {
      cvVisualizer.loadSimulationFrames(e.target.value);
    });
  }

  // Play / Pause CV Button
  const toggleCvBtn = document.getElementById('toggleCvPlayBtn');
  if (toggleCvBtn) {
    toggleCvBtn.addEventListener('click', () => {
      const playing = cvVisualizer.togglePlay();
      toggleCvBtn.textContent = playing ? '⏸ Pause' : '▶ Play';
    });
  }

  // Regenerate Adaptive Training Plan Button
  const adaptPlanBtn = document.getElementById('btnAdaptTraining');
  if (adaptPlanBtn) {
    adaptPlanBtn.addEventListener('click', async () => {
      adaptPlanBtn.textContent = '⚡ Optimizing Plan...';
      try {
        const resp = await fetch('/api/training/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sport: athleteData ? athleteData.user.sport : "Soccer",
            goal: "Max Aerobic Speed & Hamstring Protection",
            fatigue_level: 68.0,
            acwr: 1.38,
            user_id: currentAthleteId
          })
        });
        const data = await resp.json();
        if (data.program) {
          renderTrainingSchedule({
            title: `AI-Adaptive ${athleteData.user.sport} Microcycle`,
            target_goal: data.program.target_goal,
            schedule: data.program.schedule
          });
          alert('Adaptive Training Plan calibrated based on elevated ACWR and fatigue index!');
        }
      } catch (e) {
        console.error(e);
      } finally {
        adaptPlanBtn.textContent = '⚡ Re-Calibrate Adaptive Plan';
      }
    });
  }

  // Run Tactical Simulation Button
  const runSimBtn = document.getElementById('btnRunSimulation');
  if (runSimBtn) {
    runSimBtn.addEventListener('click', async () => {
      runSimBtn.textContent = '⏳ Simulating 2,000 Scenarios...';
      const sim = await tacticalSimulator.runSimulation("Soccer", "Red Stars FC", "4-3-3 High Press");
      runSimBtn.textContent = '🎲 Run Monte Carlo Simulation';
      if (sim && sim.simulation) {
        document.getElementById('simWinPct').textContent = `${sim.simulation.win_probability_pct}%`;
        document.getElementById('simExpGoals').textContent = `${sim.simulation.expected_score_team} - ${sim.simulation.expected_score_opponent}`;
        document.getElementById('simRecPace').textContent = sim.recommended_tempo;
      }
    });
  }

  // Initial Load
  loadAthleteOverview(currentAthleteId);
  applyRolePermissions(currentRole);
});
