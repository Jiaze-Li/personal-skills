"""Offline tests. No experimental IBW or font files need to be bundled."""
from pathlib import Path
import importlib.util
import struct
import tempfile
import unittest
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('afm',ROOT/'scripts'/'plot_afm.py')
afm=importlib.util.module_from_spec(spec);spec.loader.exec_module(afm)


def write_ibw(p,endian='<',unit='m'):
    nx,ny,nc=7,5,3
    data=np.stack([np.ones((ny,nx))*1e-7,
                   np.arange(ny*nx).reshape(ny,nx)*1e-10,
                   np.ones((ny,nx))*2e-7]).astype(endian+'f4')
    labels=b'\0'*32+b''.join(x.encode().ljust(32,b'\0') for x in ['DeflectionRetrace','HeightRetrace','ZSensorRetrace'])
    note=b'FastScanSize: 2e-5\rSlowScanSize: 1e-5\r'
    header=bytearray(384)
    struct.pack_into(endian+'h',header,0,5)
    struct.pack_into(endian+'15i',header,4,320+data.nbytes,0,len(note),0,*([0]*4),0,0,len(labels),0,0,0,0)
    struct.pack_into(endian+'i',header,76,data.size)
    struct.pack_into(endian+'H',header,80,2)
    struct.pack_into(endian+'4i',header,132,nx,ny,nc,0)
    struct.pack_into(endian+'4d',header,148,20e-6/(nx-1),10e-6/(ny-1),1,1)
    header[212:216]=unit.encode().ljust(4,b'\0')
    header[216:224]=b'm\0\0\0m\0\0\0'
    p.write_bytes(header+data.tobytes()+note+labels)
    return data


class Tests(unittest.TestCase):
    def test_le_be_rectangular_and_channel_order(self):
        with tempfile.TemporaryDirectory() as t:
            for endian in ('<','>'):
                p=Path(t)/'test.ibw';original=write_ibw(p,endian)
                d=afm.read_ibw(p);h,name,unit=afm.select_height(d,None,None)
                self.assertEqual(name,'HeightRetrace')
                np.testing.assert_allclose(h,original[1].astype(float)*1e9)
                self.assertEqual(h.shape,(5,7))
                sx,sy,_=afm.physical_scan_um(d,None)
                self.assertAlmostEqual(sx,20);self.assertAlmostEqual(sy,10)
    def test_unknown_voltage_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'test.ibw';write_ibw(p,unit='V');d=afm.read_ibw(p)
            with self.assertRaises(ValueError):afm.select_height(d,None,None)
    def test_no_magnitude_guessing(self):
        self.assertEqual(afm.length_factor('nm'),1e-9)
        with self.assertRaises(ValueError):afm.length_factor('')
    def test_palette_and_rounding(self):
        c=afm.palette();self.assertEqual(c.N,256)
        self.assertEqual(afm.height_label(-.284902),'−0.28 nm')
        self.assertEqual(afm.height_label(.188558),'0.19 nm')
        self.assertEqual(afm.height_label(-1e-6),'0.00 nm')
    def test_flatten_does_not_mutate_input(self):
        rng=np.random.default_rng(1);y,x=np.mgrid[-1:1:64j,-1:1:64j]
        z=.3*x*x+.03*y+rng.normal(0,.01,x.shape);copy=z.copy()
        flat,bg=afm.robust_poly_flatten(z,2)
        np.testing.assert_array_equal(z,copy)
        np.testing.assert_allclose(flat,z-bg+np.median(bg))
        self.assertLess(np.std(flat),np.std(z)/3)
    def test_constant_input_is_safe(self):
        z=np.ones((30,30))
        flat,bg=afm.robust_poly_flatten(z,1)
        self.assertTrue(np.isfinite(flat).all())


if __name__=='__main__':unittest.main()
