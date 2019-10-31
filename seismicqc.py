import geoschema
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
        survey_object = geoschema.ToJsonMixin.object_from_file(path)
        survey_objects.append(survey_object)
    return survey_objects


class ProcessStaging:

    def __init__(self, path):
        self.path = path
        self.surveys = get_survey_objects(get_survey_meta_paths(path, geoschema.survey_pattern))
        self.qc_reports = self._process_qc_reports()

    def __str__(self):
        return f'<ProcessStaging: Number of surveys = {len(self.surveys)}>'

    def _process_qc_reports(self):
        print('Processing QC Reports')
        qc_reports = []
        for survey in self.surveys:
            survey_qc = SurveyQC(survey)
            print(survey_qc)
            qc_reports.append(survey_qc)
        return qc_reports

    def write_qc_reports(self):
        for qc_report in self.qc_reports:
            qc_report.json_file()

    def make_navigation(self):
        for survey in self.surveys:
            geomset = GeometrySet(survey)



class SurveyQC:

    def __init__(self, survey):
        self.survey = survey
        self.qc_report = survey.get_qc_report()


class GeometrySet:

    def __init__(self, survey):
        self.survey = survey
        self.geomset = self._get_geomset()

    def _get_geomset(self):
        for project in self.survey.get_projects():
            for section in project.get_sections():
                print(section)



class SegyGeom:

    def __init__(self, line, epsg, file, cdp=21, cdp_x=181, cdp_y=185):
        self.line = line
        self.epsg = epsg
        self.cdp = cdp
        self.cdp_x = cdp_x
        self.cdp_y = cdp_y
        with segyio.open(file, ignore_geometry=True) as f:
            self.cdp_geometry = self._get_geometry(f)
        self.cdp_geometry_as_line = self._get_geometry_as_line()

    def _get_geometry(self, f):
        cdp = f.attributes(self.cdp)[:].tolist()
        geometry = zip(f.attributes(self.cdp_x)[:].tolist(),
                       f.attributes(self.cdp_y)[:].tolist())
        gdf = gpd(cdp, geometry=[Point(x) for x in geometry],
                  crs={'init': f'epsg:{self.epsg}'})
        return gdf

    def _get_geometry_as_line(self, epsg=4326):
        gdf = self.cdp_geometry
        gdf = gdf.to_crs({'init': f'epsg:{epsg}'})
        line_geom = [LineString([(geometry.x, geometry.y) for geometry in gdf['geometry']])]
        gdf_line = gpd({'line': [self.line]}, geometry=line_geom, crs={'init': f'epsg:{epsg}'})
        print(gdf_line)
        return gdf_line

    def get_geometry(self):
        return self.cdp_geometry_as_line


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
        with open(os.path.join(geoschema.path_to_staging, os.path.splitext(self.basename)[0] + '.json', 'w')) as fo:
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
    # survey_objects = get_survey_objects(
    #     get_survey_meta_paths(geoschema.path_to_staging, geoschema.survey_pattern))
    # for survey_object in survey_objects:
    #     projects = survey_object.get_projects()
    #     for project in projects:
    #         for section in project.get_sections():
    #             print(section)
    #             qc = SegyGeom(section.line, section.epsg,
    #                           os.path.join(geoschema.path_to_staging, section.file),
    #                           section.cdp, section.cdpx, section.cdpy)
                # print(qc.cdp_geometry.head())
                # print(qc.cdp_geometry_as_line.head())
    ps = ProcessStaging(geoschema.path_to_staging)
    ps.process_qc_reports()





if __name__ == '__main__':
    main()
