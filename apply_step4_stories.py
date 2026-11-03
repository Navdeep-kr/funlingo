import re

file_path = 'index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

initial_len = len(content)

# 1. Add CSS for Spoken Story Enhancements
stories_css = """
    /* ==========================================================================
       STEP 4: INTERACTIVE BRANCHING "COFFEE BREAK" SPOKEN STORIES
       ========================================================================== */
    .story-role-banner {
      background: linear-gradient(135deg, #F3E8FF, #EDE9FE);
      border: 2px solid var(--color-purple);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
    }

    .story-role-chip {
      background: var(--color-purple);
      color: #FFFFFF;
      font-size: 0.72rem;
      font-weight: 900;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      letter-spacing: 0.5px;
    }

    .talk-option-btn {
      transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
      position: relative;
      overflow: hidden;
    }

    .talk-option-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 0 var(--shadow-3d-base);
      border-color: var(--color-purple);
    }

    .talk-option-btn.opt-speaking {
      border-color: var(--color-sky) !important;
      background: #F0F9FF !important;
      box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.3) !important;
    }

    .opt-speak-btn {
      background: var(--color-purple-tint);
      color: var(--color-purple);
      border: 1.5px solid var(--color-purple);
      border-radius: var(--radius-pill);
      padding: 4px 10px;
      font-size: 0.75rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s ease;
    }

    .opt-speak-btn:hover {
      background: var(--color-purple);
      color: #FFFFFF;
      transform: scale(1.05);
    }

    .talk-typing-indicator {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 6px 12px;
      background: var(--bg-surface);
      border: 2px solid var(--border-subtle);
      border-radius: var(--radius-pill);
      font-size: 0.78rem;
      font-weight: 800;
      color: var(--color-purple);
      margin: 8px 0;
      animation: fadeIn 0.2s ease;
    }
"""

if "STEP 4: INTERACTIVE BRANCHING \"COFFEE BREAK\" SPOKEN STORIES" not in content:
    target_anchor = ".talk-bubble-user {"
    anchor_idx = content.find(target_anchor)
    if anchor_idx != -1:
        close_brace = content.find("}", anchor_idx)
        content = content[:close_brace+1] + "\n" + stories_css + content[close_brace+1:]
        print("[CSS] Inserted Spoken Stories CSS.")

# 2. Update TalkEngine chooseOption, renderStep, and showReport
old_talk_methods_pattern = r'renderStep\(\)\s*\{[\s\S]*?chooseOption\(optionIndex,\s*wasSpoken = false\)\s*\{[\s\S]*?showReport\(\)\s*\{[\s\S]*?document\.getElementById\(\'talkReportOverlay\'\)\.classList\.add\(\'active\'\);\s*\}'

new_talk_methods = """renderStep() {
        const sc = this.currentScenario;
        const step = sc.dialogue[this.currentStep];
        if (!step) {
          this.showReport();
          return;
        }

        const totalSteps = sc.dialogue.length;
        document.getElementById('talkStepCounter').textContent = `Exchange ${this.currentStep + 1} of ${totalSteps}`;

        // Render Character Opening Line
        const stream = document.getElementById('talkChatStream');
        const charRow = document.createElement('div');
        charRow.className = 'talk-msg-row';
        charRow.innerHTML = `
          <div class="talk-avatar-bubble">${sc.character.avatar}</div>
          <div class="talk-bubble-char">
            <div style="font-size: 0.72rem; font-weight: 900; color: var(--color-purple); margin-bottom: 2px;">
              ${sc.character.name}
            </div>
            <div style="font-size: 0.95rem; font-weight: 800; line-height: 1.35; color: var(--text-main);">
              "${step.characterSays}"
            </div>
            <button class="char-speaker-btn" onclick="speakTutorText('${step.characterSays.replace(/'/g, "\\\\'")}', 0.9)">
              <span>🔊 Replay</span>
            </button>
          </div>
        `;
        stream.appendChild(charRow);
        stream.scrollTop = stream.scrollHeight;

        // Auto-play dialogue voice
        speakTutorText(step.characterSays, 0.9);

        // Render Interactive Branching Options with Speak Aloud trigger
        const optContainer = document.getElementById('talkOptionsList');
        optContainer.innerHTML = `
          <div class="story-role-banner">
            <span style="font-size: 0.82rem; font-weight: 800; color: var(--color-purple);">Your turn to reply:</span>
            <span class="story-role-chip">🎙️ Speak or Tap Below</span>
          </div>
          ${step.options.map((opt, idx) => `
            <div class="talk-option-btn" id="talkOptCard-${idx}" onclick="talkEngine.chooseOption(${idx})">
              <div class="talk-opt-text">"${opt.text}"</div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px; width: 100%;">
                <span class="talk-opt-tone">${opt.tone}</span>
                <div style="display: flex; gap: 6px;">
                  <button type="button" class="opt-speak-btn" onclick="event.stopPropagation(); talkEngine.speakSpecificOption(${idx})">
                    <span>🎙️ Speak This</span>
                  </button>
                  <button type="button" class="btn-3d btn-ghost btn-pill" style="font-size: 0.68rem; padding: 2px 6px;" onclick="event.stopPropagation(); speakTutorText('${opt.text.replace(/'/g, "\\\\'")}', 0.85)">
                    🎧
                  </button>
                </div>
              </div>
            </div>
          `).join('')}
        `;

        // Wire Mic trigger
        const micBtn = document.getElementById('talkMicTrigger');
        micBtn.innerHTML = `<span>🎙️ Tap & Speak Any Reply Aloud</span>`;
        micBtn.onclick = () => this.listenSpokenSpeech(step.options);
      }

      speakSpecificOption(optionIndex) {
        const sc = this.currentScenario;
        const step = sc.dialogue[this.currentStep];
        const opt = step.options[optionIndex];
        if (!opt) return;

        const card = document.getElementById(`talkOptCard-${optionIndex}`);
        if (card) card.classList.add('opt-speaking');

        sounds.playPop();
        showToast(`Speak aloud: "${opt.text}" 🎙️`);

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRec) {
          setTimeout(() => this.chooseOption(optionIndex, true), 800);
          return;
        }

        const recog = new SpeechRec();
        recog.lang = appState.recognitionLang || 'en-US';

        recog.onresult = (e) => {
          if (card) card.classList.remove('opt-speaking');
          sounds.playSuccessChime();
          this.chooseOption(optionIndex, true);
        };

        recog.onerror = () => {
          if (card) card.classList.remove('opt-speaking');
          this.chooseOption(optionIndex, true);
        };

        try { recog.start(); } catch(err) {
          if (card) card.classList.remove('opt-speaking');
          this.chooseOption(optionIndex, true);
        }
      }

      chooseOption(optionIndex, wasSpoken = false) {
        const sc = this.currentScenario;
        const step = sc.dialogue[this.currentStep];
        const opt = step.options[optionIndex];
        if (!opt) return;

        sounds.playPop();

        // Track stats
        this.totalPhrasesAnswered++;
        if (opt.isPolite) this.politePhrasesUsed++;
        this.fluencyPoints += (wasSpoken ? 40 : 30);
        this.userChosenOptions.push({ stepIndex: this.currentStep, chosen: opt });

        // 1. Render User Bubble
        const stream = document.getElementById('talkChatStream');
        const userRow = document.createElement('div');
        userRow.className = 'talk-msg-row user-msg';
        userRow.innerHTML = `
          <div class="talk-avatar-bubble">🐥</div>
          <div class="talk-bubble-user">
            "${opt.text}"
            <div style="font-size: 0.68rem; opacity: 0.85; margin-top: 2px;">
              ${wasSpoken ? '🎙️ Spoken Aloud' : '✓ Selected'}
            </div>
          </div>
        `;
        stream.appendChild(userRow);
        stream.scrollTop = stream.scrollHeight;

        // 2. Character Typing Indicator
        const optContainer = document.getElementById('talkOptionsList');
        optContainer.innerHTML = `
          <div class="talk-typing-indicator">
            <span>✨</span>
            <span>${sc.character.name} is speaking...</span>
          </div>
        `;

        // 3. Render Character Dynamic Response
        setTimeout(() => {
          if (opt.charReply) {
            const replyRow = document.createElement('div');
            replyRow.className = 'talk-msg-row';
            replyRow.innerHTML = `
              <div class="talk-avatar-bubble">${sc.character.avatar}</div>
              <div class="talk-bubble-char">
                <div style="font-size: 0.72rem; font-weight: 900; color: var(--color-purple); margin-bottom: 2px;">
                  ${sc.character.name}
                </div>
                <div style="font-size: 0.95rem; font-weight: 800; line-height: 1.35; color: var(--text-main);">
                  "${opt.charReply}"
                </div>
                <button class="char-speaker-btn" onclick="speakTutorText('${opt.charReply.replace(/'/g, "\\\\'")}', 0.9)">
                  <span>🔊</span>
                </button>
              </div>
            `;
            stream.appendChild(replyRow);
            stream.scrollTop = stream.scrollHeight;
            speakTutorText(opt.charReply, 0.9);
          }

          // Advance to next step after speech finishes
          setTimeout(() => {
            this.currentStep++;
            this.renderStep();
          }, 1400);
        }, 600);
      }

      showReport() {
        sounds.playLevelUp();
        triggerConfetti();

        const sc = this.currentScenario;
        const totalSteps = sc.dialogue.length;

        // Calculate Fluency Score
        const baseScore = 80;
        const politeBonus = Math.round((this.politePhrasesUsed / totalSteps) * 15);
        const completionBonus = 5;
        const finalFluency = Math.min(100, baseScore + politeBonus + completionBonus);

        // Award XP and Gems for completing story!
        awardXP(40, true);
        appState.gems = (appState.gems || 0) + 5;
        saveState(appState);

        // Update Report UI
        document.getElementById('reportScenarioTitle').textContent = `📖 Story Complete: ${sc.title}`;
        document.getElementById('reportCharRole').textContent = `Partner: ${sc.character.avatar} ${sc.character.name} (${sc.character.role})`;
        document.getElementById('reportFluencyScore').textContent = `${finalFluency}%`;
        document.getElementById('reportPoliteCount').textContent = `${this.politePhrasesUsed}/${totalSteps} Modals Used`;
        document.getElementById('reportPhrasesPracticed').textContent = `${this.totalPhrasesAnswered} Spoken Exchanges (+40 XP ⚡ +5 💎)`;

        const upgradesBox = document.getElementById('reportUpgradesList');
        if (sc.upgrades && sc.upgrades.length > 0) {
          upgradesBox.innerHTML = sc.upgrades.map(u => `
            <div style="background: var(--bg-surface); border: 2px solid var(--border-subtle); border-radius: var(--radius-md); padding: 10px 12px; margin-bottom: 8px;">
              <div style="color: var(--color-coral); text-decoration: line-through; font-size: 0.78rem; font-weight: 700;">❌ "${u.original}"</div>
              <div style="color: var(--color-mint); font-size: 0.88rem; font-weight: 900; margin-top: 2px;">✅ "${u.upgrade}"</div>
              <div style="font-size: 0.74rem; color: var(--text-muted); font-weight: 700; margin-top: 4px;">💡 ${u.why}</div>
            </div>
          `).join('');
        }

        document.getElementById('talkReportOverlay').classList.add('active');
      }"""

content, count = re.subn(old_talk_methods_pattern, lambda m: new_talk_methods, content, count=1)
print(f"[Talk Engine] Replaced renderStep, chooseOption, & showReport: {count}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"File updated! Initial len: {initial_len}, New len: {len(content)}")
