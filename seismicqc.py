import segyio
import json
import os.path
from pyproj import Proj
from geopandas import GeoDataFrame as gpd
from shapely.geometry import Point


segy_file = r'data/MATAI_2003/DP15_FINAL_migration_nogain-PR2897_m3.sgy'
survey_name = 'Matai-2D'
processing_name = 'Final Migration'
line_name = 'M-3'
survey_epsg = '2193'


class SegyQC:

    def __init__(self, file, survey, line, epsg):
        self.basename = os.path.basename(file)
        self.survey = survey
        self.line = line
        self.epsg = epsg
        with segyio.open(file, ignore_geometry=True) as f:
            self.n_traces = f.tracecount
            self.sample_rate = segyio.tools.dt(f) / 1000
            self.n_samples = f.samples.size
            self.twt_max = f.samples.max()
            self.text_header = segyio.tools.wrap(f.text[0], width=80)
            self.binary_header = {}
            for k, v in f.bin.items():
                self.binary_header[str(k)] = v
            self.cdp_geometry_xy = self._getgeometry_xy(f)
        self.cdp_geometry_lonlat = self._getgeometry_lonlat()

    def _getgeometry_xy(self, f):
        headers = segyio.tracefield.keys
        cdp = f.attributes(headers['CDP'])[:].tolist()
        sourcexy = zip(f.attributes(headers['SourceX'])[:].tolist(),
                       f.attributes(headers['SourceY'])[:].tolist())
        return list(zip(cdp, sourcexy))

    def _getgeometry_lonlat(self):
        cdp = [item[0] for item in self.cdp_geometry_xy]
        xy = [item[1] for item in self.cdp_geometry_xy]
        lonlat = [self._xy_to_lonlat(item) for item in xy]
        return list(zip(cdp, lonlat))

    def _xy_to_lonlat(self, xy):
        p = Proj(f'+init=epsg:{self.epsg}', preserve_flags=True)
        x, y = xy
        lonlat = p(x, y, inverse=True)
        return lonlat

    def to_gdf(self):
        cdp = [item[0] for item in self.cdp_geometry_lonlat]
        geometry = [Point(item[1]) for item in self.cdp_geometry_lonlat]
        gdf = gpd(cdp, columns=['CDP'], geometry=geometry)
        # gdf.crs = {'init': 'epsg:4326'}
        gdf.crs = {'init': f'epsg:{self.epsg}'}
        gdf.to_file('output/cdp_nav.shp')
        return gdf

    def json_string(self):
        return json.dumps(self, default=convert_to_dict, indent=4)

    def json_file(self):
        with open(os.path.splitext(self.basename)[0] + '.json', 'w') as fo:
            json.dump(self, fo, default=convert_to_dict)


def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names.
    """
    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)
    return obj_dict


def main():
    qc = SegyQC(segy_file, survey_name, line_name, survey_epsg)
    print(qc.cdp_geometry_xy)
    print(qc.cdp_geometry_lonlat)
    x = qc.to_gdf()
    print(x)


if __name__ == '__main__':
    main()
