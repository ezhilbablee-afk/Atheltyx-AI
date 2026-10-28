/**
 * Virtual AI Coach & Speech Assistant
 */

class VoiceCoachAssistant {
  constructor(chatContainerId, inputId, sendBtnId, voiceToggleId) {
    this.chatContainer = document.getElementById(chatContainerId);
    this.input = document.getElementById(inputId);
    this.sendBtn = document.getElementById(sendBtnId);
    this.voiceToggle = document.getElementById(voiceToggleId);
    this.isVoiceEnabled = true;
    this.currentUserId = 2;
    this.init();
  }

  init() {
    if (this.sendBtn) {
      this.sendBtn.addEventListener('click', () => this.sendMessage());
    }
    if (this.input) {
      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') this.sendMessage();
      });
    }
    if (this.voiceToggle) {
      this.voiceToggle.addEventListener('click', () => {
        this.isVoiceEnabled = !this.isVoiceEnabled;
        this.voiceToggle.textContent = this.isVoiceEnabled ? '🔊 Voice On' : '🔇 Voice Off';
        this.voiceToggle.style.opacity = this.isVoiceEnabled ? '1' : '0.6';
      });
    }
  }

  setUserId(id) {
    this.currentUserId = id;
  }

  async sendMessage(customText = null) {
    const text = customText || (this.input ? this.input.value.trim() : "");
    if (!text) return;

    if (this.input && !customText) this.input.value = "";

    // Add user bubble
    this.addBubble(text, 'user');

    try {
      const resp = await fetch('/api/coach/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, user_id: this.currentUserId })
      });
      const data = await resp.json();

      if (data.reply) {
        this.addBubble(data.reply, 'assistant', data.actionable_tip);
        if (this.isVoiceEnabled && 'speechSynthesis' in window) {
          this.speak(data.reply);
        }
      }
    } catch (err) {
      this.addBubble("Network error communicating with AI Coaching Engine.", 'assistant');
    }
  }

  addBubble(text, sender, tip = null) {
    if (!this.chatContainer) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;
    bubble.innerHTML = `<div>${text}</div>`;

    if (tip) {
      const tipEl = document.createElement('div');
      tipEl.className = 'action-tip-box';
      tipEl.innerHTML = `<strong>💡 Key Actionable Cue:</strong> ${tip}`;
      bubble.appendChild(tipEl);
    }

    this.chatContainer.appendChild(bubble);
    this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
  }

  speak(text) {
    try {
      window.speechSynthesis.cancel();
      const cleanText = text.replace(/[*_#]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      // Audio speech output not supported or blocked by browser permissions
    }
  }
}

window.VoiceCoachAssistant = VoiceCoachAssistant;
