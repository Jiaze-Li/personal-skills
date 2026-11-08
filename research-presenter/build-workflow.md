# Build workflow: the order to make and check one slide

Written 2026-11-03 after slide 7 shipped with a 10 pt section tag (nobody measured it). The rule: every number on the slide is checked by a tool, not by eye. Do the stages in this order; do not report a slide until stage 6 is clean.

## 0. Map and choose a layout
- Map the handnote section(s) to the slide (SKILL.md step 1). Jack owns the logic; the layout is mine.
- Pick the layout from the logic of the slide, not from the previous slide (2026-11-03, Jack: "logic stays, presentation form is free"). Examples: chain A -> B -> C = row of boxes; one quantity changing = left figure, right equations; comparison = two columns; derivation = stacked equation lines with a figure strip. Look for outside examples only when no layout fits.
- Write the click story (choreography.md) now, one idea per click. The layout must leave room for what appears later.

## 1. Frame first
- Start the slide from the standard frame: copy the section tag, title, rule line, footer and page number from the last signed-off slide (slide 6 today), not from the template. Change only the words. This is what keeps tag 16 pt, title 28 pt and their positions identical on every slide.

## 2. Figure first
- Draw the figure at the largest size the panel allows (format.md "Figure first"), from the sign table (content.md). Native shapes, flat, labels as native equations or 20 pt+ text.
- Reuse an existing figure of the deck when the same object appears again (same map, same colours: blue E, red response, orange key arrows).

## 3. Then the words
- Native equations next, then the one key sentence. Apply the text rule (content.md): nothing the equation already says.
- Decide for each text whether it is body (the audience reads it: 20 pt or more) or a remark (citation, source, clarification, footer: small, at the edge). See format.md "Body versus remark". Arial; Cambria Math inside equations. Set the size explicitly on every run, never inherit.

## 4. Then the animation
- Build the clicks from the story. Directions follow the logic: figures left to right, text/equation chains top to bottom. Animate only what helps the story; parts that simply exist from the start stay still. Count the clicks.

## 5. Install safely (editing-safety.md)
- Before installing, run the audit on the new file (it parses every slide; broken XML is reported there). Only a file that passes goes into the deck folder. A repair prompt in PowerPoint always means I skipped this: cancel it, never Repair, restore the backup.
- Back up, compare disk with the last known version, install, open once, no repair prompt.

## 5b. Equations: build with structure, then check (added 2026-11-05)
- Generate every equation from structure helpers (sub, sup, subsup, bar, delimiters, big operators), never by concatenating symbol and index letters. Pass one colour to every run of an equation.
- Before installing, open an earlier slide that contains the same quantity and copy how it is built.
- The audit now fails on: an index typed on the baseline after a symbol (e.g. after ∂), an index packed into a symbol run, and a script whose colour differs from its base. It cannot see everything: it does not know every symbol.

## 6. Audit, then look
- Run the audit on the installed file and fix everything it prints for the new slide:
  `python3 ~/.claude/skills/research-presenter/audit_deck.py DECK.pptx N`
  It also checks the whole deck for one scientific notation: the same symbol must be typeset the same on every slide (f⁽ⁿ⁾ superscript everywhere, no spelled-out "tau" or "hbar"); bold/italic differences are listed as notes. A notation problem on an earlier slide is fixed (small format fix) and reported.
  It checks: tag size, title size and length (one line), text under 10 pt outside the footer (a problem), and text from 10 to 19 pt (listed as a note: fine for a remark, wrong for body, so decide which it is), fonts other than Arial / Cambria Math, shapes touching the slide edge, duplicate shape ids, clicks, animation targets that do not exist. It does not demand animation on every shape, and it does not flag a box wider than its panel.
- Then look at the rendered slide: take a background screenshot of PowerPoint (ask for computer-use access to PowerPoint at the start of the session; the user approves once). Zoom into every equation and compare index placement and colour with an earlier slide. Never report a slide as checked without having seen it. Walk the format.md checklist: equations render, series aligned, nothing hidden behind a filled box, vectors match the sign table.
- Also run the audit for the whole deck once per session and tell Jack about problems on slides he edited by hand. Report them, do not fix his hand-made work without asking (his animation choices stay as he made them).

## 7. Report
- The usual short report plus the click list. State what the audit covered and what it cannot see (slideshow playback, video).

## Known blind spots of the audit
- It reads sizes from the file. A size inherited from the theme is reported as "without explicit size". Text in pictures is not checked.
- Equation text outside the margin is judged by its box, which can be wider than the visible equation.
- Group children are only checked for size and font, not position.
