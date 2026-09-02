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
(Team, News, the engagement tabs inside Join Us) still renders fine,
since those are driven by inline `<script>` blocks with data baked
directly into the HTML. If Publications looks empty while nothing else
does, this is almost certainly the cause, not a real bug — serve the
directory instead
of opening the file: `python3 -m http.server 8000`, then open
`http://localhost:8000/index.html`.

## Design system (do not deviate without being asked)

- **Colors:** navy `#0D1F3C`, steel `#1B3A6B`, sky blue `#2E6CA8`, amber
  accent `#E8B84B`, sage green `#5B8A6F`, sand background `#F7F4EE`.
- **Fonts:** `DM Serif Display` for headings, `Inter` for body text,
  `JetBrains Mono` for small labels/eyebrows/tags. All loaded via Google
  Fonts `<link>` in `<head>`.
- **Layout:** single scrolling page, sections in this order: Nav → Hero →
  Research Pillars (3 cards) → Publications → Team ("Meet the Lab") →
  Join Us (grad student recruiting, including the tabbed student
  engagement content) → News → Contact/Footer.
- All custom CSS classes are short/abbreviated (e.g. `.hin`, `.rc`, `.tgd`,
  `.itg-card`) to keep the single file compact. Follow the existing naming
  convention rather than introducing verbose class names.

## The "Why join our lab?" section — merged structure and update cadence

The `#join` section (between Team and News) now combines two things that
used to live separately: the grad-student-recruiting content (perk cards
+ a "Ready to apply?" CTA box) and a tabbed "Student Engagement" section
that used to sit between Research Pillars and Publications as its own
full-bleed navy section. That standalone section had itself already
replaced an even earlier PI-facing "Impact Numbers" stats strip (funding
total, publication count, years active) — that framing was deliberately
dropped in favor of student-facing training/engagement stats. **Don't
split the tabs back out into their own standalone section, and don't
reintroduce total-funding or total-publications figures here** — both of
those have already been tried and deliberately moved away from.

Inside `#join`, the section now reads top to bottom as a pitch, then
quick perks, then proof, then a clear call to action: the "Why join our
lab?" heading and intro line, then the two perk cards (`.prks`, now a
2-column row, not a stack), then the tabbed evidence card (`.eng-card`,
a navy card, not a full-bleed section), then the "Ready to apply?" CTA
box (`.cb.cb-closing`, centered at a constrained width as the section's
final element, not paired side by side with the perks in a grid
anymore). The tabs render from a JS object `IMPACT_DATA` (search for
`const IMPACT_DATA` in the file, right after the `#join` section
closes), one entry per tab: `mentor`, `pubs`, `conf`, `comm`. Each entry
has `tabLabel`, `tag`, an optional `number`/`numLabel`/`sub` (Community
Engagement intentionally omits these — no clean single number exists for
it), `overview`, `examples` (2 short fact strings), and a `source` field
that is never rendered — it exists only so a future update can see where
a number/example came from.

Because the tabs now back up the "students publish here" and "students
are mentored here" claims with real numbers, the two perk cards that
made the same claims in prose ("Publication opportunities," "Mentored
for success") were removed as redundant when the sections merged — only
"Cutting-edge methods" and "Interdisciplinary network" remain. All perk
cards also lost their emoji icon (the `.pki` div) in the same pass, as a
deliberate simplification — don't reintroduce icons here without being
asked.

**Update cadence:** refresh whenever Dr. Shen's CV is updated (annual).
The full re-verification method — which CV sections map to which fields,
and the specific pitfall that the CV's asterisk-marks-student-coauthor
convention includes collaborators' students (e.g. Dr. Schwebel's UAB
mentees), not just this lab's own mentees, so counts must be filtered
against the named Student Mentoring roster first — is documented in the
HTML comment directly above `const IMPACT_DATA` in `index.html`. Read
that comment before updating rather than re-deriving the method here.

**Convention:** `.eng-card` gives the tabs their navy background and
padding now that they live as a card inside a light `.sec`, not as a
full-bleed section of their own (the old `.imp` background class this
used before the merge no longer exists — don't resurrect it). `.cb-closing`
(`max-width:640px;margin:0 auto`) is what keeps the CTA box readable
instead of stretching edge to edge now that it's not sharing a 2-column
grid with the perks anymore.

**Gotcha: this file's mobile overrides only work if they come after their
base rule in source order.** The single `@media(max-width:760px)` block
(currently sitting right after the `.stps`/`.stxt` rules, at the end of
the JOIN CSS) holds mobile tweaks for several unrelated components
(`.pw-tab`, `.pw-examples`, `.eng-card`, `.prks`) — not because they're
related, but because CSS resolves a tie in specificity by whichever rule
comes *later* in the file, media query or not. When `.prks`'s base rule
briefly lived below this media query during a reorder, its mobile
override was silently ignored (grid stayed 2 columns at every width) even
though the CSS looked correct and no console error appeared — the only
way to catch it was checking `getComputedStyle` at a narrow width. If you
add a new mobile override here, or move a class's base rule around,
confirm in a browser (not just by reading the CSS) that the base rule
still sits earlier in the file than this media query, or move the media
query again rather than assuming order doesn't matter.

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

## Team roster spreadsheet — keeping index.html and team.html in sync

The team roster is maintained by the site owner in a separate spreadsheet,
not edited directly in code. The spreadsheet lives at:

    data/PIRL-Team-Database.xlsx

It now drives **two** places on the site, not one:

- `index.html`'s `ITG_DATA` object (search for `const ITG_DATA`) — the
  "Meet the Lab" flip-card grid on the homepage. This only ever holds a
  *subset* of the roster: full cards need a photo/initials, a focus line,
  and a bio to look right.
- `team.html`'s `TDIR_DATA` array (search for `const TDIR_DATA`) — a
  plain-text directory of **every** row in the spreadsheet, no cards, no
  bios, no photos, for anyone (including the PI). It exists specifically
  so alumni who don't get a homepage card still show up somewhere. It is
  self-contained (its own inline data array, not shared with `ITG_DATA`
  via an external file the way publications data is).

**Columns and what each one controls:**

- `Section` — `Current Members` or `Alumni`. Drives placement in
  `TDIR_DATA` for both pages. The `Status` column is the owner's own
  tracking metadata and does NOT control placement — trust `Section`.
- `Order` — sequence within a group, lower numbers first. It's a single
  counter across the whole sheet (not reset to 1 within every group), so
  don't be surprised when Alumni order numbers aren't contiguous — just
  sort by it within whatever group you're building.
- `Degree Level` and `Department / Program` are two separate columns
  (they used to be one combined `Program (Degree – Department)` field —
  don't reintroduce that combined form). `Degree Level` must be exactly
  `"Doctoral"`, `"Master's"`, or `"Undergraduate"` and is grouping-only:
  it decides which of `team.html`'s three Alumni subheadings a person
  lands in and is never itself displayed. `Department / Program` (e.g.
  `"Mechanical Engineering"`, `"Public Health"`) IS displayed, on
  `team.html` only, never on homepage cards. `Years in Lab` (e.g.
  `"2021–2024"`) is likewise `team.html`-only.
- `Role / Title` must describe what the STUDENT did (e.g. "Research
  Service Learning," "Mentored Research"), never Dr. Shen's own
  mentoring relationship to them — "co-mentor," "committee chair," etc.
  describe his role, not the student's, and must never be displayed as
  if they were. If a row's Role/Title looks like it's describing Dr.
  Shen's involvement rather than the student's activity, flag it rather
  than copying it in as-is; leave `role` blank if the CV doesn't name a
  separate student activity (see Venkata Akella, whose row has no
  Role/Title for exactly this reason — `team.html` shows just his
  Department with no dangling separator in that case).
- `Featured` (`Yes`/`No`) — controls whether an **Alumni** row also gets
  a full homepage card in `ITG_DATA` (bio, focus, photo/initials, links)
  versus a text-only line on `team.html` only. It does NOT gate whether
  someone appears on `team.html` at all — every row appears there
  regardless of Featured. It also doesn't affect **Current Members**:
  every Current Member always gets a homepage card, Featured or not,
  since removing a current lab member's card would be a much bigger
  visual change than trimming an alumnus down to a text line.
- The rest of the columns (`Full Name`, `Current Focus`, `Full Bio`,
  `Photo filename`, `Avatar initials`, the two Link label/URL pairs)
  map the same way they always have — see the field mapping below.

**`team.html` row format: two lines per person, never an em dash as a
separator.** Current Members render as `Full Name` on one line and
`Role/Title` below it in a smaller muted line. Alumni render as `Full
Name` (left) with `Years in Lab` right-aligned in a small muted mono
font on the first line (the same visual treatment as a News item's
date), then `Department · Role/Title` below it in a smaller muted line
(middle dot separator, matching the device already used for Angelina
Davis's current role) — or just `Department` alone, no dangling
separator, when Role/Title is blank. Em dashes are reserved for prose
elsewhere on the site; don't use one to glue name/department/role
together into a single line here.

**`team.html` sorting is different for Current Members than for
Alumni.** Current Members sort by the spreadsheet's `Order` column
ascending — a manual, PI-first sequence the owner sets directly, not
date-based, so don't auto-sort it. Alumni ignore `Order` entirely: each
of the three Degree Level subgroups sorts by `TDIRalumniSort` (search
for it in `team.html`), which parses `Years in Lab` via
`TDIRyearRange` and orders by end year descending, then start year
descending as a tiebreak, then name alphabetically as the final
tiebreak. This makes a newly added alumni row slot into the correct
chronological position automatically with no manual renumbering needed
on future syncs. An open-ended range like `"2024–"` (no end year) sorts
as if it were the most recent/ongoing entry — but treat that as a data
smell to flag back to the owner during a sync, not something to accept
silently: an "ongoing" person filed under Alumni usually means they
should be a Current Member instead. This happened with Jesus Santiago
and Diya Patel in an earlier spreadsheet draft; both were corrected to
closed ranges (rather than left open-ended) before being finalized.

**Gotcha, worth remembering: a row can be flagged for a full card
without having the data a card needs.** Joy Gomes has gone back and
forth between `Section = Alumni`/`Current Members` and
`Featured = No`/`Yes` across several syncs, and even now that she's
settled as `Section = Current Members`, her Current Focus, Full Bio,
Photo filename, and Avatar initials are still blank. Don't fabricate any
of those to fill the gap — ask the owner if you're unsure whether the
card should exist at all, but if they confirm the person belongs as a
Current Member card as-is, the deliberate treatment is: derive initials
from their own name (a standard abbreviation, same convention as
everyone else's, not a fabricated fact), and leave both `focus` and
`bio` as empty strings rather than inventing text for either. `ITGcard`
and `ITGopenModal` both handle a falsy `focus` and a falsy `bio`
gracefully — the flip-card skips the "Current Focus" label entirely
when `focus` is empty, the modal skips the bio paragraph when `bio` is
empty, and the flip-card hint reads "Click for more" instead of "Click
for full bio" whenever `bio` is empty — so lean on that existing
behavior rather than inventing new markup or placeholder copy.
Since this row's Section/Featured value has changed direction more than
once, double-check its current values against the spreadsheet (or ask)
before assuming either state is stable.

**Workflow:** whenever the user says something like "I updated the
spreadsheet," "sync the team section," or similar — even without further
detail — do the following:

1. Read every row of the `Team Members` sheet in that workbook.
2. Compare it against both `ITG_DATA` in `index.html` and `TDIR_DATA` in
   `team.html`.
3. Regenerate `TDIR_DATA` in `team.html` to match the spreadsheet
   **exactly** — every row, every time, since that page has no Featured
   filter of its own. Each entry needs `sec` (from `Section`), `order`,
   `name`, `role`, `degree` (from `Degree Level`, alumni only), `dept`
   (from `Department / Program`, alumni only), and `years` (alumni
   only) — `degree` and `dept` are separate fields, not a combined
   string.
4. Regenerate `ITG_DATA` in `index.html` to hold only: all Current
   Members, plus any Alumni row with `Featured = Yes`.
   - Map each column directly: `Full Name` → `name`, `Role / Title` →
     `role`, `Current Focus` → `focus`, `Full Bio` → `bio`, `Avatar
     initials` → `initials`.
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
   - If a person now qualifies for a homepage card (Current Member, or
     Alumni newly marked Featured) and has no corresponding `ITG_DATA`
     entry, add them (falling back to the initials-only pattern above if
     the card fields are missing). If `ITG_DATA` has a person no longer
     in the spreadsheet, or an Alumni row that lost its Featured flag,
     remove them from `ITG_DATA` (they'll still show on `team.html`).
     Photo crop position (`pos` field) is a display-only tweak that
     doesn't come from the spreadsheet — leave any existing `pos`
     override on a person untouched unless the user separately reports
     their photo is cropped wrong.
5. **Validate the JavaScript syntax in both files' `<script>` blocks**
   after editing, before considering the task done. Try extracting each
   script's contents to a temp file and running `node --check` on it —
   but don't assume `node` is installed; check with `command -v node`
   first, since it is not on `PATH` in this dev environment. If `node`
   isn't available, validate instead by serving the directory (e.g.
   `python3 -m http.server`) and loading both `index.html` and
   `team.html` in a browser, confirming the console shows no errors and
   that the homepage cards and the `team.html` directory both render
   populated, not empty. This file has previously broken silently —
   every card on the page rendering empty with no visible error beyond a
   browser console message — because of a single bad escaped character
   inside a bio string. Pay particular attention to apostrophes inside
   single-quoted bio/focus/name strings in the spreadsheet data; escape
   them correctly or rephrase to avoid them.
6. Summarize what changed on each page (people added, removed, or
   edited; any fields that differed; anyone whose Featured status moved
   them between a card and a text line) before committing.

If the spreadsheet file can't be found at the expected path, ask the user
directly rather than guessing or skipping the update.

**Dr. Shen's bio publication count is a live value, not typed text.**
Inside `ITG_DATA`, Shen's `bio` field is a template literal (backticks,
not a plain string) that interpolates `PUB_COUNT`, a constant defined
just above `const ITG_DATA` as `typeof papers !== 'undefined' ?
papers.length : 66` — `papers` being the same array `data/publications-
data.js` exports for `publications.html`. This means the "N
peer-reviewed publications" figure in the bio always matches the actual
count on the publications page and never needs manual updating during a
Team sync; it only needs attention if the sentence's *wording* changes
(e.g. adding a new sentence near it — remember it's a template literal
now, so a literal `` ` `` or an unescaped `${` inside new bio text would
break it). The `66` fallback only fires if `data/publications-data.js`
failed to load entirely (e.g. testing via `file://` — see the gotcha
under "How to test changes" above) and should be bumped to match reality
if it ever drifts, but it is not the source of truth in normal use. The
funding total ($1.6M) and mentee count (43) later in the same sentence
are still static text sourced from the CV — there's no live data source
for those in this codebase, so they still need manual updates when the
CV changes.

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

## Publications database — keeping index.html and publications.html in sync

Unlike Team and News, the publications list isn't hand-edited in a
spreadsheet — it's a CSV that Claude maintains directly, sourced from
Dr. Shen's CV, which gets run through a script that pulls real metadata
from CrossRef. Three files work together:

    data/PIRL-Publications-Database.csv   -- hand-maintained source of truth
    scripts/sync_publications.py          -- generates the file below from it
    data/publications-data.js             -- generated; loaded by BOTH
                                              index.html (featured:true only,
                                              in the "Selected publications"
                                              section) and publications.html
                                              (everything)

**Never hand-edit `publications-data.js` directly except for the CrossRef-
pending workaround below** — it's generated output, and the next sync run
will silently overwrite manual edits.

**CSV columns:** `doi, title, url, theme, role, note, featured`. `title`
exists purely so the CSV is readable by a human scanning rows (originally
added because the owner couldn't tell which paper a row was just from its
DOI) — the sync script fills or refreshes it automatically after every
successful CrossRef/URL fetch, so don't hand-maintain it, and don't add
it to the generated JS output (`papers` objects intentionally don't carry
a `title` field; the real title only ever lives inside the `apa` string).
A row whose fetch fails this run keeps whatever `title` it already had
rather than being blanked out — for a brand-new row with a CrossRef-
pending DOI, that means filling `title` in by hand once, same as you'd
source the rest of its citation manually (see the gotcha below). `doi` is
preferred; `url` is only a fallback for a paper with no DOI yet (the
script scrapes `citation_*` meta tags from that URL instead). `theme` is
one of `prevention | neuro | tbi | other` — GBD/consortium-style papers
with huge collaborator lists (Dr. Shen contributes analytic/interpretive
input, not authorship credit) consistently go in `other` with
`role: "Consortium collaborator"`, even when the topic is injury-related,
since there's no clean way to feature or theme-bucket a 200+ author paper.
`role` should reuse the existing vocabulary already in the CSV (e.g.
`"First author, PI"`, `"Senior author · PhD Mentee"`, `"Collaborator"`,
`"Contributing author"`) rather than inventing new phrasing, so filtering
and role-pill styling stay consistent. `note` and `featured:yes` are only
meaningful for the ~8 papers curated onto the homepage; every other row
should have `featured:no` and a blank `note` — don't write "why it
matters" copy for the general list, per the site's no-fabrication rule.

**Running the sync script needs one-time setup in this dev environment:**
`requests`, `beautifulsoup4`, and `lxml` are not preinstalled — run
`python3 -m pip install requests beautifulsoup4 lxml` first, or the
script fails with `ModuleNotFoundError`. As with `node` elsewhere in this
file, don't assume the dependency is there; check/install before
concluding the environment is broken.

**Gotcha: a DOI can resolve via `doi.org` but still 404 on CrossRef's
REST API.** This happens for papers still in "advance online
publication" — the DOI is registered and `https://doi.org/<doi>` redirects
correctly to the publisher's page, but `api.crossref.org/works/<doi>`
returns 404 until CrossRef finishes indexing it (observed lag: at least
several months). The sync script has no fallback for this case when only
a DOI (no URL) is given, so the row fails and gets dropped from the
output. Don't assume a fetch failure means the DOI is wrong — check
`curl -sL -o /dev/null -w "%{http_code}" https://doi.org/<doi>` first; a
200 there with a 404 from the CrossRef API confirms this specific
situation. The fix is to source the real citation manually (web search
for the title usually surfaces the publisher's page with authors,
volume/issue/pages) and hand-append the entry into the generated
`publications-data.js`, formatted to match `build_apa()`'s output exactly.
Leave a comment at the top of the file listing which `id`s were patched
this way, since **re-running the sync script will silently drop them
again** until CrossRef catches up — check that comment before trusting a
fresh sync's output is complete.

**`sentence_case()`'s heuristic has two extension points, not one:**
`_PROTECTED_WORDS` (single proper nouns, e.g. `"China"`, `"Poland"`) and
`_PROTECTED_PHRASES` (multi-word proper nouns applied via whole-phrase
regex after word-level casing, e.g. `"Global Burden of Disease Study"`,
`"Otto the Auto"` — necessary because GBD papers are a recurring category
in this CV and word-level protection of "Global"/"Burden"/"Disease"/
"Study" individually would risk over-capitalizing those common words
elsewhere). The function also has dedicated handling for hyphenated
acronym compounds (`"VR-based"`, not caught by the plain ALL-CAPS check
since the whole token isn't uppercase) and acronyms with a lowercase
plural suffix (`"DALYs"`). If a future sync surfaces a new
mis-capitalized title, check first whether it fits one of these four
existing mechanisms before adding a fifth.

**Workflow:** whenever the user says something like "add this paper,"
"sync the publications database," or similar:

1. Add/edit the CSV row(s), reusing existing `theme`/`role` conventions
   above.
2. Run `python3 scripts/sync_publications.py data/PIRL-Publications-Database.csv data/publications-data.js`.
3. Handle any fetch failures per the CrossRef-pending gotcha above rather
   than assuming they're errors in the CSV.
4. Spot-check 5-10 generated titles for capitalization issues (the
   script prints a reminder of this every run) and extend
   `_PROTECTED_WORDS`/`_PROTECTED_PHRASES` if needed.
5. Verify both `index.html`'s featured section and `publications.html`
   render correctly (search, theme/year toggle, mentee filter) with no
   console errors before considering the task done.
6. Summarize what changed before committing.

**Known open discrepancy (as of the CSV's initial build, August 2026):**
the CV's own "Publications Across All Years" summary field states 69
peer-reviewed journal articles, but manually enumerating the CV's journal
article list found only 68 distinct entries, two of which have no
discoverable DOI anywhere (an obscure conference-adjacent journal article
and a 2009 Chinese-language journal piece) and were excluded, leaving 66
rows in the CSV. The homepage's hero impact-strip and meta tags still say
"69" (pre-existing, unchanged by that work) — this doesn't match the 66
actually browsable on `publications.html`. Don't silently "fix" this
number in either direction; it needs Dr. Shen or Paul to either locate
the missing CV entries or confirm 69 was always approximate.
