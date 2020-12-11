import os
from pathlib import Path
import re

from arcgis.gis import GIS, Group
from arcgis.env import active_gis
import arcpy
from dotenv import find_dotenv, load_dotenv


def _not_none_and_len(string: str) -> bool:
    """helper to figure out if not none and string is populated"""
    is_str = isinstance(string, str)
    has_len = False if re.match(r'\S{5,}', '') is None else True
    status = True if has_len and is_str else False
    return status


def add_data_and_model_asset_locations(dir_data: Path = None) -> bool:
    """
    Add all the locations for saving and working with data and models. This typically
    needs to be invoked following cloning the repo since these resources are excluded.
    """
    if not dir_data:
        dir_prj = Path(__file__).parent.parent.parent
        dir_data = dir_prj/'data'
    else:
        dir_data = Path(dir_data) if isinstance(dir_data, str) else dir_data

    assert isinstance(dir_data, Path), "'dir_data' must be a Path object"

    # create assets for all the target data resources
    for resc in ['raw', 'external', 'interim', 'processed']:

        # build the asset data directory
        dir_resc = dir_data/resc
        if not dir_resc.exists():
            dir_resc.mkdir(parents=True)

        # build the geodatabase asset directory
        gdb_resc = dir_resc/f'{resc}.gdb'
        if not arcpy.Exists(str(gdb_resc)):
            arcpy.management.CreateFileGDB(str(gdb_resc.parent), str(gdb_resc.name))

    # create the model directory
    dir_mdl = dir_prj/'models'
    if not dir_mdl.exists():
        dir_mdl.mkdir()

    return True


def add_group(gis: GIS = None, group_name: str = None) -> Group:
    """
    Add a group to the GIS for the project for saving resources.

    Args:
        gis: Optional
            arcgis.gis.GIS object instance.
        group_name: Optional
            Group to be added to the cloud GIS for storing project resources. Default
            is to load from the .env file. If a group name is not provided, and one is
            not located in the .env file, an exception will be raised.

    Returns: Group
    """
    # load the .env into the namespace
    load_dotenv(find_dotenv())

    # try to figure out what GIS to use
    if gis is None and isinstance(active_gis, GIS):
        gis = active_gis

    if gis is None and not isinstance(active_gis, GIS):
        url = os.getenv('ESRI_GIS_URL')
        usr = os.getenv('ESRI_GIS_USERNAME')
        pswd = os.getenv('ESRI_GIS_PASSWORD')

    # if no group name provided
    if group_name is None:

        # load the group name
        group_name = os.getenv('ESRI_GIS_GROUP')

        err_msg = 'A group name must either be defined in the .env file or explicitly provided.'
        assert isinstance(group_name, str), err_msg
        assert len(group_name), err_msg

    # create an instance of the content manager
    cmgr = gis.groups

    # make sure the group does not already exist
    assert len([grp for grp in cmgr.search() if
                grp.title.lower() == group_name.lower()]) is 0, f'A group named "{group_name}" already exists. ' \
                                                                'Please select another group name.'

    # create the group
    grp = cmgr.create(group_name)

    # ensure the group was successfully created
    assert isinstance(grp, Group), 'Failed to create the group in the Cloud GIS.'

    return grp
