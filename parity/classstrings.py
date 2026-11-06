"""Extract CONSTANT_Utf8 strings from .class files inside jars (demo texts of ColorSettingsPages)."""
import struct, sys, zipfile

def utf8_strings(data):
    if data[:4] != b'\xca\xfe\xba\xbe': return []
    n = struct.unpack_from('>H', data, 8)[0]; i = 10; out = []; k = 1
    while k < n:
        tag = data[i]
        if tag == 1:
            ln = struct.unpack_from('>H', data, i + 1)[0]
            out.append(data[i + 3:i + 3 + ln].decode('utf-8', 'replace')); i += 3 + ln
        elif tag in (3, 4): i += 5
        elif tag in (5, 6): i += 9; k += 1
        elif tag in (7, 8, 16, 19, 20): i += 3
        elif tag in (9, 10, 11, 12, 17, 18): i += 5
        elif tag == 15: i += 4
        else: break
        k += 1
    return out

if __name__ == '__main__':
    pat = sys.argv[2] if len(sys.argv) > 2 else 'ColorSettingsPage'
    z = zipfile.ZipFile(sys.argv[1])
    for nm in z.namelist():
        if nm.endswith('.class') and pat in nm:
            print('=====', nm)
            for s in utf8_strings(z.read(nm)):
                print(repr(s)[:3000])
