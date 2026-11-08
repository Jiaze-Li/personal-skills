---
name: research-presenter
description: Build physics/research talk slides the way Jack wants them — one slide at a time, equation-first, figures that act out the equations. Use when creating, formatting or reviewing slides for a research talk or group meeting, especially editable PowerPoint decks. Read format.md and content.md before touching a slide.
---

# Research Presenter (Jack's style)

Jack presents by deriving on the board. A slide carries only the skeleton: the A→B→C chain, key equations, key concepts and one illustration. Everything else is spoken.

Read these before editing a slide:
- `format.md` — what a finished slide looks like (sizes, margins, equations, arrows, checklist).
- `content.md` — what goes on a slide (message, text rule, figures, signs, claims).
- `choreography.md` — how a slide unfolds by click: story beats, text and figure appearing together, merge animation, how to build it.
- `editing-safety.md` — the routine for editing the deck without losing Jack's work (stale copies, verification).
- `build-workflow.md` — the order to make and check one slide (frame, figure, words, animation, install, audit with `audit_deck.py`, look). Follow it for every slide; the audit must be clean before reporting.
- This file — how we build together (workflow, permissions).
- `generic-reference.md` — optional generic talk material (audience, speaking notes, Q&A). Only when asked; it never overrides the three above.

## Workflow (per slide, one at a time, never fill all slides first)

Jack wants to review results on the slide, not discuss drafts in chat. Do the work in the deck; chat only carries the short report.

1. **Map first.** Before drawing anything, map the handnote sections to the slides (which section each slide covers) and follow the handnote order, because that is the order he speaks on the board. State the mapping in one line of the report. Do not skip a section or start from a later one because the figure is easier to draw from it.
2. **Draft the whole slide tentatively in the deck:** title, native equations, key sentence, then the figure derived from the equations (list what each term means physically; compute the sign table). No chat proposal of wording first. Then plan the click sequence from the story (choreography.md): text line and figure reveal together, beat by beat.
3. **Look at it.** Edit following editing-safety.md, render the real slide and run the format checklist. Fix what you find before reporting.
4. **Report short:** what is on the slide, which handnote section it covers, what to check (physics choices, exaggerations, anything unverified), remaining risk.
5. **Jack reviews in PowerPoint** and gives corrections; small format/wording fixes I apply without asking. Before touching the deck again, read his saved version, diff against my last version, keep his work.
6. **Ask in chat only when blocked** by a product or physics decision only he can make (what the slide should say, a missing argument, a claim the source does not support).

Figures for the slideshow: Jack plays slideshow mode. Build a figure step by step by click (first state visible, later states in one group with an appear-on-click animation); native shapes for simple drawing, a computed image only where a calculation is needed. A GIF is an optional extra, not the main mechanism.

## Permissions

- **Do without asking:** small format fixes, grammar and phrasing fixes, alignment, sizes, crops that remove stray fragments, applying the reference slide's title/tag style to a slide he has already discussed, and any change to animation (click order, effects, ungrouping a panel so its parts can be animated), including animation on shapes he added. He granted this in his own words on 2026-11-01. Report what changed. Also without asking since 2026-11-02: size and position of figures, labels and signs on a slide he has discussed (figure first, see format.md). He said he will widen these permissions as the skill becomes more precise, so when he grants something new, record it here.
- **Division of labour (Jack, 2026-11-02):** he gives the idea and holds the logic; I own the details and how the slide is built (positions, sizes, colours, spacing, arrow styles, label nudges, small collisions) and do them without asking, then report. His hand-placed items are hints of intent, not exact positions: keep the idea, refine the numbers by eye on the render. He expects the scope of what I do alone to keep growing.
- **Always work on the original deck.** Never open scratch or test copies in PowerPoint (it triggers file-access prompts); back up, then edit the original, and restore his saved version at once if an edit fails.
- **Ask first:** content, equation chain, figures, anything he hand-edited, titles not yet approved, slides he has not discussed, changing the skill itself (needs his own words, e.g. "rewrite the skill").
- **Never:** rebuild a figure he edited; make extra "check" copies in his folder; invent data or citations; put a claim on a slide that the source does not support.
- Report in his language, short and functional: what is now true, what he will see, remaining risk. No file or code names unless he asks.

## Tooling notes

Details are in `editing-safety.md`. Extra: a 3D device is drawn with a simple oblique projection from freeform faces, flat shading, no outlines, grouped so it moves as one object. No PDF export or soffice here; the PowerPoint view is the check.
