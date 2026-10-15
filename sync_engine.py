#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISKILL Background Sync Engine (v3.5)
Supports Rich Multi-line PYQ/MCQ Format (Tables, Assertion-Reason, Exam Refs,
Difficulty tags, Multi-bullet Explanations) + Concept.txt + Short_Notes.txt
"""

import os
import sys
import re
import json
import time
from datetime import datetime

# Ensure local imports from tools/ work from any working directory
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

import index_tracker
try:
    import build_catalog
except ImportError:
    build_catalog = None

ROOT_DIR = "."
POLL_INTERVAL = 3

TARGET_INPUTS = {
    "MCQ.txt": ("MCQ.json", "mcq"),
    "PYQ.txt": ("PYQ.json", "pyq"),
    "Concept.txt": ("Concept.json", "concept"),
    "Short_Notes.txt": ("Short_Notes.json", "short_notes")
}

def clean_math_symbols(text: str) -> str:
    """LaTeX-style symbols को पठनीय यूनिकोड चिह्नों में बदलता है।"""
    if not text:
        return ""
    replacements = {
        r"\times": "×",
        r"\div": "÷",
        r"\rightarrow": "→",
        r"\leftarrow": "←",
        r"\Rightarrow": "⇒",
        r"\geq": "≥",
        r"\leq": "≤",
        r"\neq": "≠"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()


# ================= Concept & Short Notes Parser =================

def parse_concept_text(file_path: str, micro_id: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = clean_math_symbols(f.read())

    lines = raw_text.splitlines()
    title = lines[0].replace("अध्याय:", "").strip() if lines else "अवधारणा विवरण"

    sections = []
    current_sec = None
    sec_regex = re.compile(r"^(\d+)\.\s*(.*?)$")

    for line in lines[1:]:
        line_clean = line.strip()
        match = sec_regex.match(line_clean)
        if match:
            if current_sec:
                current_sec["content"] = "\n".join(current_sec["raw_lines"]).strip()
                del current_sec["raw_lines"]
                sections.append(current_sec)

            current_sec = {
                "id": int(match.group(1)),
                "heading": match.group(2).strip(),
                "raw_lines": []
            }
        elif current_sec:
            current_sec["raw_lines"].append(line)

    if current_sec:
        current_sec["content"] = "\n".join(current_sec["raw_lines"]).strip()
        del current_sec["raw_lines"]
        sections.append(current_sec)

    return {
        "schema_version": "1.0.0",
        "asset_type": "Concept",
        "micro_topic_id": micro_id,
        "title": title,
        "sections": sections,
        "content": raw_text
    }


def parse_short_notes_text(file_path: str, micro_id: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = clean_math_symbols(f.read())

    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    title = "संक्षिप्त रिवीजन नोट्स"
    bullets = []

    for l in lines:
        if l.startswith("शीर्षक:") or l.startswith("Title:"):
            title = l.split(":", 1)[1].strip()
        elif l.startswith(("-", "•", "*")) or re.match(r"^\d+\.", l):
            bullets.append(re.sub(r"^[-•*\d.]+\s*", "", l))
        else:
            bullets.append(l)

    return {
        "schema_version": "1.0.0",
        "asset_type": "Short_Notes",
        "micro_topic_id": micro_id,
        "title": title,
        "bullet_points": bullets
    }


# ================= Rich PYQ & MCQ Multi-Line Parser =================

def parse_raw_file(file_path: str, start_id: int = 1) -> list:
    """
    उन्नत बहु-पंक्ति प्रश्न पार्सर:
    - 'प्रश्न 1', 'प्रश्न 2' या 'Q1.' से ब्लॉक विभाजित करता है
    - '* उत्तर:' से पहले के भाग से प्रश्न, परीक्षा संदर्भ, कठिनाई स्तर और 4 विकल्प निकालता है
    - '* उत्तर:' के बाद के भाग से सही विकल्प और विस्तृत व्याख्या (गलत विकल्पों के विश्लेषण सहित) निकालता है
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = clean_math_symbols(f.read())

    # 'प्रश्न 1', 'प्रश्न 2', 'प्र. 1', 'Q. 1' आदि से विभाजित करें
    q_split_pattern = re.compile(
        r"(?:^|\n)\s*(?:प्रश्न|प्र\.?|Q\.?|Question)\s*(\d+)\s*[:.\-]?\s*(?=\n|$|\"|')",
        re.IGNORECASE
    )

    matches = list(q_split_pattern.finditer(content))
    if not matches:
        # Fallback if question text starts on the same line after number
        q_split_pattern = re.compile(
            r"(?:^|\n)\s*(?:प्रश्न|प्र\.?|Q\.?|Question)\s*(\d+)\s*[:.\-]?\s*",
            re.IGNORECASE
        )
        matches = list(q_split_pattern.finditer(content))

    parsed_questions = []
    current_id = start_id

    # पैटर्न: उत्तर लाइन से विभाजित करने के लिए
    ans_split_regex = re.compile(
        r"\n\s*(?:[*•\-]\s*)?(?:सही\s+)?(?:उत्तर|Answer|Ans)\s*[:\-]\s*",
        re.IGNORECASE
    )

    # विकल्प पैटर्न: केवल लाइन की शुरुआत में (A), (B), (C), (D)
    opt_line_regex = re.compile(r"^\s*\(?([A-D])\)?[.)]?\s+(.+)$")

    for idx, match in enumerate(matches):
        block_start = match.end()
        block_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        block = content[block_start:block_end].strip()

        if not block:
            continue

        # 1. उत्तर लाइन से ब्लॉक को दो हिस्सों (प्रश्न+विकल्प बनाम उत्तर+व्याख्या) में बाँटें
        ans_split = ans_split_regex.split(block, maxsplit=1)
        if len(ans_split) < 2:
            continue

        pre_ans_part = ans_split[0].strip()
        post_ans_part = ans_split[1].strip()

        # 2. pre_ans_part से प्रश्न, मेटाडेटा और 4 विकल्प निकालें
        q_lines = []
        options = {}
        exam_ref = ""
        difficulty = ""
        in_options = False

        for line in pre_ans_part.splitlines():
            raw_line = line.strip()
            if not raw_line:
                continue

            # परीक्षा संदर्भ पहचानें
            if "परीक्षा संदर्भ" in raw_line or "Exam Ref" in raw_line:
                cleaned_ref = re.sub(r"^\(?गत वर्ष परीक्षा संदर्भ\s*[:\-]\s*|\)$", "", raw_line).strip()
                exam_ref = cleaned_ref
                continue

            # कठिनाई स्तर पहचानें
            if raw_line.startswith("कठिनाई स्तर") or raw_line.startswith("Difficulty"):
                difficulty = raw_line.split(":", 1)[-1].strip() if ":" in raw_line else raw_line
                continue

            # विकल्प (A), (B), (C), (D) पहचानें (केवल तब जब लाइन (A)/(B)/(C)/(D) से शुरू हो)
            opt_match = re.match(r"^\s*\(([A-D])\)\s*(.+)$", raw_line)
            if not opt_match:
                opt_match = re.match(r"^\s*([A-D])[.)]\s+(.+)$", raw_line)

            if opt_match:
                opt_key = opt_match.group(1).upper()
                opt_val = opt_match.group(2).strip()
                options[opt_key] = opt_val
                in_options = True
            else:
                if in_options and options:
                    # यदि किसी विकल्प का टेक्स्ट अगली लाइन में जारी हो
                    last_key = list(options.keys())[-1]
                    options[last_key] += " " + raw_line
                else:
                    q_lines.append(raw_line)

        question_text = "\n".join(q_lines).strip()

        # 3. post_ans_part से सही उत्तर (A/B/C/D) और विस्तृत व्याख्या निकालें
        post_lines = post_ans_part.splitlines()
        first_ans_line = post_lines[0].strip() if post_lines else ""
        ans_letter_match = re.search(r"([A-Da-d])", first_ans_line)
        if not ans_letter_match or len(options) < 2:
            continue

        correct_answer = ans_letter_match.group(1).upper()

        # शेष लाइनों से विस्तृत व्याख्या तैयार करें
        exp_lines = []
        for eline in post_lines[1:]:
            s_line = eline.strip()
            if not s_line:
                continue
            # '* विस्तृत व्याख्या:' हटाएँ, पर अंदर के बुलेट्स सुरक्षित रखें
            s_line = re.sub(r"^[*•\-]\s*विस्तृत व्याख्या\s*[:\-]?\s*", "", s_line)
            s_line = re.sub(r"^[*•\-]\s*(अन्य विकल्प क्यों गलत हैं\?)", r"\n🔍 \1", s_line)
            if s_line.startswith("* (") or s_line.startswith("• ("):
                s_line = "  • " + s_line.lstrip("*• ").strip()
            elif s_line.startswith("*") or s_line.startswith("•"):
                s_line = "• " + s_line.lstrip("*• ").strip()
            if s_line:
                exp_lines.append(s_line)

        detailed_explanation = "\n".join(exp_lines).strip()

        q_obj = {
            "id": current_id,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "detailed_explanation": detailed_explanation
        }
        if exam_ref:
            q_obj["exam_reference"] = exam_ref
        if difficulty:
            q_obj["difficulty"] = difficulty

        parsed_questions.append(q_obj)
        current_id += 1

    return parsed_questions


# ================= File Processor & Daemon Loop =================

def process_file(dirpath: str, input_filename: str, output_info):
    if isinstance(output_info, tuple):
        output_filename, asset_kind = output_info
    else:
        output_filename, asset_kind = output_info, ("mcq" if "MCQ" in output_filename else "pyq")

    input_path = os.path.join(dirpath, input_filename)
    output_path = os.path.join(dirpath, output_filename)
    micro_id = os.path.basename(dirpath)

    try:
        initial_size = os.path.getsize(input_path)
        time.sleep(0.4)
        if os.path.getsize(input_path) != initial_size:
            print(f"[WAIT] File is still being written: {input_path}")
            return
    except OSError:
        return

    if asset_kind == "concept":
        final_data = parse_concept_text(input_path, micro_id)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Generated Concept JSON: {output_path}")

    elif asset_kind == "short_notes":
        final_data = parse_short_notes_text(input_path, micro_id)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] Generated Short_Notes JSON: {output_path}")

    else:
        existing_data = {
            "micro_topic": micro_id,
            "asset_type": "MCQ" if asset_kind == "mcq" else "PYQ",
            "total_questions": 0,
            "questions": []
        }
        starting_id = 1

        if os.path.exists(output_path):
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    questions_list = existing_data.get("questions", [])
                    if questions_list:
                        max_id = max(q.get("id", 0) for q in questions_list)
                        starting_id = max_id + 1
            except Exception as e:
                print(f"[WARN] Corrupt JSON {output_path}: {e}. Creating backup.")
                os.rename(output_path, f"{output_path}.bak_{int(time.time())}")

        new_questions = parse_raw_file(input_path, starting_id)
        if not new_questions:
            print(f"[SKIP] No valid questions parsed from: {input_path}")
            return

        existing_data["questions"].extend(new_questions)
        existing_data["total_questions"] = len(existing_data["questions"])
        existing_data["last_updated"] = datetime.now().isoformat()

        temp_output_path = f"{output_path}.tmp"
        with open(temp_output_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        os.replace(temp_output_path, output_path)
        print(f"[SUCCESS] Appended {len(new_questions)} questions to {output_path} (Total: {existing_data['total_questions']})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = input_filename.replace(".txt", f".processed_{timestamp}.txt")
    archive_path = os.path.join(dirpath, archive_name)
    os.rename(input_path, archive_path)
    print(f"[ARCHIVE] Renamed {input_filename} -> {archive_name}")

    # Update master manifest and rebuild PWA distribution bundles automatically
    index_tracker.sync_master_manifest(ROOT_DIR)
    if build_catalog:
        build_catalog.build_distribution()


def run_monitor():
    print("=" * 60)
    print("[SISKILL ENGINE v3.5] Background Sync Daemon Active")
    print(f"Monitoring Root: {os.path.abspath(ROOT_DIR)}")
    print("Watching for: MCQ.txt | PYQ.txt | Concept.txt | Short_Notes.txt")
    print("Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        while True:
            for root, dirs, files in os.walk(ROOT_DIR):
                if "dist_assets" in root or ".git" in root or "__pycache__" in root:
                    continue
                for input_file, output_info in TARGET_INPUTS.items():
                    if input_file in files:
                        print(f"\n[DETECTED] New input file found: {os.path.join(root, input_file)}")
                        process_file(root, input_file, output_info)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n[STOPPED] Sync Engine shut down gracefully.")


if __name__ == "__main__":
    run_monitor()
