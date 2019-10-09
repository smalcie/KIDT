import segyio
import os.path
from pyproj import Proj

segy_file = r'data\MATAI_2003\DP15_FINAL_migration_nogain-PR2897_m3.sgy'


def getgeometry_xy(f):
    headers = segyio.tracefield.keys
    cdp = f.attributes(headers['CDP'])[:].tolist()
    sourcexy = zip(f.attributes(headers['SourceX'])[:].tolist(),
                   f.attributes(headers['SourceY'])[:].tolist())
    return list(zip(cdp, sourcexy))


def getgeometry_lonlat(cdp_geomtery_xy):
    cdp = [item[0] for item in cdp_geomtery_xy]
    print(cdp)
    xy = [item[1] for item in cdp_geomtery_xy]
    print(xy)
    lonlat = []
    for item in xy:
        n = xy_to_lonlat(item)
        lonlat.append(n)
    return list(zip(cdp, lonlat))


def xy_to_lonlat(xy, epsg=2193):
    p = Proj('+init=epsg:2193', preserve_flags=True)
    x = xy[0]
    y = xy[1]
    print(xy)
    lonlat = p(x, y, inverse=True)
    return lonlat


class SegyQC:

    def __init__(self, file):
        self.basename = os.path.basename(file)
        with segyio.open(file, ignore_geometry=True) as f:
            self.cdp_geometry_xy = getgeometry_xy(f)
            self.cdp_geometry_lonlat = getgeometry_lonlat(self.cdp_geometry_xy)


def main():
    qc = SegyQC(segy_file)
    print(qc.cdp_geometry_lonlat)


if __name__ == '__main__':
    main()
