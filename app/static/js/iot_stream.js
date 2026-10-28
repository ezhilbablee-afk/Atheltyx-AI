/**
 * Wearable IoT Sensor Telemetry Simulator & Live Graphing
 */

class IoTTelemetryStreamer {
  constructor(userId, updateCallback) {
    this.userId = userId;
    this.updateCallback = updateCallback;
    this.timer = null;
    this.historyHR = [142, 145, 148, 152, 150, 155, 158, 162, 160, 164];
    this.historySpeed = [18.2, 19.5, 21.0, 24.2, 26.5, 28.0, 29.8, 31.2, 27.5, 22.0];
    this.historyMuscleLoad = [58, 62, 65, 70, 74, 76, 78, 82, 80, 79];
    this.isStreaming = true;
    this.start();
  }

  setUserId(id) {
    this.userId = id;
  }

  start() {
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(() => {
      if (!this.isStreaming) return;
      this.tick();
    }, 2000);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  tick() {
    // Generate realistic athletic telemetry variations
    const lastHR = this.historyHR[this.historyHR.length - 1];
    const hrDelta = Math.floor(Math.random() * 5) - 2;
    const newHR = Math.max(120, min(188, lastHR + hrDelta));

    const newSpeed = +(Math.random() * 14 + 18).toFixed(1);
    const newCadence = Math.floor(Math.random() * 12 + 168);
    const newHRV = +(Math.random() * 8 + 58).toFixed(1);
    const newMuscleLoad = +(Math.random() * 15 + 65).toFixed(1);
    const newFatigue = +(Math.random() * 8 + 24).toFixed(1);
    const newPower = +(Math.random() * 40 + 240).toFixed(1);

    this.historyHR.push(newHR);
    if (this.historyHR.length > 20) this.historyHR.shift();

    this.historySpeed.push(newSpeed);
    if (this.historySpeed.length > 20) this.historySpeed.shift();

    const packet = {
      heart_rate: newHR,
      hrv_ms: newHRV,
      speed_kmh: newSpeed,
      cadence_spm: newCadence,
      muscle_load_pct: newMuscleLoad,
      fatigue_index: newFatigue,
      power_watts: newPower,
      timestamp: new Date().toLocaleTimeString()
    };

    // Send to backend API
    fetch(`/api/athlete/${this.userId}/telemetry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(packet)
    }).catch(() => {});

    if (this.updateCallback) {
      this.updateCallback(packet, this.historyHR, this.historySpeed);
    }
  }
}

function min(a, b) { return a < b ? a : b; }

window.IoTTelemetryStreamer = IoTTelemetryStreamer;
