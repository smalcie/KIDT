import json


class SeismicSurvey:

    def __init__(self):
        pass


survey = {
    'survey':
        {
            'name': 'Matai 2003',
            'type': '2D',
            'id': '2000000001',
            'permit': '60001',
            'operator': 'Flowers Resources Ltd',
            'start_date': '2003-02-12',
            'end_date': '2003-02-24',
        },
    'aquisition':
        {
            'contractor': 'Seismic Blasters Ltd',
            'start_date': '2003-02-12',
            'end_date': '2003-02-24',
            'epsg': '4167',
        },
    'processing':
        {
            'contractor': 'Switched On Geophysical',
            'proc_epsg': '2193',
            'projects':
                [
                    {
                        'processing': 'Final Migration',
                        'sections':
                            [
                                {
                                    'name': 'M-3',
                                    'file': r'/home/malcolm/Dev/KI/data/MATAI_2003/DP15_FINAL_migration_nogain-PR2897_m3.sgy'
                                },
                                {
                                    'name': 'M-4',
                                    'file': r'/home/malcolm/Dev/KI/data/MATAI_2003/DP15_FINAL_migration_nogain-PR2897_m4.sgy'
                                }
                            ]
                    }
                ]
        }
}


def json_file(data):
    with open('data/MATAI_2003/' + 'survey_meta.json', 'w') as fo:
        json.dump(data, fo)


def main():
    print(survey)
    json_file(survey)
    for project in survey['processing']['projects']:
        print(project)
        for section in project['sections']:
            print(section)



if __name__ == '__main__':
    main()
