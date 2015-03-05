from setuptools import setup, find_packages
 
setup(
    name='obra_to_road_results',
    packages=find_packages(),
    entry_points = {
        'console_scripts': [
            'dl_event_list=obra_to_road_results.event_list:download',
        ]
    }
)