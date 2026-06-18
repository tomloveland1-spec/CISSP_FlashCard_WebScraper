#!/usr/bin/env python3
"""Join classifications with cards; emit per-chapter Quizlet txt, Review bucket,
and master tracking doc (CSV + markdown)."""
import csv, os, collections

BASE = os.path.dirname(os.path.abspath(__file__))         # output/classifications
OUT = os.path.dirname(BASE)                               # output
BYCH = os.path.join(OUT, "by_chapter")
os.makedirs(BYCH, exist_ok=True)

CH_TITLES = {
    1: "Security Governance Through Principles and Policies",
    2: "Personnel Security and Risk Management Concepts",
    3: "Business Continuity Planning",
    4: "Laws, Regulations, and Compliance",
    5: "Protecting Security of Assets",
    6: "Cryptography and Symmetric Key Algorithms",
    7: "PKI and Cryptographic Applications",
    8: "Principles of Security Models, Design, and Capabilities",
    9: "Security Vulnerabilities, Threats, and Countermeasures",
    10: "Physical Security Requirements",
    11: "Secure Network Architecture and Components",
    12: "Secure Communications and Network Attacks",
    13: "Managing Identity and Authentication",
    14: "Controlling and Monitoring Access",
    15: "Security Assessment and Testing",
    16: "Managing Security Operations",
    17: "Preventing and Responding to Incidents",
    18: "Disaster Recovery Planning",
    19: "Investigations and Ethics",
    20: "Software Development Security",
    21: "Malicious Code and Application Attacks",
}
DOMAINS = {
    1: ("D1", "Security and Risk Management"),
    2: ("D2", "Asset Security"),
    3: ("D3", "Security Architecture and Engineering"),
    4: ("D4", "Communication and Network Security"),
    5: ("D5", "Identity and Access Management"),
    6: ("D6", "Security Assessment and Testing"),
    7: ("D7", "Security Operations"),
    8: ("D8", "Software Development Security"),
}
def domain_of(ch):
    if ch <= 4: return 1
    if ch == 5: return 2
    if ch <= 10: return 3
    if ch <= 12: return 4
    if ch <= 14: return 5
    if ch == 15: return 6
    if ch <= 19: return 7
    return 8

# --- load cards (lineno -> (term, definition)) ---
cards = {}
with open(os.path.join(BASE, "numbered_all.tsv"), encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        parts = line.split("\t", 2)
        ln = int(parts[0])
        term = parts[1] if len(parts) > 1 else ""
        defn = parts[2] if len(parts) > 2 else ""
        cards[ln] = (term, defn)

# --- load classifications ---
cls = {}
with open(os.path.join(BASE, "all_classifications.tsv"), encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if not line: continue
        p = line.split("\t", 3)
        ln = int(p[0]); ch = int(p[1]); conf = p[2]
        reason = p[3] if len(p) > 3 else ""
        cls[ln] = (ch, conf, reason)

assert set(cards) == set(cls), "card/classification mismatch"

def sanitize(t):
    return t.replace(",", "").replace("/", "-").replace(" ", "_")

# --- per-chapter Quizlet files (HIGH + MEDIUM) and Review (LOW) ---
ch_cards = collections.defaultdict(list)   # ch -> list of (term, defn)
review = []                                # list of (ln, ch, reason, term, defn): originally LOW, now placed
for ln in sorted(cards):
    ch, conf, reason = cls[ln]
    term, defn = cards[ln]
    ch_cards[ch].append((term, defn))      # every card placed in its best-guess chapter
    if conf == "LOW":
        review.append((ln, ch, reason, term, defn))

written = []
for ch in range(1, 22):
    rows = ch_cards.get(ch, [])
    if not rows:
        continue
    fn = "Chapter_%02d_%s.txt" % (ch, sanitize(CH_TITLES[ch]))
    with open(os.path.join(BYCH, fn), "w", encoding="utf-8", newline="") as f:
        for term, defn in rows:
            f.write("%s\t%s\n" % (term, defn))
    written.append((ch, fn, len(rows)))

# Every card (incl. the originally-low-confidence ones) is placed in its best-guess
# chapter above. Per-card confidence is preserved in the master CSV for re-checking.

# --- master tracking CSV ---
csv_fn = os.path.join(OUT, "flashcard_chapter_index.csv")
with open(csv_fn, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["card_no", "term", "definition", "sg_chapter", "sg_chapter_title",
                "domain", "domain_title", "confidence", "placed_in", "reason"])
    for ln in sorted(cards):
        ch, conf, reason = cls[ln]
        term, defn = cards[ln]
        d = domain_of(ch)
        placed = "Ch %d" % ch
        w.writerow([ln, term, defn, ch, CH_TITLES[ch],
                    DOMAINS[d][0], DOMAINS[d][1], conf, placed, reason])

# --- master tracking markdown summary ---
md_fn = os.path.join(OUT, "flashcard_chapter_index.md")
ch_counts = collections.Counter(cls[ln][0] for ln in cls)
dom_counts = collections.Counter(domain_of(cls[ln][0]) for ln in cls)
conf_counts = collections.Counter(cls[ln][1] for ln in cls)
with open(md_fn, "w", encoding="utf-8") as f:
    f.write("# CISSP Flashcard → Chapter / Domain Index\n\n")
    f.write("Total cards: **%d**. Confidence: HIGH **%d**, MEDIUM **%d**, LOW **%d**.\n\n"
            % (len(cards), conf_counts['HIGH'], conf_counts['MEDIUM'], conf_counts['LOW']))
    f.write("Every card is placed in its best-guess chapter. Per-chapter Quizlet files "
            "are in `output/by_chapter/`. Full per-card detail (incl. confidence, so the "
            "%d low-confidence calls can be re-checked) is in `flashcard_chapter_index.csv`."
            "\n\n" % conf_counts['LOW'])
    f.write("## Cards per chapter (Study Guide)\n\n")
    f.write("| Ch | Title | Domain | Cards |\n|----|-------|--------|------|\n")
    for ch in range(1, 22):
        d = domain_of(ch)
        f.write("| %d | %s | %s | %d |\n"
                % (ch, CH_TITLES[ch], DOMAINS[d][0], ch_counts.get(ch, 0)))
    f.write("\n## Cards per domain\n\n| Domain | Title | Cards |\n|--------|-------|------|\n")
    for d in range(1, 9):
        f.write("| %s | %s | %d |\n" % (DOMAINS[d][0], DOMAINS[d][1], dom_counts.get(d, 0)))

print("Per-chapter files written:")
for ch, fn, n in written:
    print("  %s  (%d cards)" % (fn, n))
print("Low-confidence cards placed in best-guess chapter: %d (see CSV confidence col)" % len(review))
print("Master CSV: %s" % os.path.basename(csv_fn))
print("Master MD : %s" % os.path.basename(md_fn))
