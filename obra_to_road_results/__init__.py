__import__('pkg_resources').declare_namespace(__name__)

from obra_to_road_results.event_list import download as download_list
from obra_to_road_results.event_data import download_all as download_events


def run_all():
    download_list()
    download_events()