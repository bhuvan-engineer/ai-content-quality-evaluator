import re

FILLER_PHRASES = [
    "in today's fast-paced world",
    "it is important to note",
    "delve into",
    "in conclusion",
    "without further ado",
    "game changer",
    "unlock the power",
    "revolutionize"
]

def evaluate_content(text, content_type="Email", expected_length="Medium"):
    cleaned = (text or "").strip()
    words = re.findall(r"\b[\w'-]+\b", cleaned, flags=re.UNICODE)
    word_count = len(words)
    lower = cleaned.lower()
    filler_matches = [phrase for phrase in FILLER_PHRASES if phrase in lower]
    checks = []

    if expected_length == "Short":
        passed = 20 <= word_count <= 140
        detail = f"{word_count} words; expected approximately 20–140."
    elif expected_length == "Long":
        passed = word_count >= 150
        detail = f"{word_count} words; long outputs are usually 150+ words."
    else:
        passed = 70 <= word_count <= 260
        detail = f"{word_count} words; medium outputs are usually 70–260."
    checks.append({"label": "Length range", "passed": passed, "detail": detail})

    if content_type == "Email":
        has_greeting = bool(re.search(r"(?i)\b(hi|hello|dear|नमस्ते|प्रिय|आदरणीय)\b", cleaned))
        has_closing = bool(re.search(r"(?i)\b(regards|sincerely|thanks|thank you|धन्यवाद|सादर|शुभकामनाएँ)\b", cleaned))
        structural = has_greeting and has_closing
        checks.append({
            "label": "Email structure",
            "passed": structural,
            "detail": "Greeting and closing detected." if structural else "Could not detect both a greeting and a closing; review manually."
        })
    elif content_type == "Blog introduction":
        structural = word_count >= 35 and len(re.findall(r"[.!?।]", cleaned)) >= 2
        checks.append({
            "label": "Blog introduction structure",
            "passed": structural,
            "detail": "Has a basic paragraph/sentence structure." if structural else "May be too short or lack sentence structure."
        })
    else:
        structural = word_count >= 10
        checks.append({
            "label": "Social post structure",
            "passed": structural,
            "detail": "Has enough text for a basic post." if structural else "Post may be too short; review intended platform."
        })

    checks.append({
        "label": "Filler phrase scan",
        "passed": len(filler_matches) == 0,
        "detail": "No listed filler phrases detected." if not filler_matches else "Detected: " + ", ".join(filler_matches)
    })
    checks.append({
        "label": "Manual factual review",
        "passed": False,
        "detail": "Not automated: verify facts, dates, names, claims, and cultural context before publishing."
    })

    passed_count = sum(1 for c in checks if c["passed"])
    label = "Good signal" if passed_count >= len(checks) - 1 else "Needs review"
    return {
        "word_count": word_count,
        "filler_count": len(filler_matches),
        "filler_matches": filler_matches,
        "structure_label": label,
        "checks": checks
    }

def compare_outputs(outputs, content_type="Email", expected_length="Medium"):
    return {language: evaluate_content(output, content_type, expected_length) for language, output in outputs.items()}
