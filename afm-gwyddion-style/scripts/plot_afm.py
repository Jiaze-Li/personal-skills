#!/usr/bin/env python3
"""Reproducible AFM figure from measured Igor Binary Wave v5 data.

Standalone: numpy, matplotlib, Pillow only; no GUI, internet or Gwyddion install.
The palette is frozen from the user's approved Gwyddion-style rendering.
Flattening is our NumPy implementation, NOT the Gwyddion processing engine.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
import struct
import tempfile
from pathlib import Path

_cache = os.environ.get("MPLCONFIGDIR")
if not _cache or not os.path.isdir(_cache) or not os.access(_cache, os.W_OK):
    os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp(prefix="afm-mpl-")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import ListedColormap, Normalize
import matplotlib.patheffects as pe

ROOT = Path(__file__).resolve().parents[1]


def text0(b: bytes) -> str:
    return b.split(b"\0", 1)[0].decode("latin1").strip()


def read_ibw(path: Path) -> dict:
    """Parse v5 header, actual dimensions, channel-label blocks, units and notes.

    Supports LE/BE real numeric waves, 2D images or 3D channel stacks.
    Does not infer the height channel by position or infer units by magnitude.
    """
    raw = path.read_bytes()
    if len(raw) < 384:
        raise ValueError("IBW header is truncated.")
    endian = '<' if struct.unpack_from('<h',raw)[0] == 5 else '>'
    if struct.unpack_from(endian+'h',raw)[0] != 5:
        raise ValueError("Supported format is numeric Igor Binary Wave v5. Export v5 or calibrated height data.")
    sizes = struct.unpack_from(endian+'15i', raw,4)
    if min(sizes) < 0:
        raise ValueError("Invalid negative IBW block size.")
    wfm, formula_n, note_n, extended_unit_n = sizes[:4]
    dim_unit_ns, dim_label_ns = sizes[4:8], sizes[8:12]
    npnts = struct.unpack_from(endian+'i',raw,76)[0]
    typ = struct.unpack_from(endian+'H',raw,80)[0]
    if typ & 1:
        raise ValueError("Complex waves are not supported for height maps.")
    unsigned = bool(typ & 64)
    code = typ & ~64
    types = {2:'f4',4:'f8',8:'u1' if unsigned else 'i1',
             16:'u2' if unsigned else 'i2',32:'u4' if unsigned else 'i4'}
    if code not in types:
        raise ValueError(f"Unsupported/text IBW type: {typ}.")
    dtype = np.dtype(endian+types[code])
    dims4 = struct.unpack_from(endian+'4i',raw,132)
    dims = list(dims4)
    while dims and dims[-1] == 0:
        dims.pop()
    if len(dims) not in (2,3) or min(dims) <= 0 or math.prod(dims) != npnts:
        raise ValueError(f"Expected a 2D height image / 3D channel stack; dimensions={dims4}.")
    if dims[0] < 2 or dims[1] < 2:
        raise ValueError("A height image must have at least two points per spatial axis.")
    data_end = 384 + npnts*dtype.itemsize
    if wfm != 320 + npnts*dtype.itemsize or data_end > len(raw):
        raise ValueError("IBW header and numeric data sizes disagree.")
    arr = np.frombuffer(raw,dtype=dtype,count=npnts,offset=384).copy().reshape(tuple(reversed(dims)))
    # Array indexing is [channel, y, x]; Igor's first dimension varies fastest.
    p = 64+wfm
    def block(n: int) -> bytes:
        nonlocal p
        if p+n > len(raw):
            raise ValueError("IBW metadata is truncated.")
        v=raw[p:p+n]; p+=n; return v
    block(formula_n)
    note=block(note_n).decode('latin1')
    unit=text0(block(extended_unit_n)) if extended_unit_n else text0(raw[212:216])
    dim_units=[text0(raw[216+4*i:220+4*i]) for i in range(4)]
    for i,n in enumerate(dim_unit_ns):
        if n: dim_units[i]=text0(block(n))
    label_blocks=[block(n) for n in dim_label_ns]
    channels=dims[2] if len(dims)==3 else 1
    labels=[]
    if len(dims)==3 and label_blocks[2]:
        b=label_blocks[2]
        if len(b)%32: raise ValueError("Malformed dimension-label block.")
        entries=[text0(b[i:i+32]) for i in range(0,len(b),32)]
        # First label belongs to the whole dimension; following labels index channels.
        labels=entries[1:channels+1]
    if len(labels)!=channels or not all(labels):
        m=re.search(rb'DataTypeList:([^;\r\n]+)',raw[data_end:])
        if m:
            alternate=[s.strip().decode('latin1') for s in m.group(1).split(b',') if s.strip()]
            if len(alternate)==channels: labels=alternate
    metadata={}
    for line in re.split(r'[\r\n]+',note):
        if ':' in line:
            k,v=line.split(':',1);metadata[k.strip()]=v.strip()
    return dict(array=arr, labels=labels, unit=unit, metadata=metadata,
                name=text0(raw[92:124]), dim_units=dim_units,
                steps=struct.unpack_from(endian+'4d',raw,148),
                sha256=hashlib.sha256(raw).hexdigest(), shape=list(dims))


def length_factor(unit: str) -> float:
    """SI multiplier; never infer nm versus m from data magnitudes."""
    u=unit.strip().replace('μ','u').replace('µ','u').lower()
    options={'m':1.,'meter':1.,'metre':1.,'mm':1e-3,'um':1e-6,'nm':1e-9,
             'pm':1e-12,'angstrom':1e-10,'å':1e-10}
    if u not in options:
        raise ValueError(f"Unknown/non-length unit {unit!r}; supply --height-unit only after confirming calibration.")
    return options[u]


def select_height(d: dict, channel: str | None, unit_override: str | None) -> tuple:
    arr=d['array'];labels=d['labels']
    if arr.ndim==2:
        if channel and labels and channel.lower()!=labels[0].lower():
            raise ValueError(f"Requested channel {channel!r} is not present: {labels}.")
        selected=arr;name=labels[0] if labels else d['name'] or 'single_length_channel'
    else:
        targets=[channel] if channel else ['HeightRetrace','HeightTrace','Height']
        matched=[i for target in targets for i,lab in enumerate(labels) if lab.lower()==target.lower()]
        if not matched:
            raise ValueError(f"Cannot identify requested height channel; available ordered labels: {labels}. Do not assume channel 0.")
        i=matched[0];selected=arr[i];name=labels[i]
    unit=unit_override or d['unit']
    z=np.asarray(selected,dtype=np.float64)*length_factor(unit)*1e9
    if np.count_nonzero(np.isfinite(z)) < .95*z.size:
        raise ValueError("More than 5% of height pixels are invalid; inspect scan before automatic processing.")
    return z,name,unit


def physical_scan_um(d: dict, override: list | None) -> tuple:
    if override:
        if len(override)!=2 or not all(np.isfinite(override)) or min(override)<=0:
            raise ValueError('--scan-um requires positive X Y values.')
        return float(override[0]),float(override[1]),'explicit_user_override'
    md=d['metadata'];res=[];methods=[]
    for axis,key in enumerate(('FastScanSize','SlowScanSize')):
        val=md.get(key,md.get('ScanSize'))
        if val is not None:
            # These are Asylum scan-size note fields, defined in SI metres.
            try: size=float(val)*1e6
            except ValueError: raise ValueError(f"Cannot parse {key}={val!r}; use --scan-um X Y.")
            methods.append(key if key in md else 'ScanSize')
        else:
            size=abs(d['steps'][axis])*(d['shape'][axis]-1)*length_factor(d['dim_units'][axis])*1e6
            methods.append('dimension_coordinate_span')
        if not np.isfinite(size) or size<=0:
            raise ValueError('Missing/invalid physical scan calibration; supply --scan-um X Y.')
        res.append(size)
    return *res,methods


def serif_font_name() -> str:
    names={f.name for f in font_manager.fontManager.ttflist}
    for name in ('Times New Roman','Liberation Serif','Tinos','DejaVu Serif'):
        if name in names:return name
    return 'serif'


def palette() -> ListedColormap:
    a=np.loadtxt(ROOT/'assets'/'approved_palette.csv',delimiter=',',skiprows=1)
    if a.shape!=(256,3) or np.any(~np.isfinite(a)) or np.any((a<0)|(a>1)):
        raise ValueError('Bundled locked palette is missing or malformed; do not substitute another colormap.')
    cmap=ListedColormap(a,name='approved_gwyddion_style',N=256)
    cmap.set_under(a[0]);cmap.set_over(a[-1]);cmap.set_bad('#808080')
    return cmap


def nice_scale(scan_um: float) -> float:
    target=scan_um*.25
    exp=math.floor(math.log10(target))
    candidates=[m*10.**e for e in range(exp-1,exp+2) for m in (1,2,5)]
    return min((v for v in candidates if v<scan_um*.45),key=lambda v:abs(v-target))


def height_label(z: float, decimals: int=2) -> str:
    text=f'{z:.{decimals}f}'
    if float(text)==0:text=f'{0:.{decimals}f}'
    return text.replace('-','−')+' nm'

def edge_anomaly_crop_fraction(z, max_crop=0.05):
    """Return 0 or max_crop.

    The outer max_crop strip is called abnormal when it is strongly shifted
    relative to the interior or contains far more interior-extreme pixels than
    expected. This is deliberately conservative.
    """
    if max_crop <= 0:
        return 0.0
    ny, nx = z.shape
    ky = max(1, int(round(ny * max_crop)))
    kx = max(1, int(round(nx * max_crop)))
    if ny <= 2*ky + 10 or nx <= 2*kx + 10:
        return 0.0

    inner = z[ky:ny-ky, kx:nx-kx]
    border = np.concatenate([
        z[:ky, :].ravel(),
        z[ny-ky:, :].ravel(),
        z[ky:ny-ky, :kx].ravel(),
        z[ky:ny-ky, nx-kx:].ravel(),
    ])

    inner = inner[np.isfinite(inner)]
    border = border[np.isfinite(border)]
    if inner.size < 100 or border.size < 100:
        return 0.0

    q25, q75 = np.percentile(inner, [25, 75])
    iqr = max(q75 - q25, 1e-12)
    median_shift = abs(np.median(border) - np.median(inner)) / iqr

    p1, p99 = np.percentile(inner, [1, 99])
    extreme_frac = np.mean((border < p1) | (border > p99))

    # Strong edge shift or edge-extreme enrichment.
    if median_shift > 0.75 or extreme_frac > 0.10:
        return max_crop
    return 0.0


def robust_poly_flatten(z, order=1, max_iter=8, clip_sigma=2.5):
    ny, nx = z.shape
    yy, xx = np.mgrid[-1:1:complex(ny), -1:1:complex(nx)]

    if order == 1:
        X = np.column_stack([
            np.ones(z.size),
            xx.ravel(),
            yy.ravel(),
        ])
    elif order == 2:
        X = np.column_stack([
            np.ones(z.size),
            xx.ravel(),
            yy.ravel(),
            xx.ravel()**2,
            xx.ravel()*yy.ravel(),
            yy.ravel()**2,
        ])
    else:
        raise ValueError("flatten order must be 1 or 2")

    y = z.ravel()
    mask = np.isfinite(y)
    if mask.sum() < 10*X.shape[1]:
        raise ValueError("Insufficient valid pixels for robust flattening.")

    for _ in range(max_iter):
        coef = np.linalg.lstsq(X[mask], y[mask], rcond=None)[0]
        residual = y - X @ coef
        med = np.median(residual[mask])
        mad = np.median(np.abs(residual[mask] - med))
        sigma = 1.4826 * mad if mad > 0 else np.std(residual[mask])
        if not np.isfinite(sigma) or sigma <= 0:
            break
        new_mask = np.isfinite(y) & (np.abs(residual - med) <= clip_sigma * sigma)
        if new_mask.sum() < 10*X.shape[1]:
            break
        if np.array_equal(new_mask, mask):
            break
        mask = new_mask

    background = (X @ coef).reshape(z.shape)
    # Preserve the approved arbitrary height offset; this is NOT absolute thickness.
    flattened = z - background + np.nanmedian(background)
    return flattened, background


def large_scale_metric(a):
    row_med = np.nanmedian(a, axis=1)
    col_med = np.nanmedian(a, axis=0)
    return max(float(np.ptp(row_med)), float(np.ptp(col_med)))


def auto_flatten(z):
    flat1, bg1 = robust_poly_flatten(z, order=1)
    flat2, bg2 = robust_poly_flatten(z, order=2)
    m1 = large_scale_metric(flat1)
    m2 = large_scale_metric(flat2)

    # Minimum necessary order: only use second order if improvement >=25%.
    if m2 < 0.75 * m1:
        return flat2, 2, m1, m2
    return flat1, 1, m1, m2




def process(z: np.ndarray, sx: float, sy: float, args) -> tuple:
    ny,nx=z.shape
    crop=edge_anomaly_crop_fraction(z) if args.crop=='auto' else float(args.crop)
    if not np.isfinite(crop) or not 0<=crop<=.20:
        raise ValueError('Crop fraction must be between 0 and 0.20; automatic maximum is 0.05.')
    ky,kx=round(ny*crop),round(nx*crop)
    cropped=z[ky:ny-ky,kx:nx-kx].copy()
    if min(cropped.shape)<8:raise ValueError('Crop leaves too few pixels.')
    sx2,sy2=sx*cropped.shape[1]/nx,sy*cropped.shape[0]/ny
    bg=np.zeros_like(cropped);m1=m2=None
    if args.flatten=='none':flat=cropped.copy();order=0
    elif args.flatten=='auto':
        flat,order,m1,m2=auto_flatten(cropped)
        _,bg=robust_poly_flatten(cropped,order)
    else:
        order=int(args.flatten);flat,bg=robust_poly_flatten(cropped,order)
    if not 0<=args.low_pct<args.high_pct<=100:
        raise ValueError('Percentiles must satisfy 0 <= low < high <= 100.')
    lo,hi=np.nanpercentile(flat,[args.low_pct,args.high_pct]) if args.zrange is None else args.zrange
    if not np.isfinite(lo+hi) or hi<lo:raise ValueError('Invalid height limits.')
    warning=[]
    if hi==lo:
        # A perfectly constant image has no contrast; use a reported finite display span.
        lo-=.005;hi+=.005;warning.append('Constant height data: display expanded +/-0.005 nm only.')
    if crop:warning.append('Automatic crop is a heuristic; brightness alone does not prove a scan artifact.')
    if order==2:warning.append('Quadratic background removal can remove real long-wavelength topography; review for quantitative analysis.')
    if not np.isfinite(flat).all():warning.append('Invalid pixels rendered neutral gray and excluded from percentiles; never interpolated.')
    if height_label(lo,args.decimals)==height_label(hi,args.decimals):
        warning.append('Two-decimal labels coincide; retain true limits in JSON, request --decimals 3 if needed.')
    info=dict(crop_fraction_requested=crop,crop_pixels=dict(left=kx,right=kx,top=ky,bottom=ky),
              original_shape_yx=[ny,nx],display_shape_yx=list(flat.shape),
              original_scan_um=[sx,sy],display_scan_um=[sx2,sy2],
              fov_convention='full_scan_size * retained_pixel_count / original_pixel_count',
              flatten_order=order,flatten_metric_plane_nm=m1,flatten_metric_quadratic_nm=m2,
              height_reference='z - fitted_background + median(fitted_background)',
              raw_range_nm=[float(np.nanmin(z)),float(np.nanmax(z))],
              processed_range_nm=[float(np.nanmin(flat)),float(np.nanmax(flat))],
              display_limits_nm=[float(lo),float(hi)],
              requested_percentiles=[args.low_pct,args.high_pct] if args.zrange is None else None,
              normalization='linear height -> LUT coordinate; not linear perceived brightness',
              saturated_low_pct=100*float(np.mean(flat[np.isfinite(flat)]<lo)),
              saturated_high_pct=100*float(np.mean(flat[np.isfinite(flat)]>hi)),warnings=warning)
    return flat,cropped,bg,info


def render(flat: np.ndarray, info: dict, args) -> None:
    """Render measured pixels and calibrated annotations; no AI image generation."""
    sx,sy=info['display_scan_um'];lo,hi=info['display_limits_nm']
    font=serif_font_name();scale=args.scale_um or nice_scale(sx)
    if not 0<scale<sx*.85:raise ValueError('Scale bar must fit within the displayed physical field.')
    fig=plt.figure(figsize=(6.4,5.),dpi=args.dpi,facecolor='white')
    ax=fig.add_axes([.055,.08,.72,.84])
    im=ax.imshow(flat,cmap=palette(),norm=Normalize(lo,hi,clip=False),origin='upper',
                 extent=(0,sx,sy,0),interpolation='nearest',aspect='equal')
    ax.set_xticks([]);ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True);spine.set_linewidth(1.1);spine.set_color('black')
    # Preserve the approved placement; only the scale-label typography changes.
    x0=.045*sx;ybar=.958*sy
    ax.plot([x0,x0+scale],[ybar,ybar],color='white',lw=4.,solid_capstyle='butt')
    # Use one font for digits, mu and m so the complete label is consistently bold.
    if scale>=1:
        label=f'{scale:g} μm'
    else:
        label=f'{scale*1000:g} nm'
    t=ax.text(x0+scale/2,ybar-.032*sy,label,fontsize=args.scale_font,
              fontfamily=font,fontstyle='italic',fontweight=args.scale_weight,
              color='white',ha='center',va='bottom')
    t.set_path_effects([pe.withStroke(linewidth=1.,foreground='black',alpha=.35)])
    # The rightward 100 px move at 350 dpi is frozen as a physical 2/7 inch shift.
    cx=.825+(100/350)/6.4
    cax=fig.add_axes([cx,.18,.045,.64])
    cb=fig.colorbar(im,cax=cax);cb.set_ticks([]);cb.outline.set_linewidth(1.)
    cax.text(.5,1.025,height_label(hi,args.decimals),transform=cax.transAxes,
             ha='center',va='bottom',fontsize=args.label_font,fontfamily=font,color='black')
    cax.text(.5,-.035,height_label(lo,args.decimals),transform=cax.transAxes,
             ha='center',va='top',fontsize=args.label_font,fontfamily=font,color='black')
    out=args.output
    out.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(out,dpi=args.dpi,bbox_inches='tight',pad_inches=.03,
                transparent=args.transparent,facecolor='none' if args.transparent else 'white')
    plt.close(fig)
    info['render']=dict(font=font,scale_label_pt=args.scale_font,colorbar_label_pt=args.label_font,
                        scale_um=scale,dpi=args.dpi,decimals=args.decimals,
                        scale_label_weight=args.scale_weight,scale_label_style='italic',
                        scale_label_outline_pt=1.,scale_label_outline_alpha=.35,
                        palette='approved_gwyddion_style_frozen_256',
                        colorbar_right_shift_inches=100/350,
                        upper_label=height_label(hi,args.decimals),lower_label=height_label(lo,args.decimals))


def main(argv=None) -> dict:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('-o','--output',type=Path)
    p.add_argument('--channel')
    p.add_argument('--height-unit',help='Explicit confirmed height-unit override; never guess calibration.')
    p.add_argument('--scan-um',nargs=2,type=float,metavar=('X','Y'))
    p.add_argument('--crop','--crop-frac',dest='crop',default='auto')
    p.add_argument('--flatten',choices=['auto','none','1','2'],default='auto')
    p.add_argument('--low-pct',type=float,default=5.)
    p.add_argument('--high-pct',type=float,default=99.)
    p.add_argument('--zrange',nargs=2,type=float,metavar=('MIN_NM','MAX_NM'))
    p.add_argument('--scale-um',type=float)
    p.add_argument('--scale-font',type=float,default=38.)
    p.add_argument('--scale-weight',choices=['normal','bold'],default='bold')
    p.add_argument('--label-font',type=float,default=29.)
    p.add_argument('--decimals',type=int,default=2)
    p.add_argument('--dpi',type=int,default=350)
    p.add_argument('--transparent',action='store_true')
    args=p.parse_args(argv)
    if args.dpi<72 or args.dpi>1200:raise ValueError('dpi must be 72..1200 (default 350).')
    if args.decimals not in range(7):raise ValueError('Decimals must be 0..6.')
    if not 0<args.scale_font<=72 or not 0<args.label_font<=72:raise ValueError('Font sizes must be 0..72 pt.')
    args.output=args.output or args.input.with_name(args.input.stem+'_AFM.png')
    if args.output.suffix.lower()!='.png':raise ValueError('Use .png output.')
    d=read_ibw(args.input);z,name,unit=select_height(d,args.channel,args.height_unit)
    sx,sy,size_source=physical_scan_um(d,args.scan_um)
    flat,crop,bg,info=process(z,sx,sy,args)
    info.update(skill_version='2.1.0',input_file=args.input.name,input_sha256=d['sha256'],
                channel=name,height_input_unit=unit,scan_size_source=size_source,
                engine='NumPy robust fit + Matplotlib; not Gwyddion executable')
    render(flat,info,args)
    # These are unclipped heights, not a reconstruction from the PNG.
    np.savez_compressed(args.output.with_suffix('.processed.npz'),height_nm=flat,
                        cropped_input_height_nm=crop,fitted_background_nm=bg,
                        display_scan_um=info['display_scan_um'],display_limits_nm=info['display_limits_nm'])
    args.output.with_suffix('.processing.json').write_text(json.dumps(info,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(f"{name} | crop {info['crop_pixels']} | flatten {info['flatten_order']} | "
          f"z {info['render']['lower_label']} to {info['render']['upper_label']} | {args.output}")
    return info


if __name__=='__main__':
    try: main()
    except (ValueError,OSError) as e: raise SystemExit(f'AFM error: {e}')
