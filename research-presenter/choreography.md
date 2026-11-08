# Choreography: how a slide unfolds in the slideshow

Jack plays slideshow mode and derives on the board while the slide reveals itself. A slide is a sequence of clicks, not one static picture. Plan the clicks from the story, then build them.

## Think from the story
1. Write the slide's story as 3–4 beats (e.g. "start: equilibrium → switch E on → each order adds a correction → they merge into the real f").
2. Give every beat one click. One click = one idea. The first state (no click) is the starting point of the story and is already readable on its own.
3. In each beat, the text line and the figure move together: the equation or sentence that names the idea appears on the same click as the picture that shows it. Never reveal a result in the text before the figure has shown it, unless the text is the question being asked.
4. The conclusion (the orange key sentence) comes last, after the figure has delivered the picture.

## Patterns that work
- **Cause label, then effect:** a small label ("Applied E") and its arrow appear first, then the equation/figure it causes.
- **Build the sum:** f₀ is visible; each correction map appears with its own term; a final click merges them into the total.
- **Merge:** copy the part pictures, fly the copies to the position of the result along a straight motion path (about 1.2 s), then fade the copies out while the result fades in. The originals stay in place.
- **Highlight, then explain:** a red box around the new terms appears with the equation, with a short label saying what they are.
- **Open-ended tail:** a "+ higher orders …" item appears together with the last explicit term, so the audience sees the series continues.
- **Effect follows the direction of the logic (Jack's rule, 2026-11-02):** use Wipe, and let the wipe direction say which way the argument runs. Text/equation chains read top to bottom, so wipe from the top. A figure series reads left to right, so wipe from the left. Fade only for a lone item with no direction (red box, small label). Motion only to show things combining. No spinning, bouncing or decorative effects. Duration about 0.5 s.
- **Several wipes in one click run in sequence, starting from the wipe's origin side (Jack's rule, 2026-11-04):** when two or more items wipe in together, do not start them all at once. The item nearest the origin wipes first (the click item), the next one is "after previous", and so on, so the eye sees one continuous wipe. Wipe from the left: arrow first, then the text to its right. Wipe from the top: the upper item first, the lower item after it. Items belonging to the same figure (its labels) may stay "with previous". Technically: one inner group per step, the next group's delay equals the previous duration (500 ms).
- **Clicks are the logic stages, not the shapes:** the starting state already holds the first stage (the starting equation and its plot). Each click then brings the equation line and the plot of ONE stage together (e.g. 1: applied E, equation and plot; 2: f(1), f(2), higher orders and the series equation; 3: the consequence). Jack remade a slide this way; build slides to match, do not invent a finer or different click order.
- **An operator can be the event itself (Jack, 2026-11-02):** a lone "+" after f0 on click 1 is not an unfinished item. With "Applied E" it says "switching E on adds something to f0". The sign shows up with the cause; the next click fills it with the terms (f(1), f(2), ...). So the sign or arrow that expresses the step appears on the click of that step, ahead of its content. Never move such a sign to the click where its content appears.
- Remove leftovers of older builds (hidden merge copies) once he has replaced them.
- Keep what must stay visible un-animated (titles, panels, the starting figure).
- **Animation serves the presentation (Jack, 2026-11-03):** not every shape needs an effect. Parts that simply exist from the start stay un-animated; add an effect only where it helps the story. The test is whether the click logic is right, not whether every shape is covered. A missing build entry is not a defect by itself; check that the shapes that do animate behave as intended.

## Building it (technical)
- A group animates only as a whole. To reveal parts of a panel one by one, ungroup it first, baking the group's scaling into the children (new position = group offset + (old position − child origin) × scale, same for size). The slide must look identical afterwards.
- An equation or text shape can be revealed paragraph by paragraph: target `p:txEl/p:pRg` (start/end paragraph index) and list the shape in `p:bldLst` with `build="p"`. Count empty paragraphs. The first paragraph that should already be there at the start is revealed by an after-previous effect in the first click par, whose start condition also carries `evt="onBegin"` with `tn val="2"`.
- Every effect on a text-bearing shape needs `grpId="0"` and a matching `p:bldP` entry (add `animBg="1"` for filled shapes).
- Copies for the merge must be the whole `p:pic` element (not just its `nvPicPr`). If the source is inside a group, add the group's offset − child-origin to the copy's position, because the copy sits at the top level.
- Motion path target = centre of the result minus centre of the source, divided by the slide width/height (path coordinates are fractions of the slide).
- Check by opening the deck in PowerPoint: a repair prompt means the XML is wrong; restore the saved deck at once and fix. Playback of the animation can only be judged by Jack in slideshow mode unless full-screen control is granted; say so in the report.

## Keeping clicks intact
- When Jack replaces the shape that triggers a click, give the new shape the click effect (wipe from the direction of the logic) and move the old follow-on effects under it. Count the clicks after every change: the story is a fixed number of clicks.
- The set of effects per click is part of the design. When I move shapes, I keep the effects and their order unchanged.

## Report
Give the click list in one short line per click ("click 1: Applied E, ↓, f = f₀ + f⁽¹⁾ + f⁽²⁾ + ⋯, red box, f⁽¹⁾ map") so Jack can check the story order by playing it.
