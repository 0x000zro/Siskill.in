/**
 * SISKILL Mock Test & Diagnostic Engine (script.js v3.0)
 * Supports:
 *  1. 30Q Micro-Topic Mock Test (70:30 Smart Fill)
 *  2. 30Q Full-Subject Mock Test
 *  3. 150Q 5-Subject Full Exam CBT Simulator + OMR Palette + Answer Key
 */

document.addEventListener("DOMContentLoaded", () => {
  const top150Btn = document.getElementById("btn-top-150-mock");
  if (top150Btn) top150Btn.onclick = () => render150MockModal();

  const sub30Btn = document.getElementById("btn-subject-30-mock");
  if (sub30Btn) sub30Btn.onclick = () => startSubject30Mock();
});

// Fisher-Yates Unbiased Random Shuffle
function shuffleArray(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

// 70:30 स्मार्ट प्रश्न चयनकर्ता (यदि PYQ कम हों तो MCQ से 30 पूरे करेगा, और इसके विपरीत)
function select7030Questions(pyqList, mcqList, totalTarget = 30) {
  const sPYQ = shuffleArray(pyqList);
  const sMCQ = shuffleArray(mcqList);

  const idealPYQ = Math.round(totalTarget * 0.7); // 21
  let pickedPYQ = sPYQ.slice(0, idealPYQ);
  let remainingNeeded = totalTarget - pickedPYQ.length;
  let pickedMCQ = sMCQ.slice(0, remainingNeeded);

  // यदि MCQ कम पड़ें और हमारे पास अतिरिक्त PYQ बचे हों, तो उनसे 30 पूरे करें
  if (pickedPYQ.length + pickedMCQ.length < totalTarget && sPYQ.length > pickedPYQ.length) {
    const extraNeeded = totalTarget - (pickedPYQ.length + pickedMCQ.length);
    pickedPYQ.push(...sPYQ.slice(pickedPYQ.length, pickedPYQ.length + extraNeeded));
  }

  return shuffleArray([...pickedPYQ, ...pickedMCQ]);
}

// 1. माइक्रो-टॉपिक 30Q टेस्ट लॉन्चर
window.renderMockTestLauncher = function(container, microAssets, microId) {
  window.clearActiveTestTimer();
  const mcqs = microAssets["MCQ"] ? microAssets["MCQ"].questions || [] : [];
  const pyqs = microAssets["PYQ"] ? microAssets["PYQ"].questions || [] : [];
  const totalAvailable = mcqs.length + pyqs.length;

  container.innerHTML = `
    <div class="content-card" style="text-align: center; padding: 2.5rem 1.5rem;">
      <h2 class="font-handwriting" style="font-size: 2rem; color: var(--primary);">⏱️ 30Q माइक्रो-टॉपिक मॉक टेस्ट</h2>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin: 0.75rem 0 1.25rem;">
        उपलब्ध प्रश्न पूल: <strong>${pyqs.length} PYQs</strong> | <strong>${mcqs.length} MCQs</strong> (कुल: ${totalAvailable})
      </p>
      <div style="background: #eff6ff; padding: 1.25rem; border-radius: 10px; display: inline-block; text-align: left; margin-bottom: 1.75rem; font-size: 1.05rem;">
        <div>• <strong>चयन अनुपात:</strong> 70% PYQ + 30% MCQ (स्मार्ट ऑटो-फिल)</div>
        <div>• <strong>अधिकतम प्रश्न:</strong> ${Math.min(30, totalAvailable)} प्रश्न | <strong>समय:</strong> 30 मिनट</div>
        <div>• <strong>विशेषता:</strong> लाइव OMR पैलेट एवं सबमिट करने पर विस्तृत व्याख्या</div>
      </div>
      <div>
        <button id="btn-start-micro-test" style="
          background: var(--primary); color: white; padding: 0.9rem 2.25rem;
          font-size: 1.2rem; font-weight: 800; border: none; border-radius: 30px; cursor: pointer;">
          टॉपिक टेस्ट शुरू करें 🚀
        </button>
      </div>
    </div>
  `;

  document.getElementById("btn-start-micro-test").onclick = () => {
    const selected = select7030Questions(pyqs, mcqs, 30);
    if (selected.length === 0) {
      alert("इस माइक्रो-टॉपिक में अभी प्रश्न उपलब्ध नहीं हैं।");
      return;
    }
    const formatted = selected.map((q, idx) => ({
      ...q,
      global_q_num: idx + 1,
      section_id: window.activeSubjectId,
      section_name: `टॉपिक: ${microId}`
    }));
    runUnifiedCBTPlayer(formatted, [{ id: window.activeSubjectId, name: `टॉपिक: ${microId}` }], 30);
  };
};

// 2. संपूर्ण विषय (Subject-Wise) 30Q टेस्ट
function startSubject30Mock() {
  if (!window.currentSubjectBundle) return;
  let pyqPool = [];
  let mcqPool = [];

  Object.values(window.currentSubjectBundle.micro_topics || {}).forEach(assets => {
    if (assets.PYQ && assets.PYQ.questions) pyqPool.push(...assets.PYQ.questions);
    if (assets.MCQ && assets.MCQ.questions) mcqPool.push(...assets.MCQ.questions);
  });

  const selected = select7030Questions(pyqPool, mcqPool, 30);
  if (selected.length === 0) {
    alert("इस विषय में अभी कोई प्रश्न उपलब्ध नहीं हैं।");
    return;
  }

  const subName = window.currentSubjectBundle.name_hi || window.activeSubjectId;
  const formatted = selected.map((q, idx) => ({
    ...q,
    global_q_num: idx + 1,
    section_id: window.activeSubjectId,
    section_name: subName
  }));

  runUnifiedCBTPlayer(formatted, [{ id: window.activeSubjectId, name: subName }], 30);
}

// 3. 150Q महा-मॉक टेस्ट कॉन्फ़िगरेशन स्क्रीन
function render150MockModal() {
  window.clearActiveTestTimer();
  const headerWrapper = document.getElementById("study-header-wrapper");
  if (headerWrapper) headerWrapper.classList.add("hidden");

  const mount = document.getElementById("asset-display");
  mount.innerHTML = `
    <div class="content-card" style="text-align: center; max-width: 820px; margin: 0 auto; padding: 2.5rem;">
      <h2 class="font-handwriting" style="font-size: 2.3rem; color: var(--primary); margin-bottom: 0.5rem;">
        🎯 CTET / UPTET 150Q महा-मॉक टेस्ट
      </h2>
      <p style="color: var(--text-muted); font-size: 1.15rem; margin-bottom: 1.5rem;">
        संपूर्ण 5 विषयों के प्रश्न बैंक से 70:30 अनुपात में संकलित फुल-लेंथ सीबीटी (CBT) परीक्षा
      </p>

      <div style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 12px; padding: 1.5rem; text-align: left; margin-bottom: 1.75rem;">
        <h4 style="color: var(--primary); font-size: 1.25rem; margin-bottom: 0.75rem;">📋 परीक्षा संरचना (5 खंड × 30 प्रश्न = 150 प्रश्न):</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; font-size: 1.1rem;">
          <div>1. बाल विकास (CDP): <strong>30 प्रश्न</strong></div>
          <div>2. हिन्दी भाषा (Language I): <strong>30 प्रश्न</strong></div>
          <div>3. गणित (Mathematics): <strong>30 प्रश्न</strong></div>
          <div>4. पर्यावरण अध्ययन (EVS): <strong>30 प्रश्न</strong></div>
          <div>5. द्वितीय भाषा (Language II): <strong>30 प्रश्न</strong></div>
        </div>
        <div style="margin-top: 1rem; border-top: 1px dashed #93c5fd; padding-top: 0.75rem; font-size: 1rem;">
          ⏱️ <strong>निर्धारित समय:</strong> 150 मिनट (2 घंटा 30 मिनट) | <strong>अंकन:</strong> +1 प्रति सही उत्तर (कोई नेगेटिव मार्किंग नहीं)
        </div>
      </div>

      <div style="margin-bottom: 2rem;">
        <label style="font-size: 1.2rem; font-weight: 700; margin-right: 0.75rem;">द्वितीय भाषा (Language II) चुनें:</label>
        <select id="select-lang2" style="font-size: 1.15rem; padding: 0.6rem 1.2rem; border-radius: 8px; border: 2px solid var(--primary); font-weight: 700;">
          <option value="ENG">अंग्रेजी भाषा (English)</option>
          <option value="SAN">संस्कृत भाषा (Sanskrit)</option>
        </select>
      </div>

      <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
        <button onclick="window.renderActiveAsset()" class="opt-btn" style="width:auto; padding:0.85rem 1.75rem;">← वापस लौटें</button>
        <button id="btn-launch-150-now" style="
          background: #16a34a; color: white; font-size: 1.25rem; font-weight: 800;
          padding: 0.85rem 2.5rem; border: none; border-radius: 30px; cursor: pointer;">
          150Q परीक्षा प्रारंभ करें 🚀
        </button>
      </div>
    </div>
  `;

  document.getElementById("btn-launch-150-now").onclick = () => {
    const lang2 = document.getElementById("select-lang2").value;
    buildAndStart150Mock(lang2);
  };
}

// 4. 5 विषयों के बंडलों से 150 प्रश्न संकलित करना
async function buildAndStart150Mock(lang2) {
  const mount = document.getElementById("asset-display");
  mount.innerHTML = `<div class="empty-state"><p class="font-handwriting" style="font-size: 1.8rem;">पांचों विषयों के प्रश्न बंडल संकलित किए जा रहे हैं... ⏳</p></div>`;

  const sectionsConfig = [
    { id: "CDP", name: "बाल विकास (CDP)", file: "dist_assets/bundle_CDP.json" },
    { id: "HINDI", name: "हिन्दी भाषा", file: "dist_assets/bundle_HINDI.json" },
    { id: "MATH", name: "गणित", file: "dist_assets/bundle_MATH.json" },
    { id: "EVS", name: "पर्यावरण (EVS)", file: "dist_assets/bundle_EVS.json" },
    { id: lang2, name: lang2 === "ENG" ? "अंग्रेजी भाषा" : "संस्कृत भाषा", file: `dist_assets/bundle_${lang2}.json` }
  ];

  let fullExamQuestions = [];
  let globalQNum = 1;

  for (const sec of sectionsConfig) {
    let pyqPool = [];
    let mcqPool = [];
    try {
      const res = await fetch(sec.file);
      const bundle = await res.json();
      Object.values(bundle.micro_topics || {}).forEach(assets => {
        if (assets.PYQ && assets.PYQ.questions) pyqPool.push(...assets.PYQ.questions);
        if (assets.MCQ && assets.MCQ.questions) mcqPool.push(...assets.MCQ.questions);
      });
    } catch (e) {
      console.warn(`बंडल लोड त्रुटि: ${sec.file}`, e);
    }

    const secSelected = select7030Questions(pyqPool, mcqPool, 30);
    secSelected.forEach(q => {
      fullExamQuestions.push({
        ...q,
        global_q_num: globalQNum++,
        section_id: sec.id,
        section_name: sec.name
      });
    });
  }

  if (fullExamQuestions.length === 0) {
    alert("प्रश्न बैंक में अभी कोई प्रश्न उपलब्ध नहीं हैं।");
    window.renderActiveAsset();
    return;
  }

  const activeSections = sectionsConfig.filter(s => fullExamQuestions.some(q => q.section_id === s.id));
  runUnifiedCBTPlayer(fullExamQuestions, activeSections, 150);
}

// 5. यूनिफाइड सीबीटी प्लेयर (30Q एवं 150Q दोनों के लिए OMR पैलेट + रिजल्ट सॉल्यूशंस)
function runUnifiedCBTPlayer(questions, sectionsConfig, durationMinutes) {
  window.clearActiveTestTimer();
  let currentIndex = 0;
  let userResponses = {}; // { global_q_num: cleanOptKey }
  let timeLeft = durationMinutes * 60;

  const mount = document.getElementById("asset-display");

  mount.innerHTML = `
    <div style="background: white; border: 2px solid var(--primary); border-radius: 12px; padding: 1.5rem;">
      <!-- टॉप बार -->
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 0.85rem; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
        <div>
          <span style="font-weight: 800; font-size: 1.35rem; color: var(--primary);" id="cbt-sec-title"></span>
          <div style="font-size: 1rem; color: var(--text-muted);" id="cbt-counter"></div>
        </div>
        <div style="display:flex; align-items:center; gap:0.75rem;">
          <div style="background: #0f172a; color: #fde047; padding: 0.45rem 1.15rem; border-radius: 8px; font-weight: 800; font-size: 1.3rem;" id="cbt-timer">
            00:00:00
          </div>
          <button id="btn-cbt-exit" style="background:#f1f5f9; border:1px solid var(--border); padding:0.5rem 0.9rem; border-radius:6px; font-weight:700; cursor:pointer;">✕ छोड़ें</button>
        </div>
      </div>

      <!-- सेक्शन टैब्स -->
      <div class="section-nav-bar ${sectionsConfig.length <= 1 ? 'hidden' : ''}" id="cbt-section-bar"></div>

      <!-- OMR प्रश्न संख्या पैलेट -->
      <div class="omr-palette-bar" id="cbt-omr-palette"></div>

      <!-- प्रश्न क्षेत्र -->
      <div id="cbt-question-body" style="min-height: 250px;"></div>

      <!-- बॉटम कंट्रोल्स -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.75rem; border-top: 2px solid var(--border); padding-top: 1.15rem; flex-wrap: wrap; gap: 0.75rem;">
        <button id="btn-cbt-prev" class="opt-btn" style="width: auto; padding: 0.7rem 1.5rem;">← पिछला</button>
        <button id="btn-cbt-submit" style="background: #dc2626; color: white; border: none; padding: 0.8rem 2rem; border-radius: 8px; font-weight: 800; font-size: 1.1rem; cursor: pointer;">
          टेस्ट सबमिट करें 🏁
        </button>
        <button id="btn-cbt-next" class="opt-btn" style="width: auto; padding: 0.7rem 1.5rem; background: var(--primary); color: white;">अगला →</button>
      </div>
    </div>
  `;

  // सेक्शन टैब्स बनाना
  const secBar = document.getElementById("cbt-section-bar");
  sectionsConfig.forEach(s => {
    const btn = document.createElement("button");
    btn.className = "sec-tab-btn";
    btn.textContent = s.name;
    btn.id = `cbt-sec-tab-${s.id}`;
    btn.onclick = () => {
      const idx = questions.findIndex(q => q.section_id === s.id);
      if (idx !== -1) { currentIndex = idx; renderCBTState(); }
    };
    secBar.appendChild(btn);
  });

  // ग्लोबल टाइमर शुरू करना
  const updateClock = () => {
    const h = Math.floor(timeLeft / 3600);
    const m = Math.floor((timeLeft % 3600) / 60);
    const s = timeLeft % 60;
    const tEl = document.getElementById("cbt-timer");
    if (tEl) {
      tEl.textContent = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    }
  };
  updateClock();

  window.activeTestTimer = setInterval(() => {
    timeLeft--;
    updateClock();
    if (timeLeft <= 0) {
      window.clearActiveTestTimer();
      finishCBTExam();
    }
  }, 1000);

  function renderCBTState() {
    const q = questions[currentIndex];
    document.getElementById("cbt-sec-title").textContent = q.section_name;
    document.getElementById("cbt-counter").textContent = `प्रश्न ${q.global_q_num} / ${questions.length} (उत्तरित: ${Object.keys(userResponses).length})`;

    document.querySelectorAll(".sec-tab-btn").forEach(b => b.classList.remove("active"));
    const activeTab = document.getElementById(`cbt-sec-tab-${q.section_id}`);
    if (activeTab) activeTab.classList.add("active");

    // OMR पैलेट रेंडर
    const paletteEl = document.getElementById("cbt-omr-palette");
    paletteEl.innerHTML = "";
    questions.forEach((item, idx) => {
      const dot = document.createElement("button");
      const isAns = userResponses[item.global_q_num] !== undefined;
      dot.className = `omr-dot ${idx === currentIndex ? 'active-q' : ''} ${isAns ? 'answered-q' : ''}`;
      dot.textContent = item.global_q_num;
      dot.onclick = () => { currentIndex = idx; renderCBTState(); };
      paletteEl.appendChild(dot);
    });

    // प्रश्न व विकल्प रेंडर
    const chosen = userResponses[q.global_q_num];
    const bodyEl = document.getElementById("cbt-question-body");
    bodyEl.innerHTML = `
      <div style="font-size: 1.35rem; font-weight: 700; margin-bottom: 1.25rem; line-height: 1.65;">
        प्र. ${q.global_q_num}: ${q.question}
      </div>
      <div style="display: flex; flex-direction: column; gap: 0.85rem;">
        ${Object.entries(q.options || {}).map(([k, v]) => {
          const cleanK = String(k).replace(/[()]/g, "").trim().toUpperCase();
          return `
            <button class="opt-btn ${chosen === cleanK ? 'correct-opt' : ''}" onclick="selectCBTOption(${q.global_q_num}, '${cleanK}')">
              <strong>(${cleanK})</strong> <span>${v}</span>
            </button>
          `;
        }).join("")}
      </div>
    `;

    document.getElementById("btn-cbt-prev").disabled = currentIndex === 0;
    document.getElementById("btn-cbt-next").textContent = currentIndex === questions.length - 1 ? "प्रथम प्रश्न पर जाएं" : "अगला →";
  }

  window.selectCBTOption = function(qNum, key) {
    userResponses[qNum] = key;
    renderCBTState();
  };

  document.getElementById("btn-cbt-prev").onclick = () => {
    if (currentIndex > 0) { currentIndex--; renderCBTState(); }
  };
  document.getElementById("btn-cbt-next").onclick = () => {
    if (currentIndex < questions.length - 1) { currentIndex++; renderCBTState(); }
    else { currentIndex = 0; renderCBTState(); }
  };
  document.getElementById("btn-cbt-exit").onclick = () => {
    if (confirm("क्या आप टेस्ट छोड़कर अध्ययन स्क्रीन पर वापस जाना चाहते हैं?")) {
      window.renderActiveAsset();
    }
  };
  document.getElementById("btn-cbt-submit").onclick = () => {
    if (confirm(`आपने ${questions.length} में से ${Object.keys(userResponses).length} प्रश्नों के उत्तर दिए हैं। क्या टेस्ट सबमिट करें?`)) {
      finishCBTExam();
    }
  };

  function finishCBTExam() {
    window.clearActiveTestTimer();

    let totalCorrect = 0;
    let totalWrong = 0;
    let totalSkipped = 0;
    let sectionStats = {};

    sectionsConfig.forEach(s => {
      sectionStats[s.id] = { name: s.name, correct: 0, wrong: 0, skipped: 0, total: 0 };
    });

    questions.forEach(q => {
      const resp = userResponses[q.global_q_num];
      const ans = String(q.correct_answer || "").replace(/[()]/g, "").trim().toUpperCase();
      const st = sectionStats[q.section_id];
      if (st) st.total++;

      if (!resp) {
        totalSkipped++;
        if (st) st.skipped++;
      } else if (resp === ans) {
        totalCorrect++;
        if (st) st.correct++;
      } else {
        totalWrong++;
        if (st) st.wrong++;
      }
    });

    const pct = ((totalCorrect / questions.length) * 100).toFixed(1);

    const solutionsHtml = questions.map(q => {
      const resp = userResponses[q.global_q_num];
      const ans = String(q.correct_answer || "").replace(/[()]/g, "").trim().toUpperCase();
      const isRight = resp === ans;
      return `
        <div class="practice-card" style="text-align:left;">
          <div class="practice-q">प्र. ${q.global_q_num} [${q.section_name}]: ${q.question}</div>
          <p style="margin-bottom:0.4rem;">
            <strong>आपका उत्तर:</strong>
            <span style="color:${!resp ? '#64748b' : (isRight ? '#16a34a' : '#dc2626')}; font-weight:700;">
              ${resp ? `(${resp})${q.options[resp] || ''}` : 'छोड़ा गया (Unattempted)'}
            </span>
          </p>
          <p style="margin-bottom:0.75rem; color:#16a34a; font-weight:700;">
            ✔ सही उत्तर: (${ans}) ${q.options[ans] || ''}
          </p>
          <div class="practice-exp">
            <strong>व्याख्या:</strong> ${q.detailed_explanation || 'व्याख्या उपलब्ध नहीं है।'}
          </div>
        </div>
      `;
    }).join("");

    mount.innerHTML = `
      <div class="content-card" style="text-align: center; padding: 2.25rem;">
        <h2 class="font-handwriting" style="font-size: 2.3rem; color: var(--primary);">🏆 परीक्षा परिणाम एवं विस्तृत विश्लेषण</h2>

        <div style="display: flex; justify-content: center; gap: 1.25rem; flex-wrap: wrap; margin: 1.5rem 0;">
          <div style="background: #eff6ff; border: 2px solid var(--primary); padding: 1.25rem 2rem; border-radius: 12px;">
            <div style="font-size: 2.6rem; font-weight: 800; color: var(--primary);">${totalCorrect} / ${questions.length}</div>
            <div style="font-weight: 700; color: var(--text-muted);">कुल प्राप्तांक (${pct}%)</div>
          </div>
          <div style="background: #f0fdf4; border: 2px solid #16a34a; padding: 1.25rem 2rem; border-radius: 12px;">
            <div style="font-size: 2.6rem; font-weight: 800; color: #16a34a;">${totalCorrect}</div>
            <div style="font-weight: 700; color: #166534;">सही उत्तर</div>
          </div>
          <div style="background: #fef2f2; border: 2px solid #dc2626; padding: 1.25rem 2rem; border-radius: 12px;">
            <div style="font-size: 2.6rem; font-weight: 800; color: #dc2626;">${totalWrong}</div>
            <div style="font-weight: 700; color: #991b1b;">गलत उत्तर</div>
          </div>
          <div style="background: #f8fafc; border: 2px solid var(--border); padding: 1.25rem 2rem; border-radius: 12px;">
            <div style="font-size: 2.6rem; font-weight: 800; color: var(--text-muted);">${totalSkipped}</div>
            <div style="font-weight: 700; color: var(--text-muted);">छोड़े गए</div>
          </div>
        </div>

        <h3 style="text-align: left; margin: 1.5rem 0 1rem; color: var(--primary);">📊 खंड-वार प्रदर्शन (Section-Wise Diagnostics):</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; text-align: left; margin-bottom: 2rem;">
          ${Object.values(sectionStats).map(st => {
            const acc = st.total > 0 ? Math.round((st.correct / st.total) * 100) : 0;
            return `
              <div style="background: #f8fafc; border: 1.5px solid var(--border); padding: 1rem; border-radius: 10px;">
                <div style="font-weight: 700; font-size: 1.05rem;">${st.name}</div>
                <div style="font-size: 1.35rem; font-weight: 800; color: ${acc >= 60 ? '#16a34a' : '#dc2626'}; margin: 0.3rem 0;">
                  ${st.correct} / ${st.total} (${acc}%)
                </div>
                <small style="color:var(--text-muted);">सही: ${st.correct} | गलत: ${st.wrong} \vert{} छोड़े: ${st.skipped}</small>
              </div>
            `;
          }).join("")}
        </div>

        <button class="opt-btn" style="width: auto; margin: 0 auto; background: var(--primary); color: white; padding: 0.85rem 2.5rem; font-weight: 800;" onclick="window.renderActiveAsset()">
          📖 अध्ययन स्क्रीन पर वापस लौटें
        </button>
      </div>

      <h3 style="margin: 2rem 0 1rem; color: var(--primary); font-size: 1.5rem;">🔑 विस्तृत उत्तर कुंजी एवं व्याख्याएं:</h3>
      ${solutionsHtml}
    `;
  }

  renderCBTState();
}
