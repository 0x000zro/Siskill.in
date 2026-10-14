# 📘 SISKILL — Master Production Architecture & Engineering Blueprint
**Tagline:** *Super Intelligent Learning Skill*  
**Repository:** `~/Guru_G_SI_Skill`  
**Target Domain:** CTET & UPTET (Paper 1 & Paper 2) Offline-First Educational Ecosystem  
**Document Version:** 2.5.0 (Production-Ready Release)

---

## 1. Executive Summary & Project Scope

**SISKILL (Super Intelligent Learning Skill)** एक एंटरप्राइज-स्केल, ऑफलाइन-फर्स्ट प्रोग्रेसिव वेब ऐप (PWA) और ऑटोमेटेड कंटेंट इनजेशन पाइपलाइन है। इसे विशेष रूप से ग्रामीण और कम-इंटरनेट कनेक्टिविटी वाले क्षेत्रों के छात्रों के लिए डिज़ाइन किया गया है ताकि वे बिना किसी नेटवर्क बाधा के संपूर्ण अध्ययन सामग्री, शॉर्ट नोट्स, विगत वर्षों के प्रश्न (PYQ), अभ्यास प्रश्न (MCQ) और 150 प्रश्नों के सीबीटी (CBT) मॉक टेस्ट का अभ्यास कर सकें।

### 📊 Quantitative Scale (मात्रात्मक पैमाना)
| घटक (Component) | संख्या (Count) | विवरण (Description) |
| :--- | :--- | :--- |
| **कुल विषय (Subjects)** | **6** | CDP, Hindi, Mathematics, EVS, English, Sanskrit |
| **मुख्य अध्याय (Topics)** | **136** | 3-स्तरीय पदानुक्रम का प्रथम स्तर |
| **उप-अध्याय (Subtopics)** | **305** | पदानुक्रम का द्वितीय स्तर |
| **सूक्ष्म-बिंदु (Micro-topics)** | **765** | पदानुक्रम का तृतीय (अंतिम अध्ययन) स्तर |
| **कुल डायरेक्टरीज़ (Directories)** | **1,215** | संपूर्ण फ़ोल्डर ट्री संरचना |
| **कुल एसेट फ़ाइलें (Source Files)** | **3,842** | प्रत्येक माइक्रो-टॉपिक में 5 JSON एसेट्स + कॉन्फ़िग फ़ाइलें |
| **क्लाइंट डिस्ट्रिब्यूशन फ़ाइलें** | **7** | 1 `master_catalog.json` + 6 `bundle_<SUB>.json` |

---

## 2. Subject-Wise Taxonomy Breakdown (विषय-वार संरचना)

| कोड (ID) | विषय का नाम (English / हिंदी) | Topics | Subtopics | Micro-topics | डायरेक्टरी पथ (Directory) |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **CDP** | Child Development & Pedagogy (बाल विकास) | 27 | 66 | 255 | `Child_Development_and_Pedagogy/` |
| **HINDI** | Hindi Language & Pedagogy (हिन्दी भाषा) | 18 | 42 | 88 | `Hindi/` |
| **MATH** | Mathematics & Pedagogy (गणित) | 24 | 51 | 105 | `Mathematics/` |
| **EVS** | Environmental Studies (पर्यावरण अध्ययन) | 24 | 52 | 115 | `Environmental_Studies/` |
| **ENG** | English Language & Pedagogy (अंग्रेजी) | 21 | 44 | 97 | `English/` |
| **SAN** | Sanskrit Language & Pedagogy (संस्कृत) | 22 | 50 | 105 | `Sanskrit/` |
| **TOTAL** | **6 Core Subjects** | **136** | **305** | **765** | **1,215 Directories** |

---

## 3. End-to-End System Architecture (संपूर्ण प्रणाली वास्तुकला)

सिस्टम को दो स्पष्ट परतों में विभाजित किया गया है ताकि **Authoring (लेखन/प्रबंधन)** और **Delivery (छात्र के मोबाइल पर प्रदर्शन)** में कोई टकराव न हो:

```text
====================================================================================
 LAYER 1: AUTHORING & AUTOMATION PIPELINE (Termux / Linux Server / Git Repo)
====================================================================================

  [Raw Input Files dropped in any of 765 Micro-topic Folders]
   ├── Concept.txt       (अध्याय एवं सेक्शन-वार विस्तृत थ्योरी)
   ├── Short_Notes.txt   (बुलेट-पॉइंट क्विक रिवीजन नोट्स)
   ├── PYQ.txt           (विगत वर्षों के प्रश्न + व्याख्या)
   └── MCQ.txt           (नए अभ्यास प्रश्न + व्याख्या)
          │
          ▼ (Monitored every 3 seconds)
  ┌──────────────────────────────────────────────────────────────────────┐
  │ tools/sync_engine.py (Background Daemon)                             │
  │  1. Detects raw .txt files & verifies write completion               │
  │  2. Parses text via Regex into structured, sparse JSON               │
  │  3. Auto-increments Question IDs (1, 2, 3...) for MCQ/PYQ            │
  │  4. Archives raw file -> <Name>.processed_YYYYMMDD_HHMMSS.txt        │
  └───────────────────────┬──────────────────────────────────────────────┘
                          │
          ┌───────────────┴────────────────┐
          ▼                                ▼
  ┌──────────────────────────────┐ ┌─────────────────────────────────────┐
  │ tools/index_tracker.py       │ │ tools/build_catalog.py              │
  │ • Scans 3,842 files          │ │ • Compiles 3,842 files into         │
  │ • Updates 6 <Sub>_index.json │ │   dist_assets/ (Only 7 Files!)      │
  │ • Updates root manifest.json │ │ • Eliminates HTTP/File I/O lag      │
  └──────────────────────────────┘ └──────────────────┬──────────────────┘
                                                      │
======================================================│=============================
 LAYER 2: OFFLINE-FIRST PWA & CLIENT DELIVERY         │
======================================================▼=============================

  ┌──────────────────────────────────────────────────────────────────────┐
  │ dist_assets/ (Static Host / GitHub Pages / Local Capacitor Assets)   │
  │  ├── master_catalog.json  (~250 KB - Navigation & Search Index)      │
  │  └── bundle_<SUB>.json    (6 Subject Bundles containing all assets)  │
  └───────────────────────┬──────────────────────────────────────────────┘
                          │ (Fetched once & Cached via Service Worker)
                          ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │ SISKILL Student PWA Client (index.html + style.css + app.js)         │
  │  ├── Service Worker (sw.js)     : Offline Cache-First + Dynamic Sync │
  │  ├── Collapsible Tree Sidebar   : 3-Tier Navigation (☰ Toggle)       │
  │  ├── Typography Engine          : 'Kalam' Handwriting + 18px Base    │
  │  ├── Interactive Asset Reader   :                                    │
  │  │    ├─ [Concept]     : Section-wise Card Reader                    │
  │  │    ├─ [Short_Notes] : Bullet-point Revision                       │
  │  │    ├─ [PYQ / MCQ]   : Hidden-Answer Interactive Quiz Mode         │
  │  │    └─ [30Q Test]    : Micro-topic 30-Min CBT Timer Test           │
  │  └── Full Mock Engine (script.js): 150Q, 5-Section, 150-Min CBT      │
  └──────────────────────────────────────────────────────────────────────┘

~/Guru_G_SI_Skill/
├── index.html                  # मुख्य PWA यूजर इंटरफ़ेस (App Shell)
├── style.css                   # रेस्पॉन्सिव स्टाइलिंग, हैंडराइटिंग फॉन्ट व बड़े फॉन्ट्स
├── app.js                      # कोर कैटलॉग लोडर, ट्री नेविगेशन और इंटरएक्टिव रीडर
├── script.js                   # 30Q माइक्रो-टेस्ट और 150Q फुल सीबीटी मॉक टेस्ट इंजन
├── sw.js                       # ऑफ़लाइन सर्विस वर्कर (Cache-First Strategy)
├── manifest.webmanifest        # PWA इंस्टॉलेशन मैनिफ़ेस्ट (Add to Home Screen)
├── manifest.json               # संपूर्ण रिपॉजिटरी का मास्टर डेटा मैनिफ़ेस्ट
├── brand_config.json           # ब्रांडिंग और थीम कॉन्फ़िगरेशन
├── social_links.json           # सोशल और सपोर्ट लिंक्स
├── blueprint.md                # यह मास्टर आर्किटेक्चर डॉक्यूमेंट
│
├── dist_assets/                # क्लाइंट PWA के लिए संकलित 7 डिस्ट्रिब्यूशन फ़ाइलें
│   ├── master_catalog.json
│   ├── bundle_CDP.json
│   ├── bundle_HINDI.json
│   ├── bundle_MATH.json
│   ├── bundle_EVS.json
│   ├── bundle_ENG.json
│   └── bundle_SAN.json
│
├── tools/                      # बैकएंड ऑटोमेशन और बिल्ड स्क्रिप्ट्स
│   ├── scaffold_and_audit.py   # 1,215 फ़ोल्डर्स और डिफ़ॉल्ट JSON बनाने व जाँचने की स्क्रिप्ट
│   ├── sync_engine.py          # 24/7 बैकग्राउंड टेक्स्ट-टू-JSON पार्सर डेमन
│   ├── index_tracker.py        # रियल-टाइम प्रश्न काउंटर और इंडेक्स अपडेटर
│   ├── build_catalog.py        # 3,842 फ़ाइलों को 7 बंडलों में कंपाइल करने वाला बंडलर
│   └── test_engine.py          # CLI आधारित 70:30 मॉक टेस्ट जनरेटर
│
├── Child_Development_and_Pedagogy/
│   ├── CDP_index.json
│   └── Topic_01_.../Subtopic_01_.../Micro_01_.../
│       ├── Concept.json
│       ├── Short_Notes.json
│       ├── MCQ.json
│       ├── PYQ.json
│       └── Practice.json
├── Hindi/                      # (समान 3-स्तरीय संरचना)
├── Mathematics/                # (समान 3-स्तरीय संरचना)
├── Environmental_Studies/      # (समान 3-स्तरीय संरचना)
├── English/                    # (समान 3-स्तरीय संरचना)
└── Sanskrit/                   # (समान 3-स्तरीय संरचना)

EFO
