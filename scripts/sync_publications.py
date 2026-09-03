#!/usr/bin/env python3
"""
sync_publications.py

Reads ONE database (PIRL-Publications-Database.csv) and produces ONE output
file (publications-data.js) that both the homepage's featured section and
the all-publications page load via <script src="publications-data.js">.

Database columns (you only ever need to hand-maintain doi/url/theme/role/
note/featured -- `title` is written back into the CSV by this script on
every run, purely so the file is readable by a human scanning rows; it
is not read back in as input):
    doi       -- preferred identifier
    title     -- auto-filled/refreshed by this script after each successful
                 fetch, so a row is identifiable at a glance without having
                 to decode its DOI. Left untouched for a row whose fetch
                 fails this run (see the CrossRef-pending gotcha below).
    url       -- fallback if no DOI exists yet (uses citation_* meta tags)
    theme     -- prevention | neuro | tbi | other
    note      -- plain-language "why it matters" -- ONLY used if featured=yes
    featured  -- yes/no -- whether this paper appears in the homepage's
                 curated 3-pillar section (all papers always appear on the
                 all-publications page regardless of this flag)

    student_first_author -- yes/no -- DISPLAYS a "Student First Author" tag.
                 Always an explicit human call, never inferred.
    student_coauthor     -- yes/no -- DISPLAYS a "Student Coauthor" tag. A
                 paper can be yes on BOTH student columns at once (one
                 student led it, a different one also contributed) and both
                 tags then show. These two are the ONLY columns that produce
                 a visible tag on the site.

    my_first_author  -- yes/no -- was Dr. Shen the first author
    my_senior_author -- yes/no -- was Dr. Shen the senior/last author
    my_pi            -- yes/no -- did he lead/fund the study as PI
                 (independent of byline position, so it can be yes
                 alongside my_first_author OR my_senior_author)
    my_collaborator  -- yes/no -- a middle-author contribution
    my_consortium    -- yes/no -- large multi-author consortium paper (GBD)

    None of the five my_* columns ever render as a visible tag -- they only
    feed the search box, so typing "PI" or "first author" still surfaces
    the right papers. build_role_text() assembles the searchable phrase
    from whichever boxes are checked, so that text is never hand-typed and
    can't drift out of sync the way a free-text field could.

Everything else -- authors, journal, volume/issue/pages, and the full
APA 7 reference string -- is generated automatically from CrossRef (for
DOIs) or citation_* meta tags (for URLs) and written only into the JS
output, not back into the CSV.

Usage:
    python3 sync_publications.py PIRL-Publications-Database.csv publications-data.js

Requires: requests, beautifulsoup4, lxml
Network: needs real internet access (CrossRef + publisher sites). Won't work
from a sandboxed environment without egress to api.crossref.org and journal
domains -- run this via Claude Code on your machine or a GitHub Action, not
inside a locked-down sandbox.
"""

import csv
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

CROSSREF_API = "https://api.crossref.org/works/{doi}"
# CrossRef's "polite pool" gives more reliable rate limits if you identify
# yourself with a mailto -- swap in the lab's contact address.
USER_AGENT = "PIRL-publications-sync/1.0 (mailto:jiabin_shen@uml.edu)"

# Words that stay lowercase in APA sentence-case titles unless first/after-colon.
_MINOR_WORDS = {"a","an","the","and","but","or","nor","for","so","yet",
                "as","at","by","in","into","of","off","on","onto","per",
                "to","up","via","with","from","vs","vs."}

# Proper nouns the ALL-CAPS heuristic can't catch (it only preserves acronyms
# like ADHD/TBI/VR that were already all-caps in the source). Add names here
# as you notice the sync mis-lowercase them -- e.g. place names, program
# names, person names that appear inside a title.
_PROTECTED_WORDS = {
    "China", "Manchester", "Ohio", "Alabama", "Massachusetts", "Lowell",
    "Poland", "Chinese",
}
_PROTECTED_LOOKUP = {w.lower(): w for w in _PROTECTED_WORDS}

# Multi-word proper-noun phrases the word-by-word protected list can't express
# (e.g. named research initiatives, program names). Applied case-insensitively
# as a whole-phrase fixup after sentence_case() runs.
_PROTECTED_PHRASES = [
    "Global Burden of Disease Study",
    "Otto the Auto",
]


def apply_protected_phrases(title):
    for phrase in _PROTECTED_PHRASES:
        title = re.sub(re.escape(phrase), phrase, title, flags=re.IGNORECASE)
    return title


def clean_title(raw_title):
    """Collapse embedded whitespace/newlines and drop a trailing period some
    publishers include in their title metadata (sentence_case()/build_apa()
    already add the reference-list period, so a leftover one here doubles up)."""
    title = " ".join((raw_title or "").split())
    return title.rstrip(".")


def format_authors(people):
    """'Last, F. M., Last, F., & Last, F.' -- no bold, plain APA style."""
    parts = []
    for family, given in people:
        initials = "".join(f"{p[0]}." for p in given.split() if p)
        parts.append(f"{family}, {initials}" if initials else family)
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) <= 20:
        return ", ".join(parts[:-1]) + ", & " + parts[-1]
    # APA 7: 21+ authors -> first 19, ellipsis, last author
    return ", ".join(parts[:19]) + ", ... " + parts[-1]


def sentence_case(title):
    """Best-effort APA sentence case: capitalize only the first word, the
    first word after a colon, words that were ALL CAPS in the source
    (treated as acronyms, e.g. ADHD, TBI, VR, DBQ), and anything in
    _PROTECTED_WORDS (proper nouns the ALL-CAPS check can't catch). This is
    still a heuristic -- always spot-check titles after syncing, and add
    any newly-noticed proper nouns to _PROTECTED_WORDS above."""
    words = title.split(" ")
    out = []
    capitalize_next = True
    for w in words:
        prefix = re.match(r"^\W*", w).group()
        core = re.match(r"^\W*(.*?)\W*$", w).group(1)
        suffix = w[len(prefix) + len(core):]
        hyphen_acronym = re.match(r"^([A-Z]{2,})(-.+)$", core)
        plural_acronym = re.match(r"^[A-Z]{2,}[a-z]+$", core)
        if core.isupper() and len(core) > 1:
            out.append(w)  # preserve acronym as-is
        elif hyphen_acronym:
            # e.g. "VR-based" -- the ALL-CAPS check misses this since the
            # word as a whole isn't uppercase, only the part before the hyphen.
            out.append(prefix + hyphen_acronym.group(1) + hyphen_acronym.group(2).lower() + suffix)
        elif plural_acronym:
            out.append(w)  # e.g. "DALYs" -- an acronym with a lowercase plural suffix
        elif core.lower() in _PROTECTED_LOOKUP:
            out.append(prefix + _PROTECTED_LOOKUP[core.lower()] + suffix)
        elif capitalize_next:
            fixed = core[:1].upper() + core[1:].lower() if core else core
            out.append(prefix + fixed + suffix)
        else:
            out.append(prefix + core.lower() + suffix)
        capitalize_next = w.endswith(":")
    result = " ".join(out)
    if result:
        result = result[0].upper() + result[1:]
    return result


def year_from_crossref(msg):
    for key in ("published-print", "published-online", "issued", "created"):
        date_parts = msg.get(key, {}).get("date-parts")
        if date_parts and date_parts[0] and date_parts[0][0]:
            return date_parts[0][0]
    return None


def build_apa(authors_str, year, title, journal, volume, issue, page, doi, in_press=False):
    year_part = "in press" if in_press else str(year)
    ref = f"{authors_str} ({year_part}). {title}. "
    if journal:
        ref += f"<em>{journal}</em>"
    if in_press:
        ref += ". Advance online publication."
    elif volume:
        ref += f", <em>{volume}</em>"
        if issue:
            ref += f"({issue})"
        if page:
            ref += f", {page}"
        ref += "."
    elif page:
        ref += f", Article {page}."
    else:
        ref += "."
    if doi:
        ref += f' <a href="https://doi.org/{doi}" target="_blank" rel="noopener">https://doi.org/{doi}</a>'
    return ref


def fetch_crossref(doi):
    resp = requests.get(CROSSREF_API.format(doi=doi),
                         headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()
    msg = resp.json()["message"]

    people = [(a.get("family", "").strip(), a.get("given", "").strip())
              for a in msg.get("author", []) if a.get("family")]
    title = apply_protected_phrases(sentence_case(clean_title((msg.get("title") or [""])[0])))
    journal = (msg.get("container-title") or [""])[0]
    year = year_from_crossref(msg)
    volume = msg.get("volume")
    issue = msg.get("issue")
    page = msg.get("page") or (msg.get("article-number"))

    return {
        "title": title, "journal": journal, "year": year,
        "volume": volume, "issue": issue, "page": page,
        "doi": doi, "authors": format_authors(people),
    }


def fetch_citation_meta_tags(url):
    """Fallback for entries with a URL but no DOI yet. Reads the same
    citation_* Highwire meta tags Zotero's browser connector reads."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    def meta(name):
        return [t.get("content", "").strip()
                for t in soup.find_all("meta", attrs={"name": name})
                if t.get("content")]

    title = apply_protected_phrases(sentence_case(clean_title((meta("citation_title") or [""])[0])))
    journal = (meta("citation_journal_title") or [""])[0]
    doi = (meta("citation_doi") or [None])[0]
    date = (meta("citation_publication_date") or meta("citation_online_date") or [""])[0]
    year = None
    m = re.search(r"\d{4}", date)
    if m:
        year = int(m.group())

    people = []
    for a in meta("citation_author"):
        if "," in a:
            family, given = [p.strip() for p in a.split(",", 1)]
        else:
            bits = a.split()
            family, given = (bits[-1], " ".join(bits[:-1])) if len(bits) > 1 else (a, "")
        people.append((family, given))

    return {
        "title": title, "journal": journal, "year": year,
        "volume": (meta("citation_volume") or [None])[0],
        "issue": (meta("citation_issue") or [None])[0],
        "page": (meta("citation_firstpage") or [None])[0],
        "doi": doi, "authors": format_authors(people),
    }


def build_role_text(my_first_author, my_senior_author, my_pi, my_collaborator, my_consortium):
    """Auto-generate the search-only role phrase from checkbox columns, so
    nobody ever hand-types this text (and it can't drift or be misspelled)."""
    parts = []
    if my_first_author:
        parts.append("First author")
    if my_senior_author:
        parts.append("Senior author")
    if my_collaborator:
        parts.append("Collaborator")
    if my_consortium:
        parts.append("Consortium collaborator")
    if my_pi:
        parts.append("PI")
    return ", ".join(parts)


def sync(csv_path, out_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    papers, problems = [], []

    for i, row in enumerate(rows, start=1):
        def flag(col):
            return (row.get(col) or "").strip().lower() in ("yes", "true", "1")

        doi = (row.get("doi") or "").strip()
        url = (row.get("url") or "").strip()
        theme = (row.get("theme") or "other").strip()
        note = (row.get("note") or "").strip() or None
        featured = flag("featured")
        student_first_author = flag("student_first_author")
        student_coauthor = flag("student_coauthor")
        role = build_role_text(flag("my_first_author"), flag("my_senior_author"),
                               flag("my_pi"), flag("my_collaborator"), flag("my_consortium"))
        in_press = not doi and bool(url)

        try:
            meta = fetch_crossref(doi) if doi else fetch_citation_meta_tags(url) if url else None
            if meta is None:
                problems.append(f"Row {i}: no DOI or URL provided, skipped.")
                continue
        except Exception as e:
            problems.append(f"Row {i} ({doi or url}): fetch failed ({e}).")
            continue

        if not meta.get("title"):
            problems.append(f"Row {i} ({doi or url}): no title found, needs manual review.")
            continue

        apa = build_apa(meta["authors"], meta["year"], meta["title"], meta["journal"],
                         meta["volume"], meta["issue"], meta["page"], meta["doi"], in_press)

        row["title"] = meta["title"]  # write back so the CSV stays human-scannable

        papers.append({
            "id": i,
            "year": meta["year"] or 2100,   # sorts undated/in-press entries last
            "theme": theme,
            "role": role,   # derived from the my_* checkboxes; search only, never rendered
            "apa": apa,
            "featured": featured,
            "note": note if featured else None,   # only featured papers carry a "why it matters" note
            "studentFirstAuthor": student_first_author,   # explicit human call, not inferred
            "studentCoauthor": student_coauthor,           # explicit human call, not inferred
        })
        time.sleep(0.2)  # stay polite to CrossRef / publisher servers

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by sync_publications.py -- do not hand-edit.\n")
        f.write("// Loaded by BOTH index.html (featured:true only) and all-publications.html (everything).\n")
        f.write("const papers = ")
        f.write(json.dumps(papers, indent=2, ensure_ascii=False))
        f.write(";\n")

    csv_fieldnames = ["doi", "title", "url", "theme", "note", "featured",
                      "student_first_author", "student_coauthor",
                      "my_first_author", "my_senior_author", "my_pi",
                      "my_collaborator", "my_consortium"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") or "" for k in csv_fieldnames})

    featured_count = sum(1 for p in papers if p["featured"])
    print(f"Wrote {len(papers)} publications to {out_path} ({featured_count} featured)")
    if problems:
        print(f"\n{len(problems)} row(s) need attention:")
        for p in problems:
            print(f"  - {p}")
    print("\nReminder: sentence_case() is a heuristic -- spot-check titles for "
          "proper nouns (place names, program names) that may need manual capitalization fixes.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    sync(sys.argv[1], sys.argv[2])
