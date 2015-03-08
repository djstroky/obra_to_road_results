from setuptools import setup, find_packages
 
setup(
    name='obra_to_road_results',
    packages=find_packages(),
    install_requires=[
    	'requests>=2.5.3',
    	'beautifulsoup4>=4.3'
    ],
    entry_points = {
        'console_scripts': [
            'dl_event_list=obra_to_road_results.event_list:download',
        ]
    }
)