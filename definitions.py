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
valid_connections_by_openEO_provider = {}
valid_connections_by_openEO_provider["Copernicus Data Space Ecosystem"] = []
valid_connections_by_openEO_provider["Copernicus Data Space Ecosystem"].append("SENTINEL2_L2A")
index_by_connection_by_provider = {}
index_by_connection_by_provider["Copernicus Data Space Ecosystem"] = {}
index_by_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"] = {}
index_by_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"]["NDVI"] = ["B04", "B08"]
bands_tags_connection_by_provider = {}
bands_tags_connection_by_provider["Copernicus Data Space Ecosystem"] = {}
bands_tags_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"] = []
bands_tags_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"].append("cube:dimensions")
bands_tags_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"].append("bands")
bands_tags_connection_by_provider["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"].append("values")
collection_info_image_files_base_path = '\\doc'
collection_info_image_file_by_provider_by_collection = {}
collection_info_image_file_by_provider_by_collection["Copernicus Data Space Ecosystem"] = {}
collection_info_image_file_by_provider_by_collection["Copernicus Data Space Ecosystem"]["SENTINEL2_L2A"] = "Sentinel2_Info.png"
feature_field_id_candidates = []
feature_field_id_candidates.append("id")
feature_field_id_candidates.append("fid")
CONST_OPENEO_CRS_EPSG_STRING = 'EPSG:4326'
openeo_sentinel2_l2a_tag = "SENTINEL2_L2A"
# openeo_sentinel2_bands=["B02", "B04", "B08", "B11", "SCL"]
CONST_PYTHON_CONSOLE_TAG = 'PythonConsole'
CONST_OUTPUT_PATH_SUFFIX_NDVI = '_ndvi'
CONST_OUTPUT_PATH_BANDS = '_bands'
CONST_EQUAL_AREA_CRS_EPSG_STRING = 'EPSG:3035' # valid for Europe, change for optimal
CONST_MAXIMUM_AREA_FOR_POLYGON = 5000 * 5000
CONST_VALUES_STRING_SEPARATOR = '_'





