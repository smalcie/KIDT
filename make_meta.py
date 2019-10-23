from geoschema import *

section1 = Section('1001', 'data/DP15_FINAL_migration_nogain-PR2897_m3.sgy', 2193, 21, 73, 77, )
section2 = Section('1002', 'data/DP15_FINAL_migration_nogain-PR2897_m4.sgy', 2193, 21, 73, 77, )

project1 = Project('Matai-2003-FM', 'Final Migration', sections=[section1, section2])

survey = SeismicSurvey(survey_name='Matai-2003', survey_id='MAT2D03ONS', dimension='2D', environment='onshore',
                       year='2003', projects=[project1])

o_file_name = survey.get_json_file_name()
survey.json_to_file(o_file_name)
