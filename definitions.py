# -*- coding: utf-8 -*-
"""
/***************************************************************************
  QGIS plugin Remote Sensing ARD time series downloader using OPENEO
        copyright            : (C) David Hernandez Lopez
        email                : david.hernandez@uclm.es
 ***************************************************************************/
"""

__author__ = 'david.hernandez@uclm.es'

CONST_AUTHOR_MAIL = 'david.hernandez@uclm.es'
CONST_SETTINGS_PLUGIN_NAME = "rs_ard_time_series_downloader"
CONST_SETTINGS_FILE_NAME = "rs_ard_time_series_downloader.ini"
CONST_PROGRAM_NAME = "Remote sensing ARD time series downloader"
CONST_PROGRAM_TITLE = "Remote sensing ARD time series downloader"
CONST_NO_COMBO_SELECT = " ... "
CONST_TEMPLATE_PATH = "\\templates"
CONST_DNBR_SYMBOLOGY_TEMPLATE = "\\BurnSeverityClassesUSGS_UN-SPIDER.qml"
CONST_DATE_STRING_TEMPLATE = "yyyy-MM-dd"
CONST_INITIAL_DATE_DEFAULT = "2023-10-01"
CONST_FINAL_DATE_DEFAULT = "2024-09-30"
CONST_SETTINGS_LAST_PATH_TAG = "last_path"
CONST_SETTINGS_INITIAL_DATE_TAG = "inital_date"
CONST_SETTINGS_FINAL_DATE_TAG = "final_date"
CONST_SETTINGS_OUTPUT_PATH_TAG = "output_path"
CONST_MINIMAL_DATES_INTERVAL = 5
# CONST_EARTH_ENGINE_PLUGIN = "ee_plugin"
CONST_OPENEO_PIP_INSTALL_PATH = '\\site-packages\\openeo'
CONST_OPENEO_AUTH_PATH = '\\Scripts\\openeo-auth.exe'
CONST_OPENEO_REFRESH_TOKENS = 'refresh-tokens.json'
CONST_OPENEO_MAPCANVAS_FEATURE_ID = "map_canvas"
CONST_OPENEO_EXTENT_CRS = "4258"
openEO_providers = {}
openEO_providers['Copernicus Data Space Ecosystem'] = 'openeo.dataspace.copernicus.eu'
feature_field_id_candidates = []
feature_field_id_candidates.append("id")
feature_field_id_candidates.append("fid")
CONST_OPENEO_CRS_EPSG_STRING = 'EPSG:4326'
openeo_sentinel2_l2a_tag = "SENTINEL2_L2A"
openeo_sentinel2_bands=["B02", "B04", "B08", "B11", "SCL"]
CONST_PYTHON_CONSOLE_TAG = 'PythonConsole'
CONST_OUTPUT_PATH_SUFFIX_NDVI = '_ndvi'
CONST_OUTPUT_PATH_SUFFIX_11_8_2 = '_11_8_2'




