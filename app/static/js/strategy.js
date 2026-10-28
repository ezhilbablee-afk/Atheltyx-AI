/**
 * Tactical Game Strategy Optimization and Pitch Simulator
 */

class TacticalPitchSimulator {
  constructor(pitchId) {
    this.pitch = document.getElementById(pitchId);
    this.formation = "4-2-3-1";
    this.init();
  }

  init() {
    this.renderPositions();
  }

  renderPositions() {
    if (!this.pitch) return;
    this.pitch.innerHTML = `
      <div class="pitch-half-line"></div>
      <div class="pitch-center-circle"></div>
    `;

    // Coordinates (percentage left, percentage top) for 4-2-3-1 Asymmetric Dynamic
    const homeTeam = [
      { num: '1', l: 5, t: 50, role: 'GK' },
      { num: '2', l: 22, t: 18, role: 'RB' },
      { num: '4', l: 18, t: 38, role: 'CB' },
      { num: '5', l: 18, t: 62, role: 'CB' },
      { num: '3', l: 22, t: 82, role: 'LB' },
      { num: '6', l: 36, t: 38, role: 'DM' },
      { num: '8', l: 36, t: 62, role: 'DM' },
      { num: '7', l: 56, t: 20, role: 'RW' },
      { num: '10', l: 54, t: 50, role: 'AM' },
      { num: '11', l: 56, t: 80, role: 'LW' },
      { num: '9', l: 72, t: 50, role: 'CF' }
    ];

    const awayTeam = [
      { num: '1', l: 95, t: 50, role: 'GK' },
      { num: '2', l: 82, t: 22, role: 'CB' },
      { num: '3', l: 82, t: 50, role: 'CB' },
      { num: '4', l: 82, t: 78, role: 'CB' },
      { num: '6', l: 68, t: 32, role: 'CM' },
      { num: '8', l: 68, t: 68, role: 'CM' },
      { num: '7', l: 52, t: 15, role: 'RF' },
      { num: '9', l: 45, t: 50, role: 'ST' },
      { num: '11', l: 52, t: 85, role: 'LF' }
    ];

    homeTeam.forEach((p) => {
      const el = document.createElement('div');
      el.className = 'tactical-player team-home';
      el.style.left = `${p.l}%`;
      el.style.top = `${p.t}%`;
      el.textContent = p.num;
      el.title = `${p.role} (Home)`;
      this.pitch.appendChild(el);
    });

    awayTeam.forEach((p) => {
      const el = document.createElement('div');
      el.className = 'tactical-player team-away';
      el.style.left = `${p.l}%`;
      el.style.top = `${p.t}%`;
      el.textContent = p.num;
      el.title = `${p.role} (Opponent)`;
      this.pitch.appendChild(el);
    });
  }

  async runSimulation(sport, opponent, style) {
    try {
      const resp = await fetch('/api/strategy/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sport, opponent_name: opponent, opponent_style: style })
      });
      const data = await resp.json();
      return data.result;
    } catch (err) {
      console.error("Simulation failed", err);
      return null;
    }
  }
}

window.TacticalPitchSimulator = TacticalPitchSimulator;
