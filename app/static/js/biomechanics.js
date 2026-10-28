/**
 * Biomechanics and Computer Vision Skeletal Kinematics Visualizer
 */

class BiomechanicsVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    this.frames = [];
    this.currentFrameIdx = 0;
    this.isPlaying = true;
    this.animationId = null;
    this.movementType = "Soccer Strike";
    this.init();
  }

  init() {
    if (!this.canvas) return;
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
    this.loadSimulationFrames(this.movementType);
  }

  resizeCanvas() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width;
    this.canvas.height = rect.height;
  }

  async loadSimulationFrames(movement) {
    this.movementType = movement;
    try {
      const resp = await fetch(`/api/biomechanics/simulation?movement=${encodeURIComponent(movement)}`);
      const data = await resp.json();
      this.frames = data.frames || [];
      this.currentFrameIdx = 0;
      if (!this.animationId) {
        this.animate();
      }
    } catch (err) {
      console.error("Failed to load simulation frames", err);
    }
  }

  animate() {
    this.render();
    if (this.isPlaying && this.frames.length > 0) {
      this.currentFrameIdx = (this.currentFrameIdx + 1) % this.frames.length;
    }
    setTimeout(() => {
      this.animationId = requestAnimationFrame(() => this.animate());
    }, 120);
  }

  render() {
    if (!this.ctx || !this.frames.length) return;
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;

    // Dark grid background
    ctx.fillStyle = '#0a0f1d';
    ctx.fillRect(0, 0, w, h);

    // Subtle tactical grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    const frame = this.frames[this.currentFrameIdx];
    if (!frame) return;
    const kp = frame.keypoints;

    // Skeleton bone connections
    const bones = [
      ['nose', 'neck'],
      ['neck', 'right_shoulder'],
      ['neck', 'left_shoulder'],
      ['right_shoulder', 'right_elbow'],
      ['right_elbow', 'right_wrist'],
      ['left_shoulder', 'left_elbow'],
      ['left_elbow', 'left_wrist'],
      ['neck', 'pelvis'],
      ['pelvis', 'right_hip'],
      ['pelvis', 'left_hip'],
      ['right_hip', 'right_knee'],
      ['right_knee', 'right_ankle'],
      ['left_hip', 'left_knee'],
      ['left_knee', 'left_ankle']
    ];

    // Scale coordinates
    const scale = Math.min(w, h) * 0.9;
    const offsetX = (w - scale) / 2;
    const offsetY = (h - scale) / 2;

    const toScreen = (pt) => ({
      x: offsetX + pt.x * scale,
      y: offsetY + pt.y * scale
    });

    // Draw bones
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';

    bones.forEach(([b1, b2]) => {
      if (kp[b1] && kp[b2]) {
        const p1 = toScreen(kp[b1]);
        const p2 = toScreen(kp[b2]);

        const grad = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
        grad.addColorStop(0, '#00f2fe');
        grad.addColorStop(1, '#3b82f6');

        ctx.strokeStyle = grad;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
    });

    // Draw keypoint joints
    Object.keys(kp).forEach((joint) => {
      const p = toScreen(kp[joint]);
      ctx.beginPath();
      ctx.arc(p.x, p.y, 6, 0, Math.PI * 2);
      ctx.fillStyle = joint.includes('knee') || joint.includes('hip') ? '#10b981' : '#00f2fe';
      ctx.shadowColor = '#00f2fe';
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    });

    // Update HUD indicator on DOM
    const phaseEl = document.getElementById('cv-phase-name');
    if (phaseEl) phaseEl.textContent = `PHASE: ${frame.phase_name.toUpperCase()}`;
    const frameEl = document.getElementById('cv-frame-count');
    if (frameEl) frameEl.textContent = `FRAME: ${frame.frame_id}/12`;
  }

  togglePlay() {
    this.isPlaying = !this.isPlaying;
    return this.isPlaying;
  }
}

window.BiomechanicsVisualizer = BiomechanicsVisualizer;
