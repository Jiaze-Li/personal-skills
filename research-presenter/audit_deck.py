#!/usr/bin/env python3
"""Audit a talk deck against the research-presenter format rules (read-only).

usage: python3 audit_deck.py DECK.pptx [slide numbers...]

Prints per slide: tag size, title size/length, text smaller than 10 pt (outside the
footer; 10-19 pt is listed as a note only), fonts other than Arial / Cambria Math,
shapes touching the slide edge, duplicate shape ids, and the animation summary (clicks,
effects whose target does not exist). Exit code 1 if any problem is found.
Nothing is written. Standard values live in the constants below; change them
when Jack changes the standard (and update format.md).
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

TAG_SZ, TITLE_SZ, MIN_BODY_SZ = 1600, 2800, 2000        # hundredths of a point
MIN_NOTE_SZ = 1000                                        # remarks (citations, notes) may be small, not below 10 pt
SLIDE_W, EDGE = 12192000, 100000                          # shapes may not touch the slide edge (EMU)
FOOTER_Y = 6419088                                        # footer zone starts here
TITLE_MAX_CHARS = 62                                      # one line at 28 pt bold
FONTS_OK = {'Arial', 'Cambria Math'}
MATH_CHARS = set('∫∑∂∇∝∞ΩΣΔℏ𝜴𝑓𝒌𝑬𝒋𝒗')   # math symbols typed as text in Cambria Math = wrong, must be native equations

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
MC = '{http://schemas.openxmlformats.org/markup-compatibility/2006}'


def shapes(root):
    """Yield (element, id, name, in_group) for every sp/pic/grpSp, skipping mc:Fallback copies."""
    def walk(node, nested):
        for ch in node:
            if ch.tag == MC + 'Fallback':
                continue
            if ch.tag in (P + 'sp', P + 'pic', P + 'grpSp', P + 'cxnSp'):
                nv = ch.find('.//' + P + 'cNvPr')
                yield ch, nv.get('id'), nv.get('name'), nested
                if ch.tag == P + 'grpSp':
                    yield from walk(ch, True)    # group children use group-local coordinates
                    continue
            yield from walk(ch, nested)
    yield from walk(root, False)


def xfrm(el):
    x = el.find('.//' + A + 'xfrm')
    if x is None:
        return None
    off, ext = x.find(A + 'off'), x.find(A + 'ext')
    if off is None or ext is None:
        return None
    return int(off.get('x')), int(off.get('y')), int(ext.get('cx')), int(ext.get('cy'))


def runs(el):
    """(text, size, font) for each text run, including runs inside equations."""
    out = []
    for r in el.iter():
        if r.tag in (A + 'r',):
            rp, t = r.find(A + 'rPr'), r.find(A + 't')
            out.append((t.text or '' if t is not None else '', rp.get('sz') if rp is not None else None,
                        (rp.find(A + 'latin').get('typeface') if rp is not None and rp.find(A + 'latin') is not None else None)))
        elif r.tag.endswith('}r') and r.tag.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/math'):
            rp = r.find(A + 'rPr')
            t = [c for c in r if c.tag.endswith('}t')]
            out.append(((t[0].text or '') if t else '', rp.get('sz') if rp is not None else None,
                        (rp.find(A + 'latin').get('typeface') if rp is not None and rp.find(A + 'latin') is not None else None)))
    return out


M_NS = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'


def mtext(el):
    return ''.join(t.text or '' for t in el.iter(M_NS + 't')).strip()


IDX = set('𝑎𝑏𝑐𝑑𝑒𝑖𝑗𝑘𝑙𝑚𝑛𝑝𝑞𝑟𝑠𝑡𝑥𝑦𝑧')                      # index letters (math italic)
BASES = set('𝜕𝑓𝑄𝜴𝜎𝐸𝒋𝑬𝑸𝒌𝑘𝑉𝑗')                          # symbols that carry indices


def eq_checks(root, n):
    """Native equations: every index must be a subscript, one colour per equation, scripts the colour of their base."""
    out = []
    hidden = {id(e) for fb in root.iter(MC + 'Fallback') for e in fb.iter()}
    def col(el):
        c = el.find('.//' + A + 'srgbClr')
        return c.get('val') if c is not None else None
    for om in root.iter(M_NS + 'oMath'):
        if id(om) in hidden:
            continue
        label = mtext(om)[:28]
        # (1) index typed on the baseline next to its symbol:  ∂ a ∂ b  or a single run like f0n
        for parent in om.iter():
            kids = [c for c in parent if c.tag == M_NS + 'r']
            for k1, k2, k3 in zip(kids, kids[1:], kids[2:]):
                t1, t2, t3 = mtext(k1), mtext(k2), mtext(k3)
                if t1 == '𝜕' and len(t2) == 1 and t2 in IDX and t3 and t3[0] in BASES:
                    out.append('equation %r: index %r sits on the baseline after %r, make it a subscript (sSub)' % (label, t2, t1))
        for r in om.iter(M_NS + 'r'):
            t = mtext(r)
            if len(t) >= 2 and t[0] in BASES and all(ch in IDX or ch.isdigit() for ch in t[1:]) and r.find(M_NS + 'rPr/' + M_NS + 'sty') is None:
                out.append('equation %r: %r packs an index into the symbol run, make the index a subscript' % (label, t))
        # (2) a script has a different colour than its base
        for tag in ('sSub', 'sSup', 'sSubSup'):
            for st in om.iter(M_NS + tag):
                e = st.find(M_NS + 'e'); cb = col(e) if e is not None else None
                for part in ('sub', 'sup'):
                    sc = st.find(M_NS + part)
                    if sc is not None and cb and col(sc) and col(sc) != cb:
                        out.append('equation %r: %s %r is #%s but its base is #%s (one colour per symbol)' % (label, part, mtext(sc), col(sc), cb))
    return out


def audit(z, n):
    problems, info = [], []
    try:
        root = ET.fromstring(z.read('ppt/slides/slide%d.xml' % n))
    except ET.ParseError as e:                     # invalid XML makes PowerPoint show the repair prompt
        return ['XML broken'], ['slide XML is not well-formed (%s): do NOT open it in PowerPoint' % e]
    seen, text_ids = {}, set()
    for el, sid, name, nested in shapes(root):
        seen[sid] = seen.get(sid, 0) + 1
        box = xfrm(el)
        rs = [r for r in runs(el) if r[0].strip()]
        if rs:
            text_ids.add(sid)
        if box is None:
            continue
        x, y, w, h = box
        if not nested and y >= FOOTER_Y - 1:       # footer zone: any size
            continue
        is_tag = (not nested) and y < 500000 and rs
        is_title = (not nested) and 700000 <= y <= 1300000 and h < 700000 and rs and w > 8000000
        for t, sz, font in rs:
            szv = int(sz) if sz else None
            if is_tag and szv != TAG_SZ:
                problems.append('tag is %s pt, standard %d pt: %r' % (szv and szv / 100, TAG_SZ / 100, t))
            elif is_title and szv != TITLE_SZ:
                problems.append('title is %s pt, standard %d pt: %r' % (szv and szv / 100, TITLE_SZ / 100, t[:30]))
            elif not is_tag and not is_title and szv is not None and szv < MIN_NOTE_SZ:
                problems.append('text %.1f pt (<%d) in %r: %r (too small even for a remark)' % (szv / 100, MIN_NOTE_SZ / 100, name, t[:30]))
            elif not is_tag and not is_title and szv is not None and szv < MIN_BODY_SZ:
                info.append('note: %.1f pt text %r (fine for a remark; wrong if the audience is meant to read it)' % (szv / 100, t[:30]))
            elif szv is None and not is_tag and not is_title:
                problems.append('text without explicit size in %r: %r' % (name, t[:30]))
            if font and font not in FONTS_OK:
                problems.append('font %s in %r: %r' % (font, name, t[:30]))
        for r_ in el.iter(A + 'r'):                         # symbols typed as text runs in the math font (not native equation)
            rp_, t_ = r_.find(A + 'rPr'), r_.find(A + 't')
            f_ = rp_.find(A + 'latin').get('typeface') if rp_ is not None and rp_.find(A + 'latin') is not None else None
            if f_ == 'Cambria Math' and t_ is not None and t_.text and (set(t_.text) & MATH_CHARS):
                problems.append('math symbols typed as plain text in %r: %r (use a native equation, same as the other formulas)' % (name, t_.text[:30]))
        if is_title:
            title = ''.join(r[0] for r in rs)
            info.append('title %r' % title)
            if len(title) > TITLE_MAX_CHARS:
                problems.append('title may wrap to two lines (%d chars)' % len(title))
        if not nested and y > 1400000 and not (x >= EDGE and x + w <= SLIDE_W - EDGE and y + h <= FOOTER_Y):
            if not rs or x < 0 or x + w > SLIDE_W:       # a wide text box is fine; judge by what is visible
                problems.append('%r touches the slide edge or the footer (x %d..%d, y..%d)' % (name, x, x + w, y + h))
    for sid, c in seen.items():
        if c > 1:
            problems.append('duplicate shape id %s' % sid)
    problems += eq_checks(root, n)
    # animation
    tm = root.find(P + 'timing')
    clicks = 0
    if tm is not None:
        ids = set(seen)
        targets = []
        for ctn in tm.iter(P + 'cTn'):
            nt = ctn.get('nodeType')
            if nt == 'clickEffect':
                clicks += 1
            if nt in ('clickEffect', 'withEffect', 'afterEffect'):
                tgt = ctn.find('.//' + P + 'spTgt')
                if tgt is not None:
                    targets.append(tgt.get('spid'))
        for s in set(targets):
            if s not in ids:
                problems.append('animation targets missing shape %s' % s)
        info.append('%d click(s), %d effect(s)' % (clicks, len(targets)))
    else:
        info.append('no animation')
    return info, problems


def consistency(z, slides):
    """Same symbol, same typesetting on every slide: scripts (sup/sub) and bold/italic variants."""
    scripts, styles, spelled, marks = {}, {}, [], {}
    for n in slides:
        try:
            root = ET.fromstring(z.read('ppt/slides/slide%d.xml' % n))
        except ET.ParseError:
            continue
        hidden = {id(e) for fb in root.iter(MC + 'Fallback') for e in fb.iter()}   # fallback copies are never shown
        for par in root.iter(A + 'p'):                       # text-box labels like f + (2)
            if id(par) in hidden:
                continue
            rs = [(r.find(A + 't').text or '', r.find(A + 'rPr')) for r in par.findall(A + 'r') if r.find(A + 't') is not None]
            for (t1, _), (t2, rp2) in zip(rs, rs[1:]):
                if len(t1.strip()) == 1 and t1.strip().isalpha() and re.fullmatch(r'[\(\)0-9nkabxyz,;\s]{1,6}', t2) and t2.strip():
                    b = int(rp2.get('baseline')) if rp2 is not None and rp2.get('baseline') else 0
                    scripts.setdefault((t1.strip(), t2.strip()), {}).setdefault('sup' if b > 0 else 'sub' if b < 0 else 'inline', set()).add(n)
        for tag, kind in (('sSup', 'sup'), ('sSub', 'sub')):  # native equations
            for el in root.iter(M_NS + tag):
                e = el.find(M_NS + 'e'); sc = el.find(M_NS + ('sup' if kind == 'sup' else 'sub'))
                if e is None or sc is None:
                    continue
                base, script = mtext(e), mtext(sc)
                if base and script and len(base) <= 2:
                    scripts.setdefault((base, script), {}).setdefault(kind, set()).add(n)
        for el in root.iter(M_NS + 'sSubSup'):               # quantity with an extra mark (3w, (3), total)
            e = el.find(M_NS + 'e'); sb = el.find(M_NS + 'sub'); sp = el.find(M_NS + 'sup')
            if e is not None and sb is not None and sp is not None and len(mtext(e)) <= 2:
                marks.setdefault((mtext(e), mtext(sb)), {}).setdefault('marked:' + mtext(sp), set()).add(n)
        for el in root.iter(M_NS + 'sSub'):
            e = el.find(M_NS + 'e'); sb = el.find(M_NS + 'sub')
            if e is not None and sb is not None and len(mtext(e)) <= 2 and len(mtext(sb)) == 1:
                marks.setdefault((mtext(e), mtext(sb)), {}).setdefault('bare', set()).add(n)
        for r in root.iter(M_NS + 'r'):                      # bold/italic variants of single letters
            t = mtext(r)
            if len(t) == 1 and t.isalpha():
                sty = r.find(M_NS + 'rPr/' + M_NS + 'sty')
                styles.setdefault(t, {}).setdefault(sty.get(M_NS + 'val') if sty is not None else 'italic', set()).add(n)
        for t in root.iter(A + 't'):                         # spelled-out symbols
            if id(t) in hidden:
                continue
            for w in re.findall(r'\b(hbar|tau|omega|sigma|Omega|epsilon)\b', t.text or ''):
                spelled.append((n, w))
    problems, notes = [], []
    for (base, script), kinds in sorted(scripts.items()):
        k = {x: v for x, v in kinds.items() if x in ('sup', 'sub')}
        if len(k) > 1:
            problems.append('symbol %s(%s) is superscript on slide(s) %s but subscript on slide(s) %s'
                            % (base, script, sorted(k.get('sup', [])), sorted(k.get('sub', []))))
        elif len(kinds) > 1 and 'inline' in kinds:
            notes.append('symbol %s%s: written inline on slide(s) %s but as script elsewhere' % (base, script, sorted(kinds['inline'])))
    for (base, sb), kinds in sorted(marks.items()):          # same quantity, mark present on one slide and missing on another
        if 'bare' in kinds and len(kinds) > 1:
            marked = sorted({x.split(':', 1)[1] for x in kinds if x != 'bare'})
            notes.append('quantity %s_%s: written bare on slide(s) %s but with extra mark(s) %s on slide(s) %s (same quantity? then carry the same mark)'
                         % (base, sb, sorted(kinds['bare']), marked, sorted(set().union(*[v for k, v in kinds.items() if k != 'bare']))))
    for t, v in sorted(styles.items()):
        if len(v) > 1 and 'bi' in v:
            notes.append('letter %s: bold-italic on slide(s) %s, other style on slide(s) %s (fine for vector vs scalar, else unify)'
                         % (t, sorted(v['bi']), sorted(set().union(*[x for k, x in v.items() if k != 'bi']))))
    for n, w in spelled:
        problems.append('slide %d spells the symbol out as "%s": use the Greek letter / native symbol' % (n, w))
    return problems, notes


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    z = zipfile.ZipFile(sys.argv[1])
    count = len([f for f in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', f)])
    wanted = [int(a) for a in sys.argv[2:]] or list(range(1, count + 1))
    bad = 0
    for n in wanted:
        info, problems = audit(z, n)
        print('slide %d: %s' % (n, '; '.join(info)))
        for p in problems:
            print('   !! ' + p)
        bad += len(problems)
    cp, cn = consistency(z, list(range(1, count + 1)))
    print('\ndeck-wide consistency of scientific notation:')
    for p_ in cp:
        print('   !! ' + p_)
    for n_ in cn:
        print('   note: ' + n_)
    bad += len(cp)
    print('\n%d problem(s)' % bad)
    sys.exit(1 if bad else 0)


main()
