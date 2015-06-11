from setuptools import setup, find_packages
 
setup(
    name='obra_to_road_results',
    packages=find_packages(),
    install_requires=[
    	'requests>=2.5.3',
    	'beautifulsoup4>=4.3',
        'html5lib>=0.999'
    ],
    entry_points = {
        'console_scripts': [
            'dl_event_list=obra_to_road_results.event_list:download',
            'dl_event_data=obra_to_road_results.event_data:download_all',
            'dl_all=obra_to_road_results:run_all'
        ]
    }
)