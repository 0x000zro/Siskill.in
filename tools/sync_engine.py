#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISKILL Unified Question Bank & Content Engine - Phase 2
File: tools/sync_engine.py
Function:
  - Multi-asset monitor: MCQ.txt, PYQ.txt, Concept.txt, content.txt, Short_Notes.txt
  - Bilingual resilient parser (MCQ / PYQ) with auto-increment ID append
  - Hierarchical theory parser (Concept / content) with metadata, metrics & callouts
  - Structured notes parser (Short_Notes) with key-term flashcards & categorization
  - Safe atomic write (.tmp -> .json) and timestamped file archiving
"""

import os
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ================= Configuration =================
ROOT_DIR = "."  # रूट डायरेक्टरी पाथ
POLL_INTERVAL_SECONDS = 3  # स्कैनिंग अंतराल (सेकंड)

# मॉनिटर की जाने वाली फाइलें, उनका आउटपुट और प्रोसेसिंग टाइप
TARGET_CONFIG = {
    "MCQ.txt": {"output": "MCQ.json", "type": "mcq", "mode": "append"},
    "PYQ.txt": {"output": "PYQ.json", "type": "pyq", "mode": "append"},
    "Concept.txt": {"output": "Concept.json", "type": "concept", "mode": "replace"},
    "content.txt": {"output": "content.json", "type": "concept", "mode": "replace"},
    "Short_Notes.txt": {"output": "Short_Notes.json", "type": "notes", "mode": "replace"}
}

# इनफिनिट लूप प्रोटेक्शन के लिए टाइमस्टैम्प कैश
FILE_MTIME_CACHE: Dict[str, float] = {}

# MCQ/PYQ मेटाडेटा टर्मिनेटर पैटर्न (हिंदी व अंग्रेजी कीवर्ड्स)
TERMINATOR_PATTERN = (
    r'(?='
    r'Related Theory/Trend:|संबंधित सिद्धांत एवं परिप्रेक्ष्य:|संबंधित सिद्धांत:|'
    r'Exam Trick/Common Confusion:|परीक्षा युक्ति एवं सामान्य भ्रम:|परीक्षा युक्ति:|'
    r'Memory Tip:|स्मरण सूत्र:|'
    r'Difficulty Rating:|कठिनाई स्तर:|'
    r'Bloom Level:|ब्लूम का संज्ञानात्मक स्तर:|'
    r'Competency Tested:|परीक्षित दक्षता:|'
    r'Previous CTET Trend:|पूर्व सीटीईटी प्रवृत्ति:|'
    r'Exam Name:|परीक्षा का नाम:|'
    r'Exam Year:|परीक्षा वर्ष:|'
    r'Paper:|प्रश्नपत्र:|'
    r'\n*\s*(?:प्रश्न|Q|Question)\s*\d+'
    r'|$)'
)


# ================= Shared Utilities =================

def safe_read_file(file_path: str) -> str:
    """UTF-8 और Windows BOM (utf-8-sig) को सुरक्षित तरीके से पढ़ता है।"""
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read().strip()


def clean_text(text: str) -> str:
    """अनावश्यक स्पेस और लाइन ब्रेक साफ़ करता है।"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def calculate_read_metrics(text: str) -> Dict[str, int]:
    """शब्द संख्या और पढ़ने में लगने वाले समय (150 WPM) की गणना करता है।"""
    words = re.findall(r'\S+', text)
    word_count = len(words)
    return {
        "word_count": word_count,
        "reading_time_minutes": max(1, round(word_count / 150))
    }


def extract_metadata_and_body(raw_text: str) -> Tuple[Dict[str, str], str]:
    """टेक्स्ट के शीर्ष से की-वैल्यू मेटाडेटा निकालता है।"""
    metadata = {}
    lines = raw_text.splitlines()
    body_start_idx = 0
    meta_regex = re.compile(r'^(?:शीर्षक|अध्याय|Title|Topic|Category|Tags|महत्व|Difficulty)\s*[:\-]\s*(.*)$', re.IGNORECASE)

    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            if metadata:
                body_start_idx = i + 1
                break
            continue

        match = meta_regex.match(line_clean)
        if match:
            key = line_clean.split(":", 1)[0].split("-", 1)[0].strip().lower()
            metadata[key] = match.group(1).strip()
        else:
            if i == 0 and line_clean.startswith("# "):
                metadata["title"] = line_clean.lstrip("# ").strip()
                body_start_idx = 1
                break
            body_start_idx = i
            break

    remaining_body = "\n".join(lines[body_start_idx:]).strip()
    return metadata, remaining_body


# ================= 1. MCQ & PYQ Engine =================

def parse_question_block(block: str, next_id: int) -> Optional[Dict[str, Any]]:
    """द्विभाषी प्रारूप में एक प्रश्न ब्लॉक को पार्स करता है।"""
    q_match = re.search(r'(?:प्रश्न|Q|Question)\s*\d+\s*[:.\-]?\s*\n*(.*?)(?=\(1\))', block, re.DOTALL)
    if not q_match:
        return None

    question_text = clean_text(q_match.group(1))

    # इनलाइन या अलग-अलग पंक्तियों वाले 4 विकल्प
    opt1 = re.search(r'\(1\)\s*(.*?)(?=\(2\))', block, re.DOTALL)
    opt2 = re.search(r'\(2\)\s*(.*?)(?=\(3\))', block, re.DOTALL)
    opt3 = re.search(r'\(3\)\s*(.*?)(?=\(4\))', block, re.DOTALL)
    opt4 = re.search(r'\(4\)\s*(.*?)(?=(?:Correct Answer:|सही उत्तर:|उत्तर:))', block, re.DOTALL)

    if not (opt1 and opt2 and opt3 and opt4):
        return None

    options = {
        "1": clean_text(opt1.group(1)),
        "2": clean_text(opt2.group(1)),
        "3": clean_text(opt3.group(1)),
        "4": clean_text(opt4.group(1))
    }

    ans_match = re.search(r'(?:Correct Answer:|सही उत्तर:|उत्तर:)\s*\(?([1-4A-Da-d])\)?', block)
    if not ans_match:
        return None
    raw_ans = ans_match.group(1).strip()
    ans_map = {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'a': '1', 'b': '2', 'c': '3', 'd': '4'}
    correct_answer = ans_map.get(raw_ans, raw_ans)

    exp_pattern = rf'(?:Detailed Explanation:|विस्तृत संकल्पनात्मक विश्लेषण:|विस्तृत व्याख्या:)\s*(.*?){TERMINATOR_PATTERN}'
    exp_match = re.search(exp_pattern, block, re.DOTALL)
    if not exp_match:
        return None
    detailed_explanation = clean_text(exp_match.group(1))

    item = {
        "id": next_id,
        "question": question_text,
        "options": options,
        "correct_answer": correct_answer,
        "detailed_explanation": detailed_explanation
    }

    optional_patterns = [
        ("related_theory", rf'(?:Related Theory/Trend:|संबंधित सिद्धांत एवं परिप्रेक्ष्य:|संबंधित सिद्धांत:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("exam_trick", rf'(?:Exam Trick/Common Confusion:|परीक्षा युक्ति एवं सामान्य भ्रम:|परीक्षा युक्ति:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("memory_tip", rf'(?:Memory Tip:|स्मरण सूत्र:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("difficulty_rating", rf'(?:Difficulty Rating:|कठिनाई स्तर:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("bloom_level", rf'(?:Bloom Level:|ब्लूम का संज्ञानात्मक स्तर:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("competency_tested", rf'(?:Competency Tested:|परीक्षित दक्षता:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("previous_trend", rf'(?:Previous CTET Trend:|पूर्व सीटीईटी प्रवृत्ति:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("exam_name", rf'(?:Exam Name:|परीक्षा का नाम:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("exam_year", rf'(?:Exam Year:|परीक्षा वर्ष:)\s*(.*?){TERMINATOR_PATTERN}'),
        ("paper", rf'(?:Paper:|प्रश्नपत्र:)\s*(.*?)(?=$)')
    ]

    for key, pattern in optional_patterns:
        match = re.search(pattern, block, re.DOTALL)
        if match:
            val = clean_text(match.group(1))
            if val:
                item[key] = val

    return item


def parse_mcq_file(file_path: str, starting_id: int) -> List[Dict[str, Any]]:
    """MCQ/PYQ फाइल को पढ़कर संरचित प्रश्नों की सूची देता है।"""
    content = safe_read_file(file_path)
    raw_blocks = re.split(r'(?=(?:^|\n)\s*(?:प्रश्न|Q|Question)\s*\d+)', content.strip())
    parsed_questions = []
    current_id = starting_id

    for block in raw_blocks:
        if not block.strip():
            continue
        q_obj = parse_question_block(block, current_id)
        if q_obj:
            parsed_questions.append(q_obj)
            current_id += 1

    return parsed_questions


# ================= 2. Concept & Theory Engine =================

def extract_callouts(text: str) -> List[Dict[str, str]]:
    """नोट्स और परीक्षा युक्तियों (💡/Note:) को अलग करता है।"""
    callouts = []
    pattern = re.compile(r'(?:>|💡|NOTE:|नोट:|टिप:|स्मरण:)\s*(.*?)(?=\n\n|\n[#>💡]|$)', re.IGNORECASE | re.DOTALL)
    for m in pattern.finditer(text):
        val = m.group(1).strip()
        if val:
            callouts.append({
                "type": "tip" if any(w in m.group(0).lower() for w in ["💡", "टिप", "tip"]) else "note",
                "text": re.sub(r'\s+', ' ', val)
            })
    return callouts


def parse_concept_text(file_path: str, micro_id: str) -> Dict[str, Any]:
    """Concept.txt या content.txt को संरचित थ्योरी JSON में बदलता है।"""
    raw_text = safe_read_file(file_path)
    if not raw_text:
        return {}

    meta, body = extract_metadata_and_body(raw_text)
    title = meta.get("title") or meta.get("शीर्षक") or meta.get("अध्याय") or "अवधारणा विवरण"

    lines = body.splitlines()
    sections: List[Dict[str, Any]] = []
    current_sec: Optional[Dict[str, Any]] = None
    pre_section_lines: List[str] = []
    sec_counter = 1

    header_regex = re.compile(r'^(?:#{1,3}\s*(.*?)|(\d+)[\.\:\-\)]\s+(.*?))$')

    for line in lines:
        line_clean = line.strip()
        match = header_regex.match(line_clean)
        is_heading = False
        heading_title = ""
        heading_id = sec_counter

        if match and len(line_clean) <= 120 and not line_clean.endswith(('।', '.', '?')):
            if match.group(1):
                heading_title = match.group(1).strip()
                is_heading = True
            elif match.group(3):
                heading_title = match.group(3).strip()
                try:
                    heading_id = int(match.group(2))
                except ValueError:
                    heading_id = sec_counter
                is_heading = True

        if is_heading:
            if current_sec:
                raw_sec = "\n".join(current_sec.pop("raw_lines")).strip()
                current_sec["content"] = raw_sec
                current_sec["callouts"] = extract_callouts(raw_sec)
                sections.append(current_sec)
            elif pre_section_lines:
                ov_text = "\n".join(pre_section_lines).strip()
                if ov_text:
                    sections.append({
                        "id": 0,
                        "heading": "प्रस्तावना / Overview",
                        "content": ov_text,
                        "callouts": extract_callouts(ov_text)
                    })

            current_sec = {
                "id": heading_id,
                "heading": heading_title,
                "raw_lines": []
            }
            sec_counter += 1
        else:
            if current_sec:
                current_sec["raw_lines"].append(line)
            else:
                pre_section_lines.append(line)

    if current_sec:
        raw_sec = "\n".join(current_sec.pop("raw_lines")).strip()
        current_sec["content"] = raw_sec
        current_sec["callouts"] = extract_callouts(raw_sec)
        sections.append(current_sec)
    elif pre_section_lines and not sections:
        full_text = "\n".join(pre_section_lines).strip()
        sections.append({
            "id": 1,
            "heading": "मुख्य अवधारणा",
            "content": full_text,
            "callouts": extract_callouts(full_text)
        })

    metrics = calculate_read_metrics(raw_text)
    plain_preview = re.sub(r'[\#\*\-\`]', '', body).strip().replace('\n', ' ')
    summary_preview = plain_preview[:160] + "..." if len(plain_preview) > 160 else plain_preview

    return {
        "schema_version": "2.0.0",
        "asset_type": "Concept",
        "micro_topic_id": micro_id,
        "title": title,
        "metrics": metrics,
        "summary_preview": summary_preview,
        "sections_count": len(sections),
        "sections": sections,
        "content": raw_text,
        "last_updated": datetime.now().isoformat()
    }


# ================= 3. Short Notes Engine =================

def parse_short_notes_text(file_path: str, micro_id: str) -> Dict[str, Any]:
    """Short_Notes.txt को संरचित बुलेट्स और की-टर्म्स में बदलता है।"""
    raw_text = safe_read_file(file_path)
    if not raw_text:
        return {}

    meta, body = extract_metadata_and_body(raw_text)
    title = meta.get("title") or meta.get("शीर्षक") or "संक्षिप्त रिवीजन नोट्स"

    bullet_marker_regex = re.compile(r'^(?:[-•*+]|\d+[\.\)])\s+(.*)$')
    group_heading_regex = re.compile(r'^(?:#{1,3}\s*(.*?)|([A-Za-z0-9\u0900-\u097F\s]{2,40})[:\-]\s*)$')

    groups: List[Dict[str, Any]] = []
    current_group_title = "महत्वपूर्ण बिंदु"
    current_group_points: List[str] = []
    all_flat_bullets: List[str] = []
    key_terms: List[Dict[str, str]] = []

    lines = body.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line_clean = lines[i].strip()
        if not line_clean:
            i += 1
            continue

        heading_match = group_heading_regex.match(line_clean)
        if heading_match and not bullet_marker_regex.match(line_clean) and len(line_clean) < 60:
            if current_group_points:
                groups.append({"category": current_group_title, "points": current_group_points})
                current_group_points = []
            current_group_title = (heading_match.group(1) or heading_match.group(2) or line_clean).strip().rstrip(":-")
            i += 1
            continue

        b_match = bullet_marker_regex.match(line_clean)
        if b_match:
            bullet_text = b_match.group(1).strip()
            i += 1
            continuation_lines = []
            while i < n:
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    break
                if not bullet_marker_regex.match(next_line) and not group_heading_regex.match(next_line):
                    continuation_lines.append(next_line)
                    i += 1
                else:
                    break

            if continuation_lines:
                bullet_text += " " + " ".join(continuation_lines)

            bullet_text = re.sub(r'\s+', ' ', bullet_text).strip()
            current_group_points.append(bullet_text)
            all_flat_bullets.append(bullet_text)

            term_match = re.match(r'^(?:\*\*(.*?)\*\*|(.*?))\s*[:\-—]\s*(.*)$', bullet_text)
            if term_match:
                term_name = (term_match.group(1) or term_match.group(2)).strip()
                term_desc = term_match.group(3).strip()
                if 2 <= len(term_name) <= 50 and len(term_desc) > 5:
                    key_terms.append({"term": term_name, "definition": term_desc})
        else:
            current_group_points.append(line_clean)
            all_flat_bullets.append(line_clean)
            i += 1

    if current_group_points:
        groups.append({"category": current_group_title, "points": current_group_points})

    metrics = calculate_read_metrics(raw_text)

    return {
        "schema_version": "2.0.0",
        "asset_type": "Short_Notes",
        "micro_topic_id": micro_id,
        "title": title,
        "metrics": metrics,
        "total_points": len(all_flat_bullets),
        "groups": groups,
        "key_terms": key_terms,
        "bullet_points": all_flat_bullets,
        "last_updated": datetime.now().isoformat()
    }


# ================= Core Dispatcher & File Sync =================

def process_file(dirpath: str, input_filename: str, cfg: Dict[str, str]):
    """इनपुट फाइल के प्रकार के अनुसार उसे पार्स, सेव और आर्काइव करता है।"""
    input_path = os.path.join(dirpath, input_filename)
    output_path = os.path.join(dirpath, cfg["output"])
    micro_id = os.path.basename(dirpath)

    # 1. MTime और पार्शियल राइट प्रोटेक्शन
    try:
        current_mtime = os.path.getmtime(input_path)
        if FILE_MTIME_CACHE.get(input_path) == current_mtime:
            return

        initial_size = os.path.getsize(input_path)
        time.sleep(0.5)
        if os.path.getsize(input_path) != initial_size:
            print(f"[WAIT] File is being written: {input_path}")
            return
    except OSError:
        return

    print(f"\n[DETECTED] New input file found: {input_path}")
    asset_type = cfg["type"]
    mode = cfg["mode"]

    # 2. रूटिंग एवं पार्सिंग
    if asset_type in ("mcq", "pyq"):
        starting_id = 1
        existing_data = {
            "micro_topic": micro_id,
            "asset_type": "MCQ" if asset_type == "mcq" else "PYQ",
            "total_questions": 0,
            "questions": []
        }

        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    q_list = existing_data.get("questions", [])
                    if q_list:
                        starting_id = max(q.get("id", 0) for q in q_list) + 1
            except Exception as e:
                print(f"[WARN] Error reading existing JSON {output_path}: {e}")

        new_items = parse_mcq_file(input_path, starting_id)
        if not new_items:
            print(f"[SKIP] No valid questions parsed from: {input_path}")
            FILE_MTIME_CACHE[input_path] = current_mtime
            return

        existing_data["questions"].extend(new_items)
        existing_data["total_questions"] = len(existing_data["questions"])
        existing_data["last_updated"] = datetime.now().isoformat()
        final_payload = existing_data
        log_msg = f"Appended {len(new_items)} questions to {output_path} (Total: {final_payload['total_questions']})"

    elif asset_type == "concept":
        final_payload = parse_concept_text(input_path, micro_id)
        if not final_payload or not final_payload.get("sections"):
            print(f"[SKIP] No valid concept sections parsed from: {input_path}")
            FILE_MTIME_CACHE[input_path] = current_mtime
            return
        log_msg = f"Generated Concept JSON ({final_payload['sections_count']} sections) -> {output_path}"

    elif asset_type == "notes":
        final_payload = parse_short_notes_text(input_path, micro_id)
        if not final_payload or not final_payload.get("bullet_points"):
            print(f"[SKIP] No valid short notes points parsed from: {input_path}")
            FILE_MTIME_CACHE[input_path] = current_mtime
            return
        log_msg = f"Generated Short Notes JSON ({final_payload['total_points']} points) -> {output_path}"
    else:
        return

    # 3. एटॉमिक राइट (.tmp -> .json)
    temp_output_path = f"{output_path}.tmp"
    with open(temp_output_path, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, ensure_ascii=False, indent=2)
    os.replace(temp_output_path, output_path)
    print(f"[SUCCESS] {log_msg}")

    # 4. आर्काइविंग (.txt -> .processed_<timestamp>.txt)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = input_filename.replace(".txt", f".processed_{timestamp}.txt")
    archive_path = os.path.join(dirpath, archive_name)
    os.rename(input_path, archive_path)
    print(f"[ARCHIVE] Renamed {input_filename} -> {archive_name}")

    if input_path in FILE_MTIME_CACHE:
        del FILE_MTIME_CACHE[input_path]

    # 5. मास्टर इंडेक्स ट्रैकर सिंक (यदि उपलब्ध हो)
    try:
        import index_tracker
        index_tracker.sync_master_manifest(ROOT_DIR)
    except (ImportError, AttributeError):
        pass


# ================= Monitoring Daemon Loop =================

def run_monitor():
    """बैकग्राउंड डायरेक्टरी ट्री मॉनिटर लूप।"""
    print("=" * 60)
    print("[SISKILL ENGINE] Background Sync Daemon Active (v2.0.0)")
    print(f"Monitoring Root: {os.path.abspath(ROOT_DIR)}")
    print("Watching for: " + ", ".join(TARGET_CONFIG.keys()))
    print(f"Polling Interval: {POLL_INTERVAL_SECONDS} seconds | Press Ctrl+C to stop.")
    print("=" * 60)

    while True:
        try:
            for root, dirs, files in os.walk(ROOT_DIR):
                for input_file, cfg in TARGET_CONFIG.items():
                    if input_file in files:
                        process_file(root, input_file, cfg)

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n[STOPPED] Sync Engine cleanly stopped by user.")
            break
        except Exception as err:
            print(f"[UNEXPECTED ERROR] {err}")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_monitor()
