# Locked palette provenance

The 256-entry LUT is frozen from the user's approved rendered Gwyddion-style
colorbar in LSMO19_AFM_Gwyddion_2dp_bar_right.png (this conversation, 2026-09-18).
It is deliberately self-contained, so future runs do not resample a screenshot,
fetch a mutable upstream resource, or invent new color stops.

The RGB values were reconciled against the approved measured-data panel to
preserve Matplotlib's image-byte versus colorbar-patch rounding conventions.
The first entry is black and the last entry is white. This file is a frozen
rendering match, not a claim that the original upstream floating-point gradient
resource has been redistributed verbatim.
