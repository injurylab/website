# CLAUDE.md — Pediatric Injury Research Lab website (injurylab.org)

This file is read automatically by Claude Code at the start of a session in
this repo. It exists so a fresh session has full context without the owner
(Paul, on behalf of Dr. Jiabin Shen) having to re-explain the project.

## What this repo is

A single-page static website for the **Pediatric Injury Research Lab**,
directed by **Jiabin Shen, PhD**, Associate Professor of Psychology at
UMass Lowell. Hosted on **GitHub Pages**, served at the custom domain
**injurylab.org** (DNS: A records point to GitHub Pages IPs; a `CNAME` file
in the repo root contains `injurylab.org`).

There is no build step, no framework, no package.json, no dependencies.
The entire site is one file: **`index.html`** — plain HTML + inline
`<style>` + inline `<script>`. Two supporting files sit alongside it at the
repo root: **`robots.txt`** and **`sitemap.xml`** (basic SEO). Do not
introduce a build tool, bundler, or framework unless explicitly asked —
simplicity here is intentional, since the site owner is not a developer
and edits files directly through the GitHub web UI when Claude isn't
involved.

## How to "test" changes

Since there's no build step, testing means: open `index.html` directly in
a browser (`open index.html` on Mac, or a simple local server like
`python3 -m http.server` if relative asset paths need to resolve
correctly), and visually check the change. There is no test suite to run.

**Gotcha:** opening `index.html` directly via `file://` can silently fail
to load the *external* `<script src="data/publications-data.js">` that
drives the Publications section, while everything else on the page
(Team, News, Student Engagement) still renders fine, since those are
driven by inline `<script>` blocks with data baked directly into the
HTML. If Publications looks empty while nothing else does, this is
almost certainly the cause, not a real bug — serve the directory instead
of opening the file: `python3 -m http.server 8000`, then open
`http://localhost:8000/index.html`.

## Design system (do not deviate without being asked)

- **Colors:** navy `#0D1F3C`, steel `#1B3A6B`, sky blue `#2E6CA8`, amber
  accent `#E8B84B`, sage green `#5B8A6F`, sand background `#F7F4EE`.
- **Fonts:** `DM Serif Display` for headings, `Inter` for body text,
  `JetBrains Mono` for small labels/eyebrows/tags. All loaded via Google
  Fonts `<link>` in `<head>`.
- **Layout:** single scrolling page, sections in this order: Nav → Hero →
  Research Pillars (3 cards) → Student Engagement (tabbed) → Publications →
  Team ("Meet the Lab") → Join Us (grad student recruiting) → News →
  Contact/Footer.
- All custom CSS classes are short/abbreviated (e.g. `.hin`, `.rc`, `.tgd`,
  `.itg-card`) to keep the single file compact. Follow the existing naming
  convention rather than introducing verbose class names.

## The "Student Engagement" section — structure and update cadence

Between Research Pillars and Publications sits a tabbed section
(`aria-label="Student engagement"`) that replaced an earlier PI-facing
"Impact Numbers" stats strip (funding total, publication count, years
active). That framing was deliberately dropped in favor of student-facing
training/engagement stats — don't reintroduce total-funding or
total-publications figures here.

It renders from a JS object `IMPACT_DATA` (search for `const IMPACT_DATA`
in the file), one entry per tab: `mentor`, `pubs`, `conf`, `comm`. Each
entry has `tabLabel`, `tag`, an optional `number`/`numLabel`/`sub`
(Community Engagement intentionally omits these — no clean single number
exists for it), `overview`, `examples` (2 short fact strings), and a
`source` field that is never rendered — it exists only so a future update
can see where a number/example came from.

**Update cadence:** refresh whenever Dr. Shen's CV is updated (annual).
The full re-verification method — which CV sections map to which fields,
and the specific pitfall that the CV's asterisk-marks-student-coauthor
convention includes collaborators' students (e.g. Dr. Schwebel's UAB
mentees), not just this lab's own mentees, so counts must be filtered
against the named Student Mentoring roster first — is documented in the
HTML comment directly above `const IMPACT_DATA` in `index.html`. Read
that comment before updating rather than re-deriving the method here.

**Convention:** any new full-bleed section like this needs both `sec`
(for the standard `padding:5rem 2rem`) and its own background class
(`imp` here) on the `<section>` tag — `.con` alone only centers content,
it adds no padding of its own.

## The "Meet the Lab" team section — important structure

This section (`id="team"`) is an **interactive JS-rendered grid**, not
static HTML. It renders from a JavaScript object called `ITG_DATA` (search
for `const ITG_DATA` in the file) containing three arrays: `current`,
`collab`, `alumni`. Each person is an object with `id`, `name`, `role`,
`initials`, `color`, `focus` (shown on hover-flip), `bio` (shown in a
click-to-open modal), and `links` (array of `{label, url}`).

**Known past bug:** a stray escaped apostrophe (`\\'`) inside a `bio:'...'`
string once broke the *entire* `<script>` block silently, causing all
three grids to render empty with no visible error except a browser console
"Uncaught Error: Script error." **Always validate JS syntax after editing
`ITG_DATA`** — try `node --check` on the extracted script contents if
`node` is available; if not (this dev environment currently has no `node`
on `PATH` — `command -v node` returns nothing), instead load `index.html`
in a browser and confirm both that the console shows no errors and that
the team grids actually render populated cards, not empty. At minimum,
carefully check every apostrophe inside single-quoted strings is either
avoided (rephrase) or properly escaped.

**Photos:** every person currently displays as colored initials, not real
photos. Real photo URLs from Wix and the UML site kept failing (hotlink
protection / broken paths), so the deliberate decision was to use initials
as a reliable fallback. If asked to add real photos: the correct approach
is to have the user upload image files into an `images/` folder in this
repo, then reference them with a relative path like `images/name.jpg` —
never an external hotlinked URL from Wix, UML, Twitter/X, etc., since
those have repeatedly broken.

**The team roster is also maintained in a separate spreadsheet** (an
`.xlsx` workbook with tabs: "Read Me First", "Team Members", "Dropdown
Options", "Photo Instructions") that the non-technical site owner edits
directly. If the owner provides an updated spreadsheet, read it and
regenerate the `ITG_DATA` object in `index.html` to match it exactly —
this is the established workflow for team updates going forward.

## Content rules — do not fabricate

This is a real academic's professional site. Every fact — publication
counts, funding figures, grant numbers, conference names, degrees,
collaborator names — has been sourced from the site owner's actual CV, the
UML faculty profile, Google Scholar, or lab-provided screenshots (e.g. of
the lab's official X/Twitter account posts about conference presentations).

**Never invent or guess:**
- Publication counts, funding totals, or dates — ask the user or search
  for a real source if unsure.
- ORCID IDs — extensive searching found no public ORCID for Dr. Shen or
  any student; no ORCID link exists anywhere on the site. Do not add a
  placeholder or guessed ORCID URL.
- Collaborator names for the "Research Collaborators" section — it is
  intentionally empty with a placeholder note ("Collaborator profiles are
  added as active projects are confirmed") rather than populated with
  guesses.
- Photos of people who have no confirmed, working image URL.

If a request would require fabricating a fact to complete it, stop and ask
the user for the real information instead.

## Things explicitly removed at the owner's request — do not re-add

- **ResearchGate** link/icon (removed from Contact section and site-wide).
- **Twitter/X** link/icon for Dr. Shen (removed; note the lab's own
  *official* X account, @UMLInjuryLab, was used as a source for team
  member conference info via screenshots, but is not linked from the
  site itself).
- **Nationwide Children's Hospital** — removed from every mention
  site-wide (funders list, collaborator text, etc.) per explicit request.
- **"Tenured 2025" badge** — removed from the PI's hero photo card and
  team card (tenure is still mentioned in the News section, just not as a
  standalone badge under the photo).
- **The "Participate in our research" box** — removed as a large visual
  section; replaced with a single quiet text link at the bottom of the
  News section pointing to the same REDCap signup URL
  (`https://arcsapps.umassmed.edu/redcap/surveys/?s=HCY83987F3`).
- **The mailto-based "Send a message" contact form** — removed because
  `action="mailto:"` forms are unreliable across browsers/devices; replaced
  with plain icon-links (email, UML profile, Google Scholar).

## SEO setup already in place

- `<title>`, meta `description`, meta `keywords`, Open Graph tags, and a
  `<link rel="canonical">` are all set in `<head>`.
- **JSON-LD structured data** (`<script type="application/ld+json">`) is
  present, describing Dr. Shen as a `Person` and the lab as a
  `ResearchOrganization`, using only confirmed facts (degrees, affiliation,
  contact info, research areas). Validate any edits to this block with a
  JSON parser — a syntax error here won't break the visible page but will
  silently make the structured data useless to search engines.
- `robots.txt` and `sitemap.xml` exist at the repo root, referenced from
  `<head>` and pointing crawlers at the single homepage URL.
- Google Search Console verification is a manual step the owner does
  themselves (pasting a verification meta tag Claude adds on request) —
  not yet fully confirmed as complete as of this writing.

## Deployment

Direct commits to `main` deploy automatically via GitHub Pages (no CI
config needed — this is GitHub's default Pages behavior for a repo with
`index.html` at the root). Confirm important changes render correctly
before pushing, since there is no staging environment — every push to
`main` goes live on injurylab.org within a few minutes.

**Git push authentication in this environment:** this machine authenticates
to GitHub via the `gh` CLI (logged in as `injurylab`), which registers
git's credential helper. But `gh` is installed at `/opt/homebrew/bin/gh`
and is *not* on the default `PATH` in a Claude Code session here — so a
plain `git push` can fail with `fatal: could not read Username for
'https://github.com': Device not configured` even though valid
credentials exist, simply because `gh` isn't reachable to supply them.
If that happens, don't conclude auth isn't set up — run the push with the
path included instead:

    PATH="/opt/homebrew/bin:$PATH" git push origin main

(`/opt/homebrew/bin/gh auth status` confirms login without needing the
PATH change, since it's invoked by full path directly.)

## Team roster spreadsheet — keeping index.html in sync

The team roster shown in the "Meet the Lab" section is maintained by the
site owner in a separate spreadsheet, not edited directly in code. The
spreadsheet lives at:

    data/PIRL-Team-Database.xlsx

**Workflow:** whenever the user says something like "I updated the
spreadsheet," "sync the team section," or similar — even without further
detail — do the following:

1. Read every row of the `Team Members` sheet in that workbook.
2. Compare it against the current `ITG_DATA` object in `index.html`
   (search for `const ITG_DATA`).
3. Regenerate `ITG_DATA` to match the spreadsheet **exactly**:
   - The `Section` column controls which array a person belongs in:
     `current` (for "Current Members") or `alumni` (for "Alumni"). The
     `Status` column is metadata for the owner's own tracking — it does
     NOT control placement in the code. Trust `Section`, not `Status`.
   - `Order` controls the sequence within a section — lower numbers
     first.
   - Map each remaining column directly: `Full Name` → `name`,
     `Role / Title` → `role`, `Current Focus` → `focus`, `Full Bio` →
     `bio`, `Avatar initials` → `initials`.
   - `Photo filename` → the `photo` field, as a relative path:
     `images/<filename>`. **How photos actually get linked to a person:**
     there is no automatic matching — the spreadsheet cell is the *only*
     link between a photo file and a person. Do not scan the `images/`
     folder and guess whose photo is whose based on filename similarity
     to a name; only use the exact filename the user typed into that
     row's "Photo filename" cell.
   - **Before finalizing, check that every non-blank `Photo filename`
     actually exists in the `images/` folder** (e.g. `ls images/`). If a
     spreadsheet row names a file that isn't there, don't silently drop
     it or guess a replacement — leave that person's `photo` field unset
     (so they fall back to initials, which is safe) and flag it clearly
     in your summary: "Row for <name> references images/<file> which
     doesn't exist in the images folder — check the filename or upload
     the photo." The same applies in reverse: if there's a new file in
     `images/` that isn't referenced in any row, don't add it to anyone
     automatically — just note it in the summary so the user can update
     the spreadsheet if they forgot.
   - If a person's Photo filename cell is blank, leave `photo` unset —
     the initials fallback already handles this automatically.
   - The two Link label/URL column pairs → the `links` array
     (`[{label, url}]`); omit any pair that's blank rather than adding an
     empty object.
   - If a person in the spreadsheet has no corresponding entry in
     `ITG_DATA`, add them. If `ITG_DATA` has a person no longer in the
     spreadsheet, remove them. Photo crop position (`pos` field) is a
     display-only tweak that doesn't come from the spreadsheet — leave
     any existing `pos` override on a person untouched unless the user
     separately reports their photo is cropped wrong.
4. **Validate the `<script>` block's JavaScript syntax after editing**
   before considering the task done. Try extracting the script contents
   to a temp file and running `node --check` on it — but don't assume
   `node` is installed; check with `command -v node` first, since it is
   not on `PATH` in this dev environment. If `node` isn't available,
   validate instead by loading `index.html` in a browser (e.g. navigate
   to the local `file://` path, or `open index.html`) and confirming both
   that the console shows no errors and that the team grids actually
   render populated cards, not empty ones. This file has previously
   broken silently — every card on the page rendering empty with no
   visible error beyond a browser console message — because of a single
   bad escaped character inside a bio string. Pay particular attention to
   apostrophes inside single-quoted bio/focus/name strings in the
   spreadsheet data; escape them correctly or rephrase to avoid them.
5. Summarize what changed (people added, removed, or edited; any fields
   that differed) before committing.

If the spreadsheet file can't be found at the expected path, ask the user
directly rather than guessing or skipping the update.

## Keeping this file itself up to date

This file is the persistent memory for this project across Claude Code
sessions — it's read automatically at the start of every session, so
anything durable that isn't written here effectively gets forgotten once
the session ends.

**When something comes up during a session that represents a genuinely
new durable rule, decision, or lesson** — not just a one-off fix specific
to that moment — proactively suggest adding it here before the session
ends, rather than waiting to be asked. Examples of what counts as
"durable" versus "one-off":

- **Durable (add it):** a bug pattern likely to recur (like the
  escaped-apostrophe issue already documented above), a deliberate design
  decision the owner made after trying an alternative (like choosing
  single-select over multi-select filtering), a new database or content
  source being introduced, a tool or credential now configured for this
  project, a fact or convention that future sessions would otherwise have
  to rediscover from scratch.
- **One-off (don't add it):** a specific typo fix, a single content
  update already reflected in the live data files, troubleshooting steps
  for a problem that's now resolved and unlikely to recur in the same
  form.

When proposing an addition, keep it in the same style as the rest of this
file: plain prose explaining the *why*, not just the *what*, written for
a future Claude Code session that has no memory of the conversation where
the decision was made. Show the owner the proposed addition and confirm
before actually writing it to the file, rather than silently editing
this document.

## News database spreadsheet — keeping index.html in sync

The "News & Opportunities" section is driven by a JavaScript array called
`NDB_DATA` (search for `const NDB_DATA` in `index.html`), maintained by the
site owner in a separate spreadsheet, not edited directly in code. The
spreadsheet lives at:

    data/PIRL-News-Database.xlsx

(If this file isn't at that path yet, look for it elsewhere in the repo
root, or ask the user where they saved it — do not guess a path outside
the repo.)

**How the section behaves (context for understanding what you're
syncing):** news items render as a single-open accordion — clicking one
closes whatever was previously expanded. Only the 10 most recent items
show by default (`NDB_PAGE_SIZE`), with a "Show older news" button to
reveal more. Category filter chips ("All" + one per category present in
the data) sit above the list — filtering is **single-select**, like tabs:
clicking a category shows only that category, replacing any previously
selected one (not additive/multi-select — an earlier version of this
feature allowed multiple categories at once with OR logic, but that was
found confusing in practice and was deliberately simplified to
single-select; do not reintroduce multi-select unless the user explicitly
asks for it again). Clicking the already-active category, or clicking
"All", clears the filter. Switching the filter selection always resets
the visible count back to 10. None of this interactive behavior comes
from the spreadsheet — it's fixed logic in the code (`NDB_activeFilter`
holds a single category code or `null` for "All"). The spreadsheet only
supplies the data.

**Workflow:** whenever the user says something like "I updated the news
spreadsheet," "sync the news section," or similar — even without further
detail — do the following:

1. Read every row of the `News Items` sheet in that workbook.
2. Compare it against the current `NDB_DATA` array in `index.html`.
3. Regenerate `NDB_DATA` to match the spreadsheet **exactly**:
   - `Sort Date (YYYY-MM-DD)` → the `sort` field. This is invisible to
     visitors and controls chronological order only. A far-future date
     like `2099-01-01` is the established convention for pinning an
     "Ongoing" item permanently at the top — preserve that pattern for
     any new evergreen/ongoing item rather than inventing a different
     mechanism.
   - `Display Date` → the `date` field (what visitors actually see, e.g.
     "Ongoing," "2023," "May 2026").
   - `Category` → the `cat` field. Must be one of the short internal
     codes already used in the code (`pub`, `pres`, `award`, `grant`,
     `recruit`, `milestone`, `other`) — map the spreadsheet's
     human-readable Category column (Publication/Presentation/Award/
     Grant/Recruiting/Milestone/Other) to these codes using the existing
     `NDB_CAT_LABEL` object in the code as the source of truth for the
     mapping. If the user adds a genuinely new category not in that
     list, add both a new short code and a matching entry in
     `NDB_CAT_LABEL`, and give it a CSS color rule alongside the existing
     `.ndb-cat.pub` / `.ndb-cat.pres` / etc. rules rather than leaving it
     unstyled.
   - `Headline` → the `headline` field.
   - `Details` → the `detail` field.
   - `Link label` + `Link URL` (if both present) → weave them into the
     `detail` field as an inline `<a>` tag (there is no separate `links`
     structure for news items, unlike the team database) — follow the
     existing style of embedded links already in `detail` fields (e.g.
     the "UML Psychology PhD program" link in the recruiting item).
   - If a person in the spreadsheet has no corresponding entry in
     `NDB_DATA`, add them. If `NDB_DATA` has an item no longer in the
     spreadsheet, remove it.
4. **Validate the `<script>` block's JavaScript syntax after editing**
   before considering the task done. Try extracting the script contents
   to a temp file and running `node --check` on it — but don't assume
   `node` is installed; check with `command -v node` first, since it is
   not on `PATH` in this dev environment. If `node` isn't available,
   validate instead by loading `index.html` in a browser (e.g. navigate
   to the local `file://` path, or `open index.html`) and confirming both
   that the console shows no errors and that the news list actually
   renders populated items, not an empty list. This exact file has broken
   silently before — twice — because of unescaped apostrophes inside
   single-quoted string fields (a possessive like "Activity's" or
   "Children's" typed directly into a `'...'`-delimited JS string breaks
   the entire script with no visible error beyond a browser console
   message). When a headline or detail field contains an apostrophe,
   either rephrase to avoid it, or — the safer general fix — use `"..."`
   (double-quoted) JS strings for that field instead of `'...'`, escaping
   any literal double-quotes inside with `\"`. Do not rely on backslash-
   escaping an apostrophe inside a single-quoted string
   (`'Children\'s'`) — this file has a history of that specific pattern
   getting mangled by tooling into a broken double-backslash. Prefer
   switching the quote style over escaping.
5. Summarize what changed (items added, removed, or edited) before
   committing.

If the spreadsheet file can't be found at the expected path, ask the user
directly rather than guessing or skipping the update.
