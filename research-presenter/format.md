# Format: what a finished slide looks like

Reference: the signed-off model slide of the current deck (usually slide 2). Match it.

## Sizes and fonts
- Page title: 28 pt, bold, black, Arial, one line, left, same position on every slide.
- Section tag (e.g. "01 / MOTIVATION"): 16 pt, bold, dark blue, small orange bar to its left, same position on every slide.
- Text in boxes: 20 pt or more, black. Labels and captions next to or inside a figure (including small analogy sketches) count as box text: also 20 pt or more. Make room by shrinking the figure, never the text. Box titles are optional; if used, 22–24 pt and they carry content, never format words like "LOGIC CHAIN".
- Footer, header, references and supplementary notation may be smaller (about 10–13 pt). Supplementary notation sits small, at the side.
- **Body versus remark (Jack, 2026-11-03):** every piece of text is one of two kinds. *Body* is information the audience is expected to read: titles, equations, labels, the key sentence. It is large (20 pt or more). A *remark* is there for another reason (academic habit, showing a source, a note for the few who care, a clarification of a label): a citation or DOI, a paper source tag, "E exaggerated" under the big E, a colour key, a definition kept for completeness, the footer. Remarks may be small (about 10–14 pt), sit at the side or edge, and may be grey. Test: if the audience skipped it, would the talk still work? Yes means remark. Never shrink body text to make room (shrink the figure), and never enlarge a remark to body size. Decide the kind for each text before choosing its size; a remark should still be readable by someone who leans in, so not under about 10 pt.
- Arial throughout; Cambria Math inside equations.
- **Which font for which kind of text (Jack, 2026-11-04):** words (titles, tags, captions, key sentences, remarks, words inside a box) are Arial, at the sizes above. Anything that is a math symbol or formula is a native PowerPoint equation object (Cambria Math, rendered by the equation engine), at the size of the surrounding text role (equations in boxes 22–24 pt, big figure labels about 30 pt). This includes single labels in a figure such as ∫f₀Ω, Q_xxz, j_y⁽³⁾, E, Ω: do not type them as plain text boxes, even when the font is set to Cambria Math. Typed text gets wrong sub/superscripts (italic digits, baseline hacks), no bold-italic Greek and different integral signs, so it looks different from the equations next to it. Copy the run properties (size, colour, bold/italic style) of an existing equation of the same quantity. Sub/superscripts come from equation structure, not baseline offsets. Labels that Jack typed himself stay as they are unless he asks.

## Equations
- **Anything mathematical is a native equation in standard math typesetting (Jack, 2026-11-05).** Formulas, symbols, indices, sub/superscripts, hats, bars, integrals, sums: all of it, however small. A subscript is a subscript wherever it appears: an index (a, b, c, n, k, ...) after a symbol is built with the sub/superscript structure, never a letter typed on the baseline. ∂ₐ∂ᵦ is ∂ with subscript a, ∂ with subscript b, not "∂a∂b". Do not pack a symbol and its index into one run (f₀ₙ is f with subscript 0n). This holds for generated equations too: build them with the structure functions, and copy the form of the same quantity from an earlier slide (slide 9 shows Q_abc, ∂ₐ∂ᵦΩ, f₀ₙ).
- **One colour per equation unless the emphasis is deliberate.** A script always has the colour of its base (Ω_{n,c} is entirely orange, not an orange Ω with a black n,c). Colour differences inside one equation (e.g. drift term blue, relaxation term red) are allowed only when the colour is the point of the slide. When generating an equation with a colour, pass the colour to every run, including indices, brackets, bars and big operators.
- Native, editable PowerPoint equation objects. Never pictures or Unicode typed as text. Figure labels made of symbols (∫f₀Ω, Q_xxz, j_y⁽³⁾) are equations too (see the font rule above); `audit_deck.py` flags math symbols typed as Cambria Math text.
- Readable at the back of the room. Typeset carefully (sub/superscripts, hats, vectors bold).
- Emphasis on one symbol (e.g. E) is used to show its power in the response order.
- **One symbol, one typesetting across the whole deck (Jack, 2026-11-03):** the same quantity looks the same on every slide (f⁽ⁿ⁾ is a superscript, f₀ a subscript, same bold/italic for vectors). Before building a slide, look at how the earlier slides typeset each symbol and copy it, also inside text-box labels (their baseline setting), not only inside equations. At the end of a slide, scan the other slides for the same symbols. The marks a quantity carries belong to it too: if E_y is E_y^{3ω} on one slide, a later slide that talks about the same field writes E_y^{3ω}, not a bare E_y (Jack, 2026-11-05: slide 13 dropped the 3ω that slide 12 had). Copy the exact form from the slide where the quantity was introduced; the audit lists bare/marked mismatches as notes, so judge each one.

## Layout
- One common margin for the title, tag, text columns and footer. Panels and figures may be wider than the title when the layout needs it (Jack, 2026-11-03), but never touch the slide edge (keep about 0.3 cm); nothing touching a panel or box edge inside a panel.
- **Judge by what the audience sees (Jack, 2026-11-03):** a text or equation box wider than its panel does not matter as long as the visible text stays inside the panel. Presentation comes first, the audit is a helper.
- Panels may be resized freely to fit content. Content inside a panel keeps equal padding.
- Text is centered or aligned deliberately, never accidentally off-center.
- Arrow glyphs between steps sit alone in one centered column, thick, aligned with each other.
- Text and equations share a clear alignment (e.g. proportionality signs lined up).
- Orange accent bar marks a key box; the one key message may be orange.
- Items in a series (stacked labels 1ω / 2ω / 3ω, rows of steps, equation lines) align on their shared element, not each on its own center: line up the ω, or the = sign, vertically, the way equations are aligned on =. Use one common left edge when the shared part sits at the start of each item. Equal sizes. Place labels in empty space of their panel, never over data.

## Figures
- **Series items align abstractly (Jack):** items of one series (titles f0, f(1), f(2); maps; signs) sit at the same relative position in their own cell, e.g. all at the top-left corner of their map, at the same height. Equal gaps between series items and equal margins to the panel edge on both sides. Check visible edges, not image edges: transparent margins hide real distances.
- **Wrap a long series like an equation:** when the row is too wide, break the line where the equation would break; the operator (+) starts the second line. Put the result (= or →) at the end.
- **Cause marks sit next to the sign they belong to:** the E arrow goes right above the first +, and animates with it.
- **Operators carry meaning:** use → (orange, same as the key arrows) when the right side is not a strict sum (e.g. the total contains all orders), = only for a strict equality.
- **Figure first, text second (Jack, 2026-11-02):** fix the figure size and position first, as large as the panel allows; then place labels, signs and notes around it, in the figure's empty corners and margins. Never let a label's position cap the figure's size. Image margins are transparent, so labels may sit over them. Row layout: keep a series on one line, size all maps equal, leave just enough gap for the sign between them.
- Paper figures: crop only stray fragments from neighbouring panels; never stretch; keep citation and axis meaning intact.
- Own drawings: flat shading, no outlines, native editable shapes, grouped.
- Labels reuse the equation symbols.

## Pre-flight checklist (look at the rendered slide)
1. Title 28 pt, one line; tag 16 pt in the standard spot.
2. All box text ≥ 20 pt; only footer/reference text smaller.
3. Titles, text and footer inside the common margin; panels not touching the slide edge; nothing clipped; visible text inside its panel.
4. Equations render (none blank); arrows centered and aligned; series items (labels, panels, rows) aligned on their shared element (the ω, the =).
5. New shapes not hidden behind a filled box.
6. Every vector in a figure matches its sign table (see content.md).
