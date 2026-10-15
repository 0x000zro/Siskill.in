/**
 * SISKILL Core Application Engine (v3.0 Production)
 * Super Intelligent Learning Skill
 */

window.masterCatalog = null;
window.currentSubjectBundle = null;
window.activeSubjectId = "CDP";
window.activeMicroId = null;
window.activeAssetType = "Concept";
window.activeTestTimer = null;

// ग्लोबल टाइमर क्लीनअप (मेमोरी लीक रोकने के लिए)
window.clearActiveTestTimer = function() {
  if (window.activeTestTimer) {
    clearInterval(window.activeTestTimer);
    window.activeTestTimer = null;
  }
};

document.addEventListener("DOMContentLoaded", async () => {
  registerServiceWorker();
  initNetworkMonitor();
  initSidebarToggle();
  initOfflinePreloader();
  await loadMasterCatalog();
  setupTabListeners();
  initGlobalSearch();
});

function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js")
      .then(() => console.log("[SW v3] Active"))
      .catch(err => console.error("[SW Error]:", err));
  }
}

function initNetworkMonitor() {
  const badge = document.getElementById("network-badge");
  const updateStatus = () => {
    if (!badge) return;
    if (navigator.onLine) {
      badge.textContent = "ऑनलाइन";
      badge.className = "badge-online";
    } else {
      badge.textContent = "ऑफ़लाइन मोड";
      badge.className = "badge-offline";
    }
  };
  window.addEventListener("online", updateStatus);
  window.addEventListener("offline", updateStatus);
  updateStatus();
}

function initSidebarToggle() {
  const toggleBtn = document.getElementById("btn-toggle-sidebar");
  const appBody = document.getElementById("app-body");
  if (toggleBtn && appBody) {
    toggleBtn.addEventListener("click", () => {
      appBody.classList.toggle("sidebar-collapsed");
    });
  }
}

// सभी 6 विषयों के बंडलों को एक क्लिक में ऑफ़लाइन कैश करना
function initOfflinePreloader() {
  const btn = document.getElementById("btn-offline-all");
  if (!btn) return;
  btn.onclick = async () => {
    if (!window.masterCatalog) return;
    btn.disabled = true;
    btn.textContent = "⏳ सेव हो रहा है...";
    try {
      for (const sub of window.masterCatalog.subjects) {
        await fetch(`dist_assets/bundle_${sub.id}.json`);
      }
      btn.textContent = "✅ 100% ऑफ़लाइन तैयार";
    } catch (e) {
      btn.textContent = "⚠️ नेटवर्क त्रुटि";
      btn.disabled = false;
    }
  };
}

// 1. मास्टर कैटलॉग लोड करना
async function loadMasterCatalog() {
  try {
    const res = await fetch("dist_assets/master_catalog.json");
    window.masterCatalog = await res.json();
    renderSubjectPills();
    await selectSubject(window.activeSubjectId);
  } catch (err) {
    console.error("कैटलॉग लोड विफल:", err);
  }
}

// 2. विषय सेलेक्टर पिल्स
function renderSubjectPills() {
  const container = document.getElementById("subject-selector");
  if (!container || !window.masterCatalog) return;
  container.innerHTML = "";

  window.masterCatalog.subjects.forEach(sub => {
    const btn = document.createElement("button");
    btn.className = `subj-btn ${sub.id === window.activeSubjectId ? 'active' : ''}`;
    btn.textContent = sub.id;
    btn.title = `${sub.name_hi} (${sub.total_questions || 0} Qs)`;
    btn.onclick = () => selectSubject(sub.id);
    container.appendChild(btn);
  });
}

// 3. विषय बंडल लोड करना
async function selectSubject(subId) {
  window.clearActiveTestTimer();
  window.activeSubjectId = subId;
  renderSubjectPills();

  const treeContainer = document.getElementById("tree-view");
  if (!treeContainer) return;
  treeContainer.innerHTML = "<p class='loading-text'>डेटा बंडल लोड हो रहा है...</p>";

  try {
    const res = await fetch(`dist_assets/bundle_${subId}.json`);
    window.currentSubjectBundle = await res.json();
    renderTree(subId);
  } catch (err) {
    treeContainer.innerHTML = "<p class='loading-text' style='color:#dc2626;'>बंडल लोड नहीं हो सका।</p>";
  }
}

// 4. 3-स्तरीय ट्री रेंडरर (स्वतः प्रथम माइक्रो-टॉपिक चयन सहित)
function renderTree(subId) {
  const subMeta = window.masterCatalog.subjects.find(s => s.id === subId);
  const container = document.getElementById("tree-view");
  if (!container || !subMeta) return;
  container.innerHTML = "";

  let firstMicroItem = null;

  subMeta.topics.forEach(topic => {
    const topicDiv = document.createElement("div");
    topicDiv.className = "tree-topic";

    const titleDiv = document.createElement("div");
    titleDiv.className = "topic-title";
    titleDiv.innerHTML = `<span>${topic.name_hi}</span> <span>▾</span>`;

    const subGroup = document.createElement("div");
    subGroup.className = "subtopic-group";

    titleDiv.onclick = () => subGroup.classList.toggle("hidden");
    topicDiv.appendChild(titleDiv);

    topic.subtopics.forEach(st => {
      const stWrap = document.createElement("div");
      stWrap.className = "subtopic-block";

      const stTitle = document.createElement("div");
      stTitle.className = "subtopic-title";
      stTitle.textContent = st.name_hi;
      stWrap.appendChild(stTitle);

      const mList = document.createElement("ul");
      mList.className = "micro-list";

      st.micro_topics.forEach(m => {
        const mItem = document.createElement("li");
        mItem.className = `micro-item ${m.id === window.activeMicroId ? 'active' : ''}`;
        mItem.dataset.search = `${m.name_hi} ${m.name_en || ''} ${m.id}`.toLowerCase();
        mItem.innerHTML = `
          <span>${m.name_hi}</span>
          <span class="badge-count">${(m.pyq_count || 0) + (m.mcq_count || 0)} Q</span>
        `;
        mItem.onclick = (e) => loadMicroContent(m.id, topic.name_hi, st.name_hi, m.name_hi, e.currentTarget);
        mList.appendChild(mItem);

        if (!firstMicroItem) {
          firstMicroItem = { id: m.id, t: topic.name_hi, st: st.name_hi, m: m.name_hi, el: mItem };
        }
      });

      stWrap.appendChild(mList);
      subGroup.appendChild(stWrap);
    });

    topicDiv.appendChild(subGroup);
    container.appendChild(topicDiv);
  });

  // विषय बदलते ही पहला माइक्रो-टॉपिक स्वतः खोलें
  if (firstMicroItem) {
    loadMicroContent(firstMicroItem.id, firstMicroItem.t, firstMicroItem.st, firstMicroItem.m, firstMicroItem.el, true);
  }
}

// 5. चयनित माइक्रो-टॉपिक लोड करना
function loadMicroContent(microId, tName, stName, mName, targetEl, isAutoLoad = false) {
  window.clearActiveTestTimer();
  window.activeMicroId = microId;

  const headerWrapper = document.getElementById("study-header-wrapper");
  if (headerWrapper) headerWrapper.classList.remove("hidden");

  const bc = document.getElementById("breadcrumb");
  const titleEl = document.getElementById("active-micro-title");
  const subTitleEl = document.getElementById("active-micro-subtitle");

  if (bc) bc.textContent = `${window.activeSubjectId} > ${tName} > ${stName}`;
  if (titleEl) titleEl.textContent = mName;
  if (subTitleEl) subTitleEl.textContent = `माइक्रो-टॉपिक कोड: ${microId}`;

  document.querySelectorAll(".micro-item").forEach(el => el.classList.remove("active"));
  if (targetEl) targetEl.classList.add("active");

  if (!isAutoLoad && window.innerWidth <= 768) {
    document.getElementById("app-body").classList.add("sidebar-collapsed");
  }

  renderActiveAsset();
}

// 6. मल्टी-एसेट कार्ड रेंडरर (Concept, Short_Notes, PYQ, MCQ, Mock_Test)
window.renderActiveAsset = function() {
  window.clearActiveTestTimer();
  const display = document.getElementById("asset-display");
  if (!display) return;

  const headerWrapper = document.getElementById("study-header-wrapper");
  if (headerWrapper) headerWrapper.classList.remove("hidden");

  if (!window.activeMicroId || !window.currentSubjectBundle) {
    display.innerHTML = `<div class="empty-state"><p>बायें पैनल से कोई माइक्रो-टॉपिक चुनें।</p></div>`;
    return;
  }

  const microAssets = window.currentSubjectBundle.micro_topics[window.activeMicroId] || {};
  const data = microAssets[window.activeAssetType];

  // A. Concept: समृद्ध कार्ड रीडर (ASCII डायग्राम व सब-लिस्ट सपोर्ट सहित)
  if (window.activeAssetType === "Concept") {
    if (!data) {
      display.innerHTML = `<div class="empty-state"><p>इस माइक्रो-टॉपिक के लिए अवधारणा सामग्री तैयार की जा रही है।</p></div>`;
      return;
    }

    let html = `
      <div class="content-card" style="border-left: 6px solid var(--primary);">
        <h2 class="font-handwriting">${data.title || 'मुख्य अवधारणा'}</h2>
        ${data.subtitle ? `<p style="color:var(--text-muted);">${data.subtitle}</p>` : ''}
      </div>
    `;

    if (data.sections && data.sections.length > 0) {
      data.sections.forEach(sec => {
        html += `<div class="content-card"><h3>${sec.heading || ''}</h3>`;
        if (sec.content) {
          html += `<div>${formatRichText(sec.content)}</div>`;
        }
        if (sec.points && Array.isArray(sec.points)) {
          html += `<ul class="notes-bullet-list">${sec.points.map(p => `<li>${p}</li>`).join("")}</ul>`;
        }
        if (sec.definitions && Array.isArray(sec.definitions)) {
          html += sec.definitions.map(d => `
            <div style="background:#f8fafc; padding:1rem; border-left:4px solid var(--primary-light); margin-bottom:0.85rem; border-radius:6px;">
              <strong>${d.scholar}:</strong> "${d.statement}"<br>
              <small style="color:var(--text-muted);"><strong>सार:</strong> ${d.core_essence || ''}</small>
            </div>
          `).join("");
        }
        if (sec.principles && Array.isArray(sec.principles)) {
          html += `<ul class="notes-bullet-list">${sec.principles.map(p => `<li><strong>${p.name}:</strong>${p.rule}</li>`).join("")}</ul>`;
        }
        html += `</div>`;
      });
    } else if (data.content) {
      html += `<div class="content-card"><div>${formatRichText(data.content)}</div></div>`;
    }
    display.innerHTML = html;
  }

  // B. Short Notes: बुलेट पॉइंट रिवीजन
  else if (window.activeAssetType === "Short_Notes") {
    if (!data || !data.bullet_points || data.bullet_points.length === 0) {
      display.innerHTML = `<div class="empty-state"><p>शॉर्ट नोट्स उपलब्ध नहीं हैं।</p></div>`;
      return;
    }
    const bullets = data.bullet_points.map(pt => `<li>${pt}</li>`).join("");
    display.innerHTML = `
      <div class="content-card">
        <h2 class="font-handwriting">${data.title || 'संक्षिप्त रिवीजन नोट्स'}</h2>
        <ul class="notes-bullet-list">${bullets}</ul>
      </div>
    `;
  }

  // C. PYQ एवं MCQ: इंटरएक्टिव हिडन-आंसर मोड
  else if (window.activeAssetType === "MCQ" || window.activeAssetType === "PYQ") {
    if (!data || !data.questions || data.questions.length === 0) {
      display.innerHTML = `<div class="empty-state"><p>${window.activeAssetType} प्रश्न उपलब्ध नहीं हैं।</p></div>`;
      return;
    }

    let qHtml = "";
    data.questions.forEach((q, idx) => {
      const qKey = `q_${idx}`;
      const cleanAns = String(q.correct_answer || "").replace(/[()]/g, "").trim().toUpperCase();
      qHtml += `
        <div class="practice-card" id="card-${qKey}">
          <div class="practice-q">प्र. ${idx + 1}: ${q.question}</div>
          <div class="practice-opts" id="opts-${qKey}">
            ${Object.entries(q.options || {}).map(([optKey, optVal]) => {
              const cleanOpt = String(optKey).replace(/[()]/g, "").trim().toUpperCase();
              return `
                <button class="opt-btn" data-opt="${cleanOpt}" onclick="handleOptionSelect('${qKey}', '${cleanOpt}', '${cleanAns}')">
                  <strong>(${cleanOpt})</strong> <span>${optVal}</span>
                </button>
              `;
            }).join("")}
          </div>
          <div class="practice-exp hidden" id="exp-${qKey}">
            <div style="font-weight:800; font-size:1.2rem; margin-bottom: 0.5rem;" id="verdict-${qKey}"></div>
            <div style="white-space: pre-line;"><strong>विस्तृत व्याख्या:</strong>\n${q.detailed_explanation || 'व्याख्या उपलब्ध नहीं है।'}</div>
          </div>
        </div>
      `;
    });
    display.innerHTML = qHtml;
  }

  // D. Mock Test लॉन्चर
  else if (window.activeAssetType === "Mock_Test") {
    if (window.renderMockTestLauncher) {
      window.renderMockTestLauncher(display, microAssets, window.activeMicroId);
    }
  }
};

// 7. विकल्प चयन हैंडलर (चयन के बाद ही उत्तर और व्याख्या दिखाएगा)
window.handleOptionSelect = function(qKey, selectedKey, correctKey) {
  const optsContainer = document.getElementById(`opts-${qKey}`);
  const expBox = document.getElementById(`exp-${qKey}`);
  const verdictBox = document.getElementById(`verdict-${qKey}`);
  if (!optsContainer || !expBox) return;

  const buttons = optsContainer.querySelectorAll(".opt-btn");
  buttons.forEach(btn => {
    btn.disabled = true;
    const optLabel = btn.dataset.opt;
    if (optLabel === correctKey) {
      btn.classList.add("correct-opt");
    } else if (optLabel === selectedKey) {
      btn.classList.add("wrong-opt");
    }
  });

  if (selectedKey === correctKey) {
    verdictBox.innerHTML = `✅ <span style="color:#16a34a;">बिल्कुल सही उत्तर! (विकल्प ${correctKey})</span>`;
    expBox.classList.remove("wrong-exp");
  } else {
    verdictBox.innerHTML = `❌ <span style="color:#dc2626;">गलत उत्तर! सही उत्तर विकल्प (${correctKey}) है।</span>`;
    expBox.classList.add("wrong-exp");
  }

  expBox.classList.remove("hidden");
};

// 8. ASCII डायग्राम और पैराग्राफ फ़ॉर्मेटर
function formatRichText(text) {
  if (!text) return "";
  const blocks = text.split("\n\n");
  return blocks.map(block => {
    if (/[┌┐└┘├┤┬┴┼─│╭╮╯╰]/.test(block)) {
      return `<pre class="ascii-diagram">${block}</pre>`;
    }
    return `<p style="margin-bottom:0.85rem;">${block.replace(/\n/g, "<br>")}</p>`;
  }).join("");
}

function setupTabListeners() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.onclick = (e) => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      e.currentTarget.classList.add("active");
      window.activeAssetType = e.currentTarget.dataset.asset;
      window.renderActiveAsset();
    };
  });
}

// 9. स्मार्ट ग्लोबल सर्च (टॉपिक, सब-टॉपिक व माइक्रो-टॉपिक फ़िल्टर)
function initGlobalSearch() {
  const searchInput = document.getElementById("global-search");
  if (!searchInput) return;

  searchInput.addEventListener("input", (e) => {
    const term = e.target.value.trim().toLowerCase();

    document.querySelectorAll(".tree-topic").forEach(topicEl => {
      let topicHasMatch = false;
      const subGroup = topicEl.querySelector(".subtopic-group");

      topicEl.querySelectorAll(".subtopic-block").forEach(stBlock => {
        let stHasMatch = false;
        stBlock.querySelectorAll(".micro-item").forEach(mItem => {
          const haystack = mItem.dataset.search || mItem.textContent.toLowerCase();
          if (!term || haystack.includes(term)) {
            mItem.style.display = "flex";
            stHasMatch = true;
            topicHasMatch = true;
          } else {
            mItem.style.display = "none";
          }
        });
        stBlock.style.display = stHasMatch ? "block" : "none";
      });

      topicEl.style.display = topicHasMatch ? "block" : "none";
      if (term && topicHasMatch && subGroup) {
        subGroup.classList.remove("hidden");
      }
    });
  });
}


// प्रश्न टेक्स्ट (Markdown Table व कथन-कारण) और व्याख्या फ़ॉर्मेटर
window.formatQuestionBody = function(qText) {
  if (!qText) return "";
  const lines = qText.split("\n");
  let html = "";
  let inTable = false;

  lines.forEach(line => {
    const t = line.trim();
    if (t.startsWith("|") && t.endsWith("|")) {
      if (/^\|[\s\-:|]+\|$/.test(t)) return; // Skip separator row |---|---|
      if (!inTable) {
        html += `<table style="width:100%; border-collapse:collapse; margin:0.75rem 0; font-size:1.05rem;">`;
        inTable = true;
      }
      const cells = t.slice(1, -1).split("|").map(c => c.trim());
      html += `<tr>${cells.map(c => `<td style="border:1px solid var(--border); padding:0.5rem 0.75rem; background:#f8fafc;">${c}</td>`).join("")}</tr>`;
    } else {
      if (inTable) {
        html += `</table>`;
        inTable = false;
      }
      html += `<div style="margin-bottom:0.35rem;">${t}</div>`;
    }
  });
  if (inTable) html += `</table>`;
  return html;
};
