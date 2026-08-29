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

## Design system (do not deviate without being asked)

- **Colors:** navy `#0D1F3C`, steel `#1B3A6B`, sky blue `#2E6CA8`, amber
  accent `#E8B84B`, sage green `#5B8A6F`, sand background `#F7F4EE`.
- **Fonts:** `DM Serif Display` for headings, `Inter` for body text,
  `JetBrains Mono` for small labels/eyebrows/tags. All loaded via Google
  Fonts `<link>` in `<head>`.
- **Layout:** single scrolling page, sections in this order: Nav → Hero →
  Research Pillars (3 cards) → Impact numbers strip → Publications →
  Team ("Meet the Lab") → Join Us (grad student recruiting) → News →
  Contact/Footer.
- All custom CSS classes are short/abbreviated (e.g. `.hin`, `.rc`, `.tgd`,
  `.itg-card`) to keep the single file compact. Follow the existing naming
  convention rather than introducing verbose class names.

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
`ITG_DATA`** — e.g. extract the script block and run `node --check` on it,
or at minimum carefully check every apostrophe inside single-quoted
strings is either avoided (rephrase) or properly escaped.

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
     `images/<filename>` (the user uploads actual image files into an
     `images/` folder in the repo separately — never fabricate or guess
     a filename that isn't in the spreadsheet).
   - The two Link label/URL column pairs → the `links` array
     (`[{label, url}]`); omit any pair that's blank rather than adding an
     empty object.
   - If a person in the spreadsheet has no corresponding entry in
     `ITG_DATA`, add them. If `ITG_DATA` has a person no longer in the
     spreadsheet, remove them. If someone's Photo filename is blank,
     leave `photo` unset — the initials fallback already handles this
     automatically. Photo crop position (`pos` field) is a display-only
     tweak that doesn't come from the spreadsheet — leave any existing
     `pos` override on a person untouched unless the user separately
     reports their photo is cropped wrong.
4. **Validate the `<script>` block's JavaScript syntax after editing**
   before considering the task done (e.g. extract the script contents to
   a temp file and run `node --check` on it, or equivalent). This file
   has previously broken silently — every card on the page rendering
   empty with no visible error beyond a browser console message — because
   of a single bad escaped character inside a bio string. Pay particular
   attention to apostrophes inside single-quoted bio/focus/name strings
   in the spreadsheet data; escape them correctly or rephrase to avoid
   them.
5. Summarize what changed (people added, removed, or edited; any fields
   that differed) before committing.

If the spreadsheet file can't be found at the expected path, ask the user
directly rather than guessing or skipping the update.
