from geoschema import *
import segyio
import json
import os.path
from glob import glob
from pyproj import Proj
from geopandas import GeoDataFrame as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt


def get_survey_meta_paths(path, pattern):
    return glob(os.path.join(path, pattern))


def get_survey_objects(paths):
    survey_objects = []
    for path in paths:
        survey_object = ToJsonMixin.object_from_file(path)
        survey_objects.append(survey_object)
    return survey_objects


class ProcessStaging:

    def __init__(self, path):
        self.path = path
        self.surveys = get_survey_objects(get_survey_meta_paths(path, survey_pattern))

    def __str__(self):
        return f'<ProcessStaging: Number of surveys = {len(self.surveys)}>'

    def process_qc_reports(self):
        qc_reports = []
        for survey in self.surveys:
            survey_qc = SurveyQC(survey)
            qc_reports.append(survey.make_qc_reports())
        return qc_reports

    def make_navigations(self):
        pass

class SurveyQC:

    def __init__(self, survey):
        self.survey = survey
        self.qc_report = survey.get_qc_report()

class GeometrySet:

    def __init__(self, survey, *args):
        self.survey = survey
        self.geometries = args


class SegyGeom:

    def __init__(self, line, epsg, file, cdp=21, cdp_x=181, cdp_y=185):
        self.line = line
        self.epsg = epsg
        self.cdp = cdp
        self.cdp_x = cdp_x
        self.cdp_y = cdp_y
        with segyio.open(file, ignore_geometry=True) as f:
            self.cdp_geometry = self._get_geometry(f)
        self.cdp_geometry_lonlat = self._getgeometry_lonlat()

    def _get_geometry(self, f):
        cdp = f.attributes(self.cdp)[:].tolist()
        geometry = zip(f.attributes(self.cdp_x)[:].tolist(),
                       f.attributes(self.cdp_y)[:].tolist())
        return list(zip(cdp, geometry))

    def _getgeometry_lonlat(self):
        cdp = [item[0] for item in self.cdp_geometry]
        xy = [item[1] for item in self.cdp_geometry]
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
        line_geom = [LineString([item[1] for item in self.cdp_geometry_lonlat])]
        gdf_line = gpd({'line': [self.line]}, geometry=line_geom, crs={'init': f'epsg:{self.epsg}'})
        gdf_line.to_file('output/cdp_nav_line.shp')
        gdf_line.plot()
        plt.show()
        gdf = gpd(cdp, columns=['CDP'], geometry=geometry)
        gdf.crs = {'init': f'epsg:{self.epsg}'}
        gdf.to_file('output/cdp_nav_point.shp')
        return gdf

class SegyQC:

    def __init__(self, survey, epsg, line, file):
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
    # qc = SegyQC(segy_file, survey_name, line_name, survey_epsg)
    # print(qc.cdp_geometry_xy)
    # print(qc.cdp_geometry_lonlat)
    # x = qc.to_gdf()
    # #print(x)
    # geom = SegyGeom(line=line_name, epsg=survey_epsg, file=segy_file)
    # print(geom)
    # survey_objects = get_survey_objects(get_survey_meta_paths(path_to_data, survey_pattern))
    # for survey_object in survey_objects:
    #     projects = survey_object.get_projects()
    #     for project in projects:
    #         print(project.get_sections())
    ps = ProcessStaging(path_to_staging)
    print(ps)



if __name__ == '__main__':
    main()
