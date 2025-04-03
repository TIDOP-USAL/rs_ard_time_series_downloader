# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

# import optparse
import argparse
import matplotlib.pyplot as plt
import numpy as np
from osgeo import gdal, osr, ogr
import os
import json
from urllib.parse import unquote
import shutil
from os.path import exists
import datetime
import glob
from math import floor, ceil, sqrt, isnan, modf, trunc
import csv
import re
import math
from pathlib import Path

CONST_FIELD_IN_SHAPEFILE_BASENAME_STRING_SEPARATOR = '_'
CONST_FIELD_IN_SHAPEFILE_DATE_POSITION = 2
CONST_VALUES_STRING_SEPARATOR = '_'
CONST_COMMON_FIELDS_STRING_SEPARATOR = ';'
CONST_DATE_PREFIX = '20'
CONST_CSV_DATE_HEADER = 'date'
CONST_CSV_COUNT_HEADER = 'pixels_count'
CONST_CSV_NDVI_MEAN_HEADER = 'ndvi_mean'
CONST_CSV_NDVI_STD_HEADER = 'ndvi_std'
CONST_SHP_COUNT_HEADER = '_count'
CONST_SHP_MEAN_HEADER = '_mean'
CONST_SHP_STD_HEADER = '_stdev'
CONST_CROP_TYPE = 'crop'

def delete_shapefile(shapefile):
    str_error = ''
    input_base_name = os.path.splitext(os.path.basename(shapefile))[0]
    input_base_path = os.path.dirname(shapefile)
    output_base_path = os.path.dirname(shapefile)
    output_base_name = os.path.splitext(os.path.basename(shapefile))[0]
    for file in os.listdir(input_base_path):
        file_base_name = os.path.splitext(os.path.basename(file))[0]
        if file_base_name == input_base_name:
            file_with_path = input_base_path + "/" + file
            os.remove(file_with_path)
            if exists(file_with_path):
                str_error = "Unable to remove file. %s" % file_with_path
                return str_error
    return str_error


def copy_shapefile(input_shp, output_shp):
    str_error = ''
    if exists(output_shp):
        str_error = delete_shapefile(output_shp)
        if str_error:
            return str_error
    input_base_name = os.path.splitext(os.path.basename(input_shp))[0]
    input_base_path = os.path.dirname(input_shp)
    output_base_path = os.path.dirname(output_shp)
    output_base_name = os.path.splitext(os.path.basename(output_shp))[0]
    for file in os.listdir(input_base_path):
        file_base_name = os.path.splitext(os.path.basename(file))[0]
        if file_base_name == input_base_name:
            file_extension = os.path.splitext(os.path.basename(file))[1]
            output_file = output_base_path + "/" + output_base_name  + file_extension
            output_file = os.path.normcase(output_file)
            input_file = input_base_path + "/" + file
            input_file = os.path.normcase(input_file)
            try:
                shutil.copyfile(input_file, output_file)
            except EnvironmentError as e:
                str_error = "Unable to copy file. %s" % e
                return str_error
    return str_error


class GdalErrorHandler(object):
    def __init__(self):
        self.err_level = gdal.CE_None
        self.err_no = 0
        self.err_msg = ''

    def handler(self, err_level, err_no, err_msg):
        self.err_level = err_level
        self.err_no = err_no
        self.err_msg = err_msg

def julian_date(day, month, year):
    if month <= 2:  # january & february
        year = year - 1.0
        month = month + 12.0
    jd = floor(365.25 * (year + 4716.0)) + floor(30.6001 * (month + 1.0)) + 2.0
    jd = jd - floor(year / 100.0) + floor(floor(year / 100.0) / 4.0)
    jd = jd + day - 1524.5
    # jd = jd + day - 1524.5 + (utc_time)/24.
    mjd = jd - 2400000.5
    return jd, mjd


def process(input_path,
            output_path,
            output_name,
            field_id,
            common_fields):
    str_error = None
    common_fields_values = common_fields.split(CONST_COMMON_FIELDS_STRING_SEPARATOR)
    for i in range(len(common_fields_values)):
        common_fields_values[i] = common_fields_values[i].lower()
    if not exists(input_path):
        str_error = ("Error:\nInput path does not exists:\n{}".format(input_path))
        return str_error
    if not exists(output_path):
        os.mkdir(output_path)
        if not exists(output_path):
            str_error = ("Error:\nOutput path does not exists and error making it:\n{}".format(output_path))
            return str_error
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    shp_files = []
    for file in files:
        if file.endswith(".SHP") or file.endswith(".shp"):
            file_base_name = os.path.splitext(os.path.basename(file))[0]
            file_path = input_path + "\\" + file
            file_path = os.path.normpath(file_path)
            shp_files.append(file_path)
    if len(shp_files) == 0:
        str_error = ("Error:\nThere are no shapefiles files in input path:\n{}".format(input_path))
        return str_error
    cont = 0
    driver = ogr.GetDriverByName('ESRI Shapefile')
    values_by_id_by_date_by_type = {}
    fields_values_by_id_by_field_name = {}
    print('Adding fields from input shapefiles:')
    for input_shp in shp_files:
        print('Processing file: {}'.format(input_shp))
        input_shp_basename = os.path.splitext(os.path.basename(input_shp))[0]
        input_shp_basename_values = input_shp_basename.split(CONST_FIELD_IN_SHAPEFILE_BASENAME_STRING_SEPARATOR)
        if len(input_shp_basename_values) < (CONST_FIELD_IN_SHAPEFILE_DATE_POSITION-1):
            str_error = "Function process"
            str_error += "\nError in dataset file:\n{}".format(input_shp)
            str_error += "\nthere are no enough fields separated by {}".format(CONST_FIELD_IN_SHAPEFILE_BASENAME_STRING_SEPARATOR)
            return str_error
        str_date = '20' + input_shp_basename_values[CONST_FIELD_IN_SHAPEFILE_DATE_POSITION-1]
        in_vec_ds = None
        try:
            in_vec_ds = driver.Open(input_shp, 0)  # 0 means read-only. 1 means writeable.
        except ValueError:
            str_error = "Function process"
            str_error += "\nError opening dataset file:\n{}".format(input_shp)
            return str_error
        in_layer = in_vec_ds.GetLayer()
        in_crs = in_layer.GetSpatialRef()
        in_crs_wkt = in_crs.ExportToWkt()
        in_geometry_type = in_layer.GetGeomType()
        if in_geometry_type != ogr.wkbPolygon \
                and in_geometry_type != ogr.wkbMultiPolygon \
                and in_geometry_type != ogr.wkbPolygonM and in_geometry_type != ogr.wkbPolygonZM:
            str_error = "Function process"
            str_error += "\nNot Polygon geometry type in file:\n{}".format(input_shp)
            return str_error
        in_layer_definition = in_layer.GetLayerDefn()
        input_field_id_index = in_layer_definition.GetFieldIndex(field_id)
        if not input_field_id_index:
            str_error = "Function process"
            str_error += "\nNot common field name: {} in file:\n{}".format(field_id, input_shp)
            return str_error
        for feature in in_layer:
            id = feature[field_id]
            id_str = str(id)
            for i in range(in_layer_definition.GetFieldCount()):
                field_name = in_layer_definition.GetFieldDefn(i).GetName()
                if field_name.lower() not in common_fields_values:
                    if not id in values_by_id_by_date_by_type:
                        values_by_id_by_date_by_type[id] = {}
                    if not id in fields_values_by_id_by_field_name:
                        fields_values_by_id_by_field_name[id] = {}
                    value = feature[field_name]
                    # str_value_name = field_name.replace('_', '')
                    str_value = None
                    if field_name == CONST_SHP_COUNT_HEADER:
                        str_value_name = CONST_CSV_COUNT_HEADER
                        str_value = '0'
                        if value:
                            str_value = "{:.0f}".format(value)
                    elif field_name == CONST_SHP_MEAN_HEADER:
                        str_value_name = CONST_CSV_NDVI_MEAN_HEADER
                        str_value = '0.000'
                        if value:
                            str_value = "{:.3f}".format(value)
                    elif field_name == CONST_SHP_STD_HEADER:
                        str_value_name = CONST_CSV_NDVI_STD_HEADER
                        str_value = '0.000'
                        if value:
                            str_value = "{:.3f}".format(value)
                    if not str_value:
                        continue
                    if not str_date in values_by_id_by_date_by_type[id]:
                        values_by_id_by_date_by_type[id][str_date] = {}
                    values_by_id_by_date_by_type[id][str_date][str_value_name] = str_value
        in_vec_ds = None
        cont = cont + 1
    print('Writing CSV results ...')
    for id in values_by_id_by_date_by_type:
        str_id = str(id)
        output_csv = os.path.normpath(output_path + '\\' + output_name + '_' + str_id + '.csv')
        if exists(output_csv):
            os.remove(output_csv)
            if exists(output_csv):
                str_error = ("Error removing existing output CSV:\n{}".format(output_csv))
                return str_error
        output_graph =  os.path.normpath(output_path + '\\' + output_name + '_'  + str_id + '.png')
        if exists(output_graph):
            os.remove(output_graph)
            if exists(output_graph):
                str_error = ("Error removing existing output graph file:\n{}".format(output_graph))
                return str_error
        file_csv = None
        try:
            file_csv = open(output_csv, "w")
        except IOError:
            str_error = ("Error opening output CSV:\n{}".format(output_csv))
            return str_error
        x = []
        y = []
        file_csv.write('%s,%s,%s,%s\n'%(CONST_CSV_DATE_HEADER, CONST_CSV_COUNT_HEADER, CONST_CSV_NDVI_MEAN_HEADER, CONST_CSV_NDVI_STD_HEADER))
        for date in values_by_id_by_date_by_type[id]:
            str_count = values_by_id_by_date_by_type[id][date][CONST_CSV_COUNT_HEADER]
            str_mean = values_by_id_by_date_by_type[id][date][CONST_CSV_NDVI_MEAN_HEADER]
            str_std = values_by_id_by_date_by_type[id][date][CONST_CSV_NDVI_STD_HEADER]
            file_csv.write('%s,%s,%s,%s\n'%(date, str_count, str_mean, str_std))
            x.append(date)
            y.append(float(str_mean))
        file_csv.close()
        plt.plot(x, y, color='g', linestyle='dashed', marker='o', label="NDVI time series")
        plt.xticks(rotation=90)
        plt.xlabel('Dates')
        plt.ylabel('NDVI')
        plt.title('NDVI time series', fontsize=10)
        plt.grid()
        plt.legend()
        plt.savefig(output_graph, bbox_inches='tight')
        plt.close()
    return str_error

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", help="Input path", type=str)
    parser.add_argument("--output_path", help="Output path", type=str)
    parser.add_argument("--output_name", help="Output name", type=str)
    parser.add_argument("--field_id", help="Field id", type=str)
    parser.add_argument("--common_fields", help="Common fields", type=str)
    # parser.add_argument("--output_path", type=str,
    #                     help="Output path or empty for multispectral orthomosaic path")
    args = parser.parse_args()
    if not args.input_path:
        parser.print_help()
        return
    input_path = args.input_path
    if not args.output_path:
        parser.print_help()
        return
    output_path = args.output_path
    if not args.output_name:
        parser.print_help()
        return
    output_name = args.output_name
    if not args.field_id:
        parser.print_help()
        return
    field_id = args.field_id
    if not args.common_fields:
        parser.print_help()
        return
    common_fields = args.common_fields
    str_error = process(input_path,
                        output_path,
                        output_name,
                        field_id,
                        common_fields)
    if str_error:
        print("Error:\n{}".format(str_error))
        return
    print("... Process finished", flush=True)


if __name__ == '__main__':
    err = GdalErrorHandler()
    gdal.PushErrorHandler(err.handler)
    gdal.UseExceptions()  # Exceptions will get raised on anything >= gdal.CE_Failure
    assert err.err_level == gdal.CE_None, 'the error level starts at 0'
    main()
