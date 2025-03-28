# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

# import optparse
import argparse
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


def process(input_path,
            output_shp,
            common_field_name,
            prefix_fields_to_join,
            minimum_pixel_count):
    str_error = None
    if not exists(input_path):
        str_error = ("Error:\nInput path does not exists:\n{}".format(input_path))
        return str_error
    files = [f for f in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, f))]
    shp_files = []
    for file in files:
        if file.endswith(".SHP") or file.endswith(".shp"):
            file_base_name = os.path.splitext(os.path.basename(file))[0]
            file_path = input_path + "\\" + file
            file_path = os.path.normpath(file_path)
            if file_path != os.path.normpath(output_shp):
                shp_files.append(file_path)
    if len(shp_files) == 0:
        str_error = ("Error:\nThere are no shapefiles files in input path:\n{}".format(input_path))
        return str_error
    cont = 0
    driver = ogr.GetDriverByName('ESRI Shapefile')
    out_vec_ds = None
    out_layer = None
    for input_shp in shp_files:
        if cont == 0:
            str_error = copy_shapefile(input_shp, output_shp)
            if str_error:
                print("Error:\n{}".format(str_error))
                return
            try:
                out_vec_ds = driver.Open(output_shp, 1)  # 0 means read-only. 1 means writeable.
            except ValueError:
                str_error = "Function process"
                str_error += "\nError opening dataset file:\n{}".format(output_shp)
                return str_error
            out_layer = out_vec_ds.GetLayer()
            out_crs = out_layer.GetSpatialRef()
            out_crs_wkt = out_crs.ExportToWkt()
            out_geometry_type = out_layer.GetGeomType()
            if out_geometry_type != ogr.wkbPolygon \
                    and out_geometry_type != ogr.wkbMultiPolygon \
                    and out_geometry_type != ogr.wkbPolygonM and out_geometry_type != ogr.wkbPolygonZM:
                str_error = "Function process"
                str_error += "\nNot Polygon geometry type in file:\n{}".format(output_shp)
                return str_error
            out_layer_definition = out_layer.GetLayerDefn()
            output_field_id_index = out_layer_definition.GetFieldIndex(common_field_name)
            if not output_field_id_index:
                str_error = "Function process"
                str_error += "\nNot common field name: {} in file:\n{}".format(common_field_name, output_shp)
                return str_error
            cont = cont + 1
            continue
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
        input_field_id_index = in_layer_definition.GetFieldIndex(common_field_name)
        if not input_field_id_index:
            str_error = "Function process"
            str_error += "\nNot common field name: {} in file:\n{}".format(common_field_name, input_shp)
            return str_error
        for feature in in_layer:
            id = feature.GetFieldAsDouble(common_field_name)
            for out_feature in out_layer:
                out_id = out_feature.GetFieldAsDouble(common_field_name)
                if out_id == id:
                    for i in range(in_layer_definition.GetFieldCount()):
                        field_name = in_layer_definition.GetFieldDefn(i).GetName()
                        if field_name.startswith(prefix_fields_to_join):
                            out_layer.CreateField(in_layer_definition.GetFieldDefn(i))#ogr.OFTReal))
                            value = None
                            if in_layer_definition.GetFieldDefn(i).GetType() == ogr.OFTInteger:
                                value = feature.GetFieldAsInteger(i)
                            elif in_layer_definition.GetFieldDefn(i).GetType() == ogr.OFTReal:
                                value = feature.GetFieldAsDouble(i)
                            elif in_layer_definition.GetFieldDefn(i).GetType() == ogr.OFTString:
                                value = feature.GetFieldAsString(i)
                            else:
                                value = feature.GetFieldAsString(i)
                            value = out_feature[field_name]
                            out_feature.SetField(field_name, value)
                    out_layer.SetFeature(out_feature)
            out_layer.ResetReading()
        cont = cont + 1
    return str_error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", help="Input path", type=str)
    parser.add_argument("--output_shapefile", help="Output shapefile", type=str)
    parser.add_argument("--common_field_name", help="Common field name", type=str)
    parser.add_argument("--prefix_fields_to_join", help="Prefix fields names to join", type=str)
    parser.add_argument("--minimum_pixel_count", type=int, help="Minimmum pixel count")
    # parser.add_argument("--output_path", type=str,
    #                     help="Output path or empty for multispectral orthomosaic path")
    args = parser.parse_args()
    if not args.input_path:
        parser.print_help()
        return
    input_path = args.input_path
    if not args.output_shapefile:
        parser.print_help()
        return
    output_shapefile = args.output_shapefile
    if not args.common_field_name:
        parser.print_help()
        return
    common_field_name = args.common_field_name
    if not args.prefix_fields_to_join:
        parser.print_help()
        return
    prefix_fields_to_join = args.prefix_fields_to_join
    if not args.minimum_pixel_count:
        parser.print_help()
        return
    minimum_pixel_count = args.minimum_pixel_count
    str_error = process(input_path,
                        output_shapefile,
                        common_field_name,
                        prefix_fields_to_join,
                        minimum_pixel_count)
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
