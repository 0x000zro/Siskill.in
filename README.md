# Siskill.in
टर्मिनल (~/Guru_G_SI_Skill) में सीधे README.md फ़ाइल जनरेट करने के लिए नीचे दी गई cat << 'EOF' कमांड चलाएँ:
cat << 'EOF' > README.md
# 📖 SISKILL — Super Intelligent Learning Skill

[![Platform](https://img.shields.io/badge/Platform-Offline--First%20PWA-1e3a8a?style=for-the-badge)](./index.html)
[![Taxonomy](https://img.shields.io/badge/Micro--Topics-765-10b981?style=for-the-badge)](./manifest.json)
[![Assets](https://img.shields.io/badge/Source%20Files-3,842-f59e0b?style=for-the-badge)](./dist_assets/master_catalog.json)
[![Engine](https://img.shields.io/badge/Automation-Python%203-2563eb?style=for-the-badge)](./tools/sync_engine.py)

> **"Super Intelligent Learning Skill"** — सीटीईटी (CTET) और यूपीटीईटी (UPTET) की तैयारी के लिए एक एंटरप्राइज-स्केल, **ऑफलाइन-फर्स्ट प्रोग्रेसिव वेब ऐप (PWA)** और स्वचालित कंटेंट पाइपलाइन।

---

## 🌟 मुख्य विशेषताएँ (Key Features)

1. **100% ऑफ़लाइन-फर्स्ट आर्किटेक्चर (Offline-First PWA):**
   * सर्विस वर्कर (`sw.js`) और स्मार्ट बंडल कैशिंग के माध्यम से एक बार लोड होने के बाद बिना इंटरनेट के भी संपूर्ण अध्ययन सामग्री और मॉक टेस्ट चलते हैं।
2. **3,842 फ़ाइलों का स्मार्ट संकलन (Zero-Lag Bundling):**
   * 1,215 डायरेक्टरीज़ और 3,842 सोर्स फ़ाइलों को क्लाइंट के लिए केवल **7 ऑप्टिमाइज़्ड डिस्ट्रिब्यूशन फ़ाइलों (`dist_assets/`)** में कंपाइल किया जाता है, जिससे मोबाइल ब्राउज़र पर ऐप 0.2 सेकंड में लोड होता है।
3. **5-इन-1 यूनिफाइड लर्निंग कंसोल:**
   * **📘 मुख्य अवधारणा (Concept):** अध्याय और सेक्शन-वार कार्ड रीडर।
   * **📝 संक्षिप्त नोट्स (Short Notes):** परीक्षा से पहले तेज़ रिवीजन के लिए बुलेट-पॉइंट नोट्स।
   * **🎯 विगत वर्ष प्रश्न (PYQ):** उत्तर चुनने के बाद ही सही/गलत प्रतिक्रिया और विस्तृत व्याख्या दिखाने वाला इंटरएक्टिव मोड।
   * **💡 अभ्यास प्रश्न (MCQ):** नवीन परीक्षा पैटर्न पर आधारित इंटरएक्टिव प्रश्नोत्तरी।
   * **⏱️ 30Q माइक्रो-टॉपिक टेस्ट:** प्रत्येक सूक्ष्म-बिंदु (Micro-topic) के लिए 30 मिनट का टाइमर आधारित टेस्ट।
4. **🏆 150Q महा-मॉक टेस्ट (Full Exam CBT Simulator):**
   * संपूर्ण परीक्षा पैटर्न (**70% PYQ + 30% MCQ**) पर आधारित 5 खंडों (CDP, हिन्दी, गणित, पर्यावरण, और द्वितीय भाषा: English/Sanskrit) का 150 मिनट का लाइव सीबीटी (CBT) टेस्ट और विषय-वार स्कोरकार्ड।
5. **उत्कृष्ट पठनीयता एवं हैंडराइटिंग UI:**
   * देवनागरी के लिए **'Kalam' (Handwriting)** एवं **'Noto Sans Devanagari'** फॉन्ट्स, बड़ा फॉन्ट साइज़ (`18px+`), और एक क्लिक में छिपने वाला **Collapsible Sidebar (`☰`)**।
6. **स्वचालित बैकग्राउंड सिंक इंजन (`sync_engine.py`):**
   * किसी भी माइक्रो-टॉपिक फ़ोल्डर में `.txt` फ़ाइल (`Concept.txt`, `Short_Notes.txt`, `MCQ.txt`, `PYQ.txt`) रखते ही इंजन उसे स्वतः पार्स करके `.json` में बदलता है, पुरानी फ़ाइल को आर्काइव करता है, और PWA बंडल अपडेट कर देता है।

---

## 📊 विषय-वार टैक्सोनॉमी पैमाना (Taxonomy Scale)

संपूर्ण पाठ्यक्रम को **3-स्तरीय पदानुक्रम (`Topic` → `Subtopic` → `Micro-topic`)** में द्विभाषी रूप में व्यवस्थित किया गया है:

| विषय कोड | विषय का नाम (Subject Name) | मुख्य अध्याय (Topics) | उप-अध्याय (Subtopics) | सूक्ष्म-बिंदु (Micro-topics) | डायरेक्टरी पथ |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **CDP** | बाल विकास एवं शिक्षाशास्त्र (Child Development) | 27 | 66 | 255 | `Child_Development_and_Pedagogy/` |
| **HINDI** | हिन्दी भाषा एवं शिक्षाशास्त्र (Hindi) | 18 | 42 | 88 | `Hindi/` |
| **MATH** | गणित एवं शिक्षाशास्त्र (Mathematics) | 24 | 51 | 105 | `Mathematics/` |
| **EVS** | पर्यावरण अध्ययन (Environmental Studies) | 24 | 52 | 115 | `Environmental_Studies/` |
| **ENG** | अंग्रेजी भाषा एवं शिक्षाशास्त्र (English) | 21 | 44 | 97 | `English/` |
| **SAN** | संस्कृत भाषा एवं शिक्षाशास्त्र (Sanskrit) | 22 | 50 | 105 | `Sanskrit/` |
| **कुल (Total)** | **6 विषय (Subjects)** | **136** | **305** | **765** | **1,215 फ़ोल्डर्स / 3,842 फ़ाइलें** |

---

## 🏗️ सिस्टम आर्किटेक्चर (System Architecture)

```text
[Raw Text Drop: Concept.txt / Short_Notes.txt / PYQ.txt / MCQ.txt]
                               │
                               ▼
              ┌─────────────────────────────────┐
              │   tools/sync_engine.py (Daemon) │
              │  • Parses .txt -> Sparse .json  │
              │  • Archives processed .txt      │
              └────────────────┬────────────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         ▼                                           ▼
┌─────────────────────────┐               ┌──────────────────────────┐
│  tools/index_tracker.py │               │  tools/build_catalog.py  │
│  Updates manifest.json  │               │  Builds dist_assets/     │
│  & 6 Subject Indexes    │               │  (1 Catalog + 6 Bundles) │
└─────────────────────────┘               └─────────────┬────────────┘
                                                        │
                                                        ▼
                                       ┌─────────────────────────────────┐
                                       │   SISKILL Offline-First PWA     │
                                       │  • Service Worker Cache (sw.js) │
                                       │  • Interactive Reader (app.js)  │
                                       │  • 30Q & 150Q CBT (script.js)   │
                                       └─────────────────────────────────┘

🚀 त्वरित शुरुआत (Quick Start Guide)
1. रिपॉजिटरी क्लोन करें
git clone <YOUR_REPO_URL> Guru_G_SI_Skill
cd Guru_G_SI_Skill

2. फ़ोल्डर ऑडिट एवं डिस्ट्रिब्यूशन बंडल तैयार करें
# सभी 765 माइक्रो-टॉपिक डायरेक्टरीज़ और इंडेक्स सत्यापित करें
python3 tools/scaffold_and_audit.py
python3 tools/index_tracker.py

# 3,842 फ़ाइलों को 7 क्लाइंट बंडलों (dist_assets/) में कंपाइल करें
python3 tools/build_catalog.py

3. बैकग्राउंड सिंक इंजन चालू करें
# लाइव टर्मिनल मोड में चलाने के लिए:
python3 tools/sync_engine.py

# या 24/7 बैकग्राउंड डेमन के रूप में चलाने के लिए:
nohup python3 tools/sync_engine.py > sync.log 2>&1 &

4. ऑफ़लाइन PWA वेब सर्वर शुरू करें
python3 -m http.server 8080

अपने ब्राउज़र में http://localhost:8080 खोलें। मोबाइल पर "Add to Home Screen" चुनकर इसे स्टैंडअलोन ऐप की तरह इंस्टॉल करें।
✍️ कंटेंट जोड़ने की मानक विधि (Content Ingestion Formats)
किसी भी माइक्रो-टॉपिक फ़ोल्डर में नीचे दिए गए प्रारूप में .txt फ़ाइल रखते ही sync_engine.py उसे 3 सेकंड के भीतर प्रोसेस कर देगा:
1. Concept.txt (मुख्य अवधारणा)
अध्याय: वृद्धि एवं विकास की अवधारणा
1. विषय का परिचय
वृद्धि का तात्पर्य शारीरिक परिवर्तनों से है जबकि विकास गुणात्मक व सर्वांगीण होता है।
2. मूल सिद्धांत
विकास सिर से पैर (मस्तकाधोमुखी) और केंद्र से बाहर (निकट-दूर) की ओर होता है।

2. Short_Notes.txt (संक्षिप्त नोट्स)
शीर्षक: वृद्धि एवं विकास - क्विक रिवीजन पॉइंट्स
• वृद्धि केवल मात्रात्मक है, विकास गुणात्मक व मात्रात्मक दोनों है।
• विकास का क्रम: D = H × E (वंशानुक्रम × वातावरण)।
• विकास रेखीय नहीं, वर्तुलाकार (Spiral) होता है।

3. MCQ.txt / PYQ.txt (प्रश्नोत्तरी)
(आपकी मानक प्रश्न-विकल्प-उत्तर-व्याख्या टेक्स्ट संरचना जिसे sync_engine.py स्वतः क्रमांकित करके मौजूदा JSON सूची में जोड़ देता है।)
📂 प्रोजेक्ट फ़ाइल संरचना (Directory Structure)
Guru_G_SI_Skill/
├── index.html                  # मुख्य PWA ऐप शेल (UI Layout)
├── style.css                   # रेस्पॉन्सिव स्टाइलिंग एवं Kalam हैंडराइटिंग फॉन्ट्स
├── app.js                      # कैटलॉग लोडर, साइडबार ट्री, ग्लोबल सर्च व कार्ड रीडर
├── script.js                   # 30Q माइक्रो-टेस्ट एवं 150Q फुल सीबीटी मॉक टेस्ट इंजन
├── sw.js                       # ऑफ़लाइन सर्विस वर्कर (Cache-First + Dynamic Bundle Sync)
├── manifest.webmanifest        # PWA इंस्टॉलेशन कॉन्फ़िगरेशन
├── manifest.json               # रूट डेटा मैनिफ़ेस्ट
├── blueprint.md                # विस्तृत इंजीनियरिंग ब्लूप्रिंट
├── README.md                   # प्रोजेक्ट दस्तावेज़ीकरण
├── dist_assets/                # कंपाइल किए गए 7 क्लाइंट JSON बंडल
│   ├── master_catalog.json
│   └── bundle_<SUBJECT>.json
├── tools/                      # ऑटोमेशन स्क्रिप्ट्स
│   ├── scaffold_and_audit.py
│   ├── sync_engine.py
│   ├── index_tracker.py
│   ├── build_catalog.py
│   └── test_engine.py
└── [6 Subject Directories]/    # CDP, Hindi, Mathematics, EVS, English, Sanskrit

🛠️ सीएलआई टूल्स संदर्भ (CLI Tools Reference)
| कमांड (Command) | कार्य (Purpose) |
|---|---|
| python3 tools/scaffold_and_audit.py | छूटे हुए फ़ोल्डर्स और डिफ़ॉल्ट JSON एसेट्स की जाँच व निर्माण |
| python3 tools/sync_engine.py | नए .txt इनपुट्स को .json में बदलने वाला लाइव वॉचर |
| python3 tools/index_tracker.py | सभी विषयों के कुल PYQ और MCQ प्रश्नों की गणना व इंडेक्स अपडेट |
| python3 tools/build_catalog.py | PWA के लिए dist_assets/ बंडल जनरेट करना |
| python3 tools/test_engine.py | टर्मिनल से 70:30 अनुपात में test_session.json जनरेट करना |
📜 ब्रांड एवं लाइसेंस (Brand & License)
 * Platform: SISKILL
 * Tagline: Super Intelligent Learning Skill
 * Architecture: Offline-First Educational PWA & Automated Question Bank Pipeline
   EOF

### जाँच करें
कमांड चलाने के बाद `ls -lh README.md blueprint.md` चलाकर सुनिश्चित करें कि दोनों मास्टर दस्तावेज़ आपकी रूट डायरेक्टरी में तैयार हो चुके हैं।

<ElicitationsGroup message="प्रोजेक्ट दस्तावेज़ीकरण पूर्ण हो चुका है। अगले कदम के लिए चुनें:">
  <Elicitation label="GitHub रिपॉजिटरी पर पुश और लाइव डिप्लॉय करें" query="सभी नई फ़ाइलों और dist_assets को GitHub पर कमिट करके GitHub Pages पर लाइव PWA होस्ट करने की कमांड्स बताएं।"/>
  <Elicitation label="कमज़ोर टॉपिक विश्लेषण (Weak-Area Diagnostic) जोड़ें" query="टेस्ट सबमिट होने पर माइक्रो-टॉपिक स्तर पर कमज़ोर क्षेत्रों का विश्लेषण और प्रोग्रेस हिस्ट्री दिखाने का कोड script.js में जोड़ें।"/>
  <Elicitation label="PWA को Android APK में पैक करें" query="हमारे SISKILL PWA को Capacitor के माध्यम से ऑफ़लाइन Android APK में बदलने की प्रक्रिया बताएं।"/>
</ElicitationsGroup>

