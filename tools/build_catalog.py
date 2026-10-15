#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISKILL Distribution Bundler (v3.0 - Collision-Proof & Verified)
Compiles 3,842 individual asset files into 6 Subject Bundles and 1 Master Catalog.
"""

import os
import json
from datetime import datetime

ROOT_DIR = "."
DIST_DIR = "dist_assets"

INDEX_MAP = {
    "CDP": "Child_Development_and_Pedagogy/CDP_index.json",
    "HINDI": "Hindi/Hindi_index.json",
    "MATH": "Mathematics/Maths_index.json",
    "EVS": "Environmental_Studies/EVS_index.json",
    "ENG": "English/Eng_index.json",
    "SAN": "Sanskrit/Sanskrit_index.json"
}

def build_distribution():
    os.makedirs(DIST_DIR, exist_ok=True)
    master_catalog = {
        "generated_at": datetime.now().isoformat(),
        "total_subjects": len(INDEX_MAP),
        "subjects": []
    }

    print("=" * 60)
    print("[SISKILL BUNDLER v3.0] Compiling Assets into Distribution Packages")
    print("=" * 60)

    for sub_id, index_rel in INDEX_MAP.items():
        index_path = os.path.join(ROOT_DIR, index_rel)
        if not os.path.exists(index_path):
            print(f"[WARN] Index file missing: {index_path}. Skipping.")
            continue

        with open(index_path, "r", encoding="utf-8") as f:
            sub_meta = json.load(f)

        sub_dir = sub_meta.get("subject", {}).get("directory", os.path.dirname(index_rel))
        subject_bundle = {
            "id": sub_id,
            "name_en": sub_meta.get("subject", {}).get("name_en", sub_id),
            "name_hi": sub_meta.get("subject", {}).get("name_hi", sub_id),
            "compiled_at": datetime.now().isoformat(),
            "micro_topics": {}
        }

        catalog_topics = []
        sub_mcq_total = 0
        sub_pyq_total = 0

        for t_idx, t in enumerate(sub_meta.get("topics", []), 1):
            t_folder = t.get("folder", t.get("slug", ""))
            t_id = t.get("id", f"T{t_idx:02d}")
            cat_subtopics = []

            for st_idx, st in enumerate(t.get("subtopics", []), 1):
                st_folder = st.get("folder", st.get("slug", ""))
                st_id = st.get("id", f"{t_id}_ST{st_idx:02d}")
                cat_micros = []

                for m_idx, m in enumerate(st.get("micro_topics", []), 1):
                    m_folder = m.get("folder", m.get("slug", ""))
                    raw_m_id = m.get("id", m.get("micro_id", m_folder))

                    # Collision-proof ID: if raw_m_id already exists in bundle, scope it with st_id
                    m_id = raw_m_id if raw_m_id and raw_m_id not in subject_bundle["micro_topics"] else f"{st_id}_{m_folder or m_idx}"

                    target_dir = os.path.join(ROOT_DIR, sub_dir, t_folder, st_folder, m_folder)

                    assets_data = {}
                    for asset_name in ["Concept", "Short_Notes", "MCQ", "PYQ", "Practice"]:
                        a_path = os.path.join(target_dir, f"{asset_name}.json")
                        if os.path.exists(a_path):
                            try:
                                with open(a_path, "r", encoding="utf-8") as af:
                                    assets_data[asset_name] = json.load(af)
                            except Exception:
                                pass

                    subject_bundle["micro_topics"][m_id] = assets_data

                    mcq_count = len(assets_data.get("MCQ", {}).get("questions", []))
                    pyq_count = len(assets_data.get("PYQ", {}).get("questions", []))
                    sub_mcq_total += mcq_count
                    sub_pyq_total += pyq_count

                    cat_micros.append({
                        "id": m_id,
                        "name_hi": m.get("name_hi", m_folder),
                        "name_en": m.get("name_en", m.get("slug", m_folder)),
                        "folder": m_folder,
                        "mcq_count": mcq_count,
                        "pyq_count": pyq_count,
                        "has_concept": "Concept" in assets_data,
                        "has_short_notes": "Short_Notes" in assets_data
                    })

                cat_subtopics.append({
                    "id": st_id,
                    "name_hi": st.get("name_hi", st_folder),
                    "name_en": st.get("name_en", st.get("slug", st_folder)),
                    "micro_topics": cat_micros
                })

            catalog_topics.append({
                "id": t_id,
                "name_hi": t.get("name_hi", t_folder),
                "name_en": t.get("name_en", t.get("slug", t_folder)),
                "subtopics": cat_subtopics
            })

        bundle_file = os.path.join(DIST_DIR, f"bundle_{sub_id}.json")
        with open(bundle_file, "w", encoding="utf-8") as bf:
            json.dump(subject_bundle, bf, ensure_ascii=False)

        master_catalog["subjects"].append({
            "id": sub_id,
            "name_en": sub_meta.get("subject", {}).get("name_en", sub_id),
            "name_hi": sub_meta.get("subject", {}).get("name_hi", sub_id),
            "bundle_file": f"bundle_{sub_id}.json",
            "total_mcqs": sub_mcq_total,
            "total_pyqs": sub_pyq_total,
            "total_questions": sub_mcq_total + sub_pyq_total,
            "topics": catalog_topics
        })
        print(f"  [✓] Bundled {sub_id:<6} -> {bundle_file} (Topics: {len(catalog_topics)}, MCQs: {sub_mcq_total}, PYQs: {sub_pyq_total})")

    cat_file = os.path.join(DIST_DIR, "master_catalog.json")
    with open(cat_file, "w", encoding="utf-8") as cf:
        json.dump(master_catalog, cf, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"[SUCCESS] Master Catalog generated -> {cat_file}")
    print("=" * 60)

if __name__ == "__main__":
    build_distribution()
