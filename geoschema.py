import json
import os.path

path_to_data = 'data'

section1 = {'line': '1001', 'file': r'/path/to/section1', 'epsg': 2193,
            'cdp': 21, 'cdpx': 73, 'cdpy': 77}

section2 = {'line': '1002', 'file': r'/path/to/section2', 'epsg': 2193,
            'cdp': 21, 'cdpx': 73, 'cdpy': 77}


class ToJsonMixin:

    def __init__(self):
        pass

    def json_string(self):
        return json.dumps(self, default=ToJsonMixin._convert_to_dict, indent=4)

    def json_to_file(self, file):
        with open(file, 'w') as fo:
            json.dump(self, fo, default=ToJsonMixin._convert_to_dict)

    @staticmethod
    def object_from_file(file):
        with open(file, 'r') as fo:
            return json.load(fo, object_hook=ToJsonMixin._dict_to_obj)

    @staticmethod
    def _convert_to_dict(o):
        """
        A function takes in a custom object and returns a dictionary representation of the object.
        This dict representation includes meta data such as the object's module and class names.
        """
        #  Populate the dictionary with object meta data
        obj_dict = {
            "__class__": o.__class__.__name__,
            "__module__": o.__module__
        }
        #  Populate the dictionary with object properties
        obj_dict.update(o.__dict__)
        return obj_dict

    @staticmethod
    def _dict_to_obj(our_dict):
        """
        Function that takes in a dict and returns a custom object associated with the dict.
        This function makes use of the "__module__" and "__class__" metadata in the dictionary
        to know which object type to create.
        """
        if "__class__" in our_dict:
            # Pop ensures we remove metadata from the dict to leave only the instance arguments
            class_name = our_dict.pop("__class__")
            # Get the module name from the dict and import it
            module_name = our_dict.pop("__module__")
            # We use the built in __import__ function since the module name is not yet known at runtime
            module = __import__(module_name)
            # Get the class from the module
            class_ = getattr(module, class_name)
            # Use dictionary unpacking to initialize the object
            obj = class_(**our_dict)
        else:
            obj = our_dict
        return obj


class Section(ToJsonMixin):

    def __init__(self, line, file, epsg, cdp, cdpx, cdpy):
        self.line = line
        self.file = file
        self.epsg = epsg
        self.cdp = cdp
        self.cdpx = cdpx
        self.cdpy = cdpy

    def __str__(self):
        return f'<Section: line={self.line}>'


class Project(ToJsonMixin):

    def __init__(self, project_name, processing_type, sections=[]):
        self.project_name = project_name
        self.processing_type = processing_type
        self.sections = sections

    def __str__(self):
        return f'<Project: project name={self.project_name}, type={self.processing_type}>'

    def add_section(self, section):
        self.sections.append(section)


class SeismicSurvey(ToJsonMixin):

    def __init__(self, survey_name, survey_id, dimension, environment, year, projects=[]):
        self.survey_name = survey_name
        self.survey_id = survey_id
        self.dimension = dimension.upper()
        self.environment = environment
        self.year = year
        self.projects = projects

    def __str__(self):
        return f'<SeismicSurvey: survey name={self.survey_name}, dimension={self.dimension}, ' \
               f'year={self.year}>'

    def get_json_file_name(self):
        return os.path.join(path_to_data, f'{self.survey_id}_survey.json')


def main():
    s1 = Section(section1['line'], section1['file'], section1['epsg'],
                 section1['cdp'], section1['cdpx'], section1['cdpy'],)
    s2 = Section(section2['line'], section2['file'], section2['epsg'],
                 section2['cdp'], section2['cdpx'], section2['cdpy'],)
    proj = Project('abcdef', 'Final Migration', sections=[s1, s2])
    survey = SeismicSurvey(survey_name='Matai-2003', survey_id='MAT2D03ONS', dimension='2D', environment='onshore',
                           year='2003', projects=[proj])
    print(survey.json_string())
    o_file_name = survey.get_json_file_name()
    survey.json_to_file(o_file_name)
    # # s3 = json.loads(s1.json_string(), object_hook=ToJsonMixin._dict_to_obj)
    # # print(json.loads(proj.json_string(), object_hook=ToJsonMixin._dict_to_obj))
    # with open('output.json', 'r') as fo:
    #     survey_from_file = json.load(fo, object_hook=ToJsonMixin._dict_to_obj)
    surveyobj = ToJsonMixin.object_from_file(o_file_name)
    print('object from json')
    print(surveyobj.json_string())


if __name__ == "__main__":
    main()
