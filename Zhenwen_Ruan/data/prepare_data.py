"""Rebuild the A2 handoff from the two original A1 sources. Python standard library only."""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


def normalize(value):
    return re.sub(r"\s+", " ", value.strip().lower())


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("postings", type=Path)
    parser.add_argument("skills_zip", type=Path)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    candidates = {}
    total = 0
    duplicate_candidates = 0
    with args.postings.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        source_fields = reader.fieldnames
        for row in reader:
            total += 1
            if re.search(r"\bbusiness analyst\b", normalize(row["job_title"])):
                if row["job_link"] in candidates:
                    duplicate_candidates += 1
                    raise ValueError("Duplicate candidate job_link requires review")
                candidates[row["job_link"]] = row
    aliases = {
        "communication skills": "communication",
        "problem-solving": "problem solving",
        "problemsolving": "problem solving",
        "problem solving skills": "problem solving",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "microsoft power bi": "power bi",
        "powerbi": "power bi",
    }
    skills_rows = 0
    matched = {}
    with zipfile.ZipFile(args.skills_zip) as archive:
        with archive.open("job_skills.csv") as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig")):
                skills_rows += 1
                key = row["job_link"]
                if key in candidates:
                    if key in matched:
                        raise ValueError("Duplicate skills key requires review")
                    matched[key] = row["job_skills"] or ""
    cohort = []
    long_rows = []
    token_map = Counter()
    exclusion_rows = []
    frequency = Counter()
    baseline_frequency = Counter()
    for key, row in candidates.items():
        raw = matched.get(key, "")
        tokens = {normalize(token) for token in raw.split(",") if normalize(token)}
        if "business analysis" not in tokens:
            exclusion_rows.append({"job_link": key, "job_title": row["job_title"], "reason": "No exact business analysis skill" if raw else "Missing or empty skills"})
            continue
        skills = sorted({aliases.get(token, token) for token in tokens})
        for token in tokens:
            token_map[(token, aliases.get(token, token))] += 1
        baseline_frequency.update(tokens)
        frequency.update(skills)
        cohort.append({**row, "job_skills_raw": raw, "skills_normalized_json": json.dumps(skills, ensure_ascii=False), "skill_count": len(skills)})
        long_rows.extend({"job_link": key, "skill": skill} for skill in skills)
    cohort.sort(key=lambda row: row["job_link"])
    long_rows.sort(key=lambda row: (row["job_link"], row["skill"]))
    n = len(cohort)
    assert n > 0
    write_csv(args.out / "ba_jobs_clean.csv", source_fields + ["job_skills_raw", "skills_normalized_json", "skill_count"], cohort)
    write_csv(args.out / "ba_skills_long.csv", ["job_link", "skill"], long_rows)
    vocabulary = sorted(skill for skill in frequency if skill != "business analysis")
    matrix = []
    for row in cohort:
        present = set(json.loads(row["skills_normalized_json"]))
        matrix.append({"job_link": row["job_link"], **{skill: int(skill in present) for skill in vocabulary}})
    write_csv(args.out / "ba_skill_matrix.csv", ["job_link"] + vocabulary, matrix)
    write_csv(args.out / "skill_frequency.csv", ["skill", "postings", "proportion", "is_cohort_defining"], [{"skill": skill, "postings": count, "proportion": count/n, "is_cohort_defining": int(skill == "business analysis")} for skill, count in frequency.most_common()])
    write_csv(args.out / "skill_normalization_audit.csv", ["original_normalized_token", "mapped_skill", "postings"], [{"original_normalized_token": token, "mapped_skill": mapped, "postings": count} for (token, mapped), count in sorted(token_map.items())])
    write_csv(args.out / "excluded_title_candidates.csv", ["job_link", "job_title", "reason"], exclusion_rows)
    for field in ["company", "job_location", "job_title", "first_seen"]:
        counts = Counter(row[field] for row in cohort)
        write_csv(args.out / (field + "_counts.csv"), [field, "postings"], [{field: value, "postings": count} for value, count in counts.most_common()])
    audit = {
        "source_posting_rows": total,
        "source_skill_rows": skills_rows,
        "title_candidates": len(candidates),
        "candidate_duplicate_keys": duplicate_candidates,
        "candidates_with_skill_row": len(matched),
        "cohort_records": n,
        "expected_A1_cohort": 1929,
        "matches_A1_cohort": n == 1929,
        "first_seen_min": min(row["first_seen"] for row in cohort),
        "first_seen_max": max(row["first_seen"] for row in cohort),
        "distinct_first_seen_values": len({row["first_seen"] for row in cohort}),
        "unique_skills_including_defining_skill": len(frequency),
        "long_table_rows": len(long_rows),
        "matrix_rows": n,
        "matrix_skill_columns": len(vocabulary),
        "missing_by_source_field_in_cohort": {field: sum(not row[field].strip() for row in cohort) for field in source_fields},
        "aliases": aliases,
        "source_sha256": {},
    }
    for path in [args.postings, args.skills_zip]:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024*1024), b""):
                digest.update(chunk)
        audit["source_sha256"][path.name] = digest.hexdigest()
    (args.out / "quality_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
