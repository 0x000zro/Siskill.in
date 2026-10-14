#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SISKILL Distribution Bundler
Converts 3,842 scattered asset files into 6 Subject Bundles and 1 Master Catalog.
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
        "subjects": []
    }

    print("[BUILD] Compiling 3,842 files into optimized bundles...")

    for sub_id, index_rel in INDEX_MAP.items():
        index_path = os.path.join(ROOT_DIR, index_rel)
        if not os.path.exists(index_path):
            continue

        with open(index_path, "r", encoding="utf-8") as f:
            sub_meta = json.load(f)

        sub_dir = sub_meta.get("subject", {}).get("directory", "")
        subject_bundle = {
            "id": sub_id,
            "name_en": sub_meta.get("subject", {}).get("name_en"),
            "name_hi": sub_meta.get("subject", {}).get("name_hi"),
            "micro_topics": {}  # id -> { Concept, Short_Notes, MCQ, PYQ }
        }

        catalog_topics = []

        for t in sub_meta.get("topics", []):
            t_folder = t.get("folder", "")
            cat_subtopics = []

            for st in t.get("subtopics", []):
                st_folder = st.get("folder", "")
                cat_micros = []

                for m in st.get("micro_topics", []):
                    m_id = m.get("id")
                    m_folder = m.get("folder", "")
                    target_dir = os.path.join(ROOT_DIR, sub_dir, t_folder, st_folder, m_folder)

                    # माइक्रो-टॉपिक के सभी एसेट्स को एक स्थान पर संकलित करना
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

                    cat_micros.append({
                        "id": m_id,
                        "name_hi": m.get("name_hi"),
                        "name_en": m.get("name_en", m.get("slug")),
                        "mcq_count": len(assets_data.get("MCQ", {}).get("questions", [])),
                        "pyq_count": len(assets_data.get("PYQ", {}).get("questions", []))
                    })

                cat_subtopics.append({
                    "id": st.get("id"),
                    "name_hi": st.get("name_hi"),
                    "name_en": st.get("name_en", st.get("slug")),
                    "micro_topics": cat_micros
                })

            catalog_topics.append({
                "id": t.get("id"),
                "name_hi": t.get("name_hi"),
                "name_en": t.get("name_en", t.get("slug")),
                "subtopics": cat_subtopics
            })

        # 1. विषय का सम्पूर्ण बंडल सुरक्षित करें
        bundle_file = os.path.join(DIST_DIR, f"bundle_{sub_id}.json")
        with open(bundle_file, "w", encoding="utf-8") as bf:
            json.dump(subject_bundle, bf, ensure_ascii=False)

        # 2. कैटलॉग में विषय की संरचना जोड़ें
        master_catalog["subjects"].append({
            "id": sub_id,
            "name_en": sub_meta.get("subject", {}).get("name_en"),
            "name_hi": sub_meta.get("subject", {}).get("name_hi"),
            "bundle_url": f"dist_assets/bundle_{sub_id}.json",
            "topics": catalog_topics
        })
        print(f"  [✓] Bundled {sub_id} -> {bundle_file}")

    # 3. मास्टर कैटलॉग सुरक्षित करें
    cat_file = os.path.join(DIST_DIR, "master_catalog.json")
    with open(cat_file, "w", encoding="utf-8") as cf:
        json.dump(master_catalog, cf, ensure_ascii=False)
    print(f"\n[SUCCESS] Master Catalog Created -> {cat_file}")

if __name__ == "__main__":
    build_distribution()
