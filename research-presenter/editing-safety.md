# Editing safely (PowerPoint on this Mac)

Mistakes here cost Jack's hand work, so follow this routine on every edit of the deck.

## Before an edit
1. The deck must be closed in PowerPoint. An open copy can be stale and can save itself over my edit.
2. Compare the saved deck with my last version (or my backup). Anything new is Jack's work: keep it, never rebuild it.
3. Back up the saved state to the scratchpad. Work on the one working deck only; no extra copies in his folder.

## Never let a stale copy overwrite the install (2026-11-02)
- PowerPoint saves the document it holds in memory when it is closed or when Jack saves. A stale copy left open puts the old content back over my install, silently.
- Order: close any open deck, read the file on disk and compare with the last version I know, install, wait 15 s, open once, check the render. Do not click into the deck while the old copy could still be open, and do not call close on a doc that was opened before the install.
- If the render lacks something I just installed, first check the file on disk (is my change in it?) before debugging the XML.
- Editing never needs PowerPoint open. It is only for looking at the render; background control does not take his mouse.
- If Jack is editing live (the file changes between my read and my install), stop, tell him, and ask him to close the deck. Re-check with `cmp` right before copying.
- After an animation target is deleted in PowerPoint (e.g. he replaces the = sign), the click it started disappears and its effects merge into the previous click. Re-read the click structure and rebuild it.

## Doing the edit
- python-pptx does not see shapes inside `mc:AlternateContent` (native equations). Use lxml or raw XML for those, and write the zip back with every other part unchanged.
- New shapes go last in the shape tree. A shape placed earlier is hidden under any later filled box.
- Native equation: `a14:m` inside `mc:AlternateContent` (Choice requires `a14`, Fallback a plain text box). An equation-only paragraph needs the `m:oMathPara` wrapper, otherwise nothing renders.
- Some math-italic Greek (e.g. 𝜔) renders blank. Use the plain letter (ω).
- Replace text by exact match and assert the match count first, so a changed sentence fails loudly instead of silently doing nothing.

## Repair prompt ("PowerPoint found a problem with content") (2026-11-02)
- It means invalid XML. Never click Repair; cancel, restore the backup, then find the cause.
- Known cause: `a:pPr algn` takes only `l`, `ctr`, `r`, `just` etc. `"c"` is invalid and triggers the prompt (it looks fine in python-pptx and in every other check). Use `ctr`. Also check `m:jc` uses `left`/`center`.
- Duplicate shape ids on a slide (e.g. a movie picture and a hand-written shape) are a likely cause too: give every shape a unique id. An equation shape's two copies (Choice and Fallback) legitimately share one id.
- Bisect: build variants (frame only, no equations, no timing), install and open each once, cancel any prompt, restore the backup between runs. Whitespace-only `m:t`, an empty `a:t` and `m:acc` accents are valid.

## After the edit: verify twice
1. Read the saved file back and check the new text is really there (an older save can undo it).
2. `touch` the file, wait about 10 s, open it in PowerPoint, and look at the rendered slide.
   - It opens on slide 1. Click the slide's thumbnail, then press down, one key at a time with a wait between. Queued keys jump slides. Zoom the slide area and confirm the slide number.
   - If the view shows old content: close the deck, touch, wait, reopen.
3. Run the format checklist in format.md on what you see.
4. Close the deck and release PowerPoint when done, so no stale copy stays open for Jack to save over.

## Adding figures and animation
- Add a picture with python-pptx (`add_picture`) to get the relationship right, then move its element into a group. Write an image computed from the physics to the scratchpad, never into Jack's folder.
- Group the later build steps into one `p:grpSp` and add an appear-on-click `p:timing` block targeting the group id (after `clrMapOvr`). PowerPoint shows a star next to the slide thumbnail when the animation is read. Slideshow playback has not been tested unless said so in the report.
- Animated figures: use a video (mp4, H.264, yuv420p), not a GIF; PowerPoint plays it natively, sharper and smaller. Add it with python-pptx `add_movie` with a poster frame (it gives a click-to-play timing block). To mix it with other click effects, write the main sequence yourself: click 1 a `mediacall` `playFrom(0.0)` on the movie, later clicks the other effects, plus a `p:video` `cMediaNode` (set `repeatCount="indefinite"` to loop) in the root list. Re-read the movie's shape id after setting ids. Render frames with matplotlib and pipe them to ffmpeg; keep text inside the video at 14 pt or more at slide size.
- After the shape tree is rebuilt, PowerPoint may regenerate the stale preview image of equation shapes on its own; this is harmless.
- A deck opened by python-pptx and saved again keeps everything, including shapes in `mc:AlternateContent`.

## Reporting
- Say what was and was not checked.
- If an edit was undone or anything unexpected happened (stale copy, lost text), say so plainly.
- Tell Jack to close any copy he has open without saving if it may be stale.
