# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

# Docs: https://www.qgistutorials.com/es/docs/running_qgis_jobs.html
import argparse
from osgeo import gdal, osr, ogr
import os, sys
import json
import shutil
from os.path import exists

from qgis.core import *
qgs = QgsApplication([], False)
qgs.initQgis()
qgis_prefix_path = os.environ["QGIS_PREFIX_PATH"]
qgis_python_plugins_path = os.path.normpath(qgis_prefix_path + "\\python\\plugins")
sys.path.append(qgis_python_plugins_path)
import processing
from processing.core.Processing import Processing
Processing.initialize()

CONST_PARAMETERS_TAG = 'PARAMETERS'
CONST_OUTPUTS_TAG = 'OUTPUTS'
CONST_BANDS_TAG = 'bands'
CONST_NDVI_TAG = 'ndvi'
CONST_PLOT_ID_ATTRIBUTE_NAME_TAG = 'plot_id_attribute_name'
CONST_PLOT_ID_VALUE_FOR_SELECTION_TAG = 'plot_id_value_for_selection'
CONST_PLOTS_TAG = 'plots'
CONST_OUTPUT_SHAPEFILE_TAG = 'output_shapefile'

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

def process(input_json):
    str_error = None
    if not exists(input_json):
        str_error = ("Error:\nInput JSON does not exists:\n{}".format(input_json))
        return str_error
    with open(input_json) as f:
        json_content = json.load(f)
    if not isinstance(json_content, list):
        str_error = ("\nInput JSON:\n{}".format(input_json))
        str_error += ("\nError:\nContent is not a list")
        return str_error
    for i in range(len(json_content)):
        print('Processing {}/{}'.format(str(i+1), str(len(json_content))))
        parameters = json_content[i][CONST_PARAMETERS_TAG]
        if not isinstance(parameters, dict):
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nContent is not a dictionary")
            return str_error
        if not CONST_BANDS_TAG in parameters:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_BANDS_TAG))
            return str_error
        bands = parameters[CONST_BANDS_TAG]
        bands = bands.replace("'", "")
        if not CONST_NDVI_TAG in parameters:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_NDVI_TAG))
            return str_error
        ndvi = parameters[CONST_NDVI_TAG]
        ndvi = ndvi.replace("'", "")
        if not CONST_PLOT_ID_ATTRIBUTE_NAME_TAG in parameters:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_PLOT_ID_ATTRIBUTE_NAME_TAG))
            return str_error
        plot_id_attribute_name = parameters[CONST_PLOT_ID_ATTRIBUTE_NAME_TAG]
        plot_id_attribute_name = plot_id_attribute_name.replace("'", "")
        if not CONST_PLOT_ID_VALUE_FOR_SELECTION_TAG in parameters:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_PLOT_ID_VALUE_FOR_SELECTION_TAG))
            return str_error
        plot_id_value_for_selection = parameters[CONST_PLOT_ID_VALUE_FOR_SELECTION_TAG]
        plot_id_value_for_selection = plot_id_value_for_selection.replace("'", "")
        if not CONST_PLOTS_TAG in parameters:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_PARAMETERS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_PLOTS_TAG))
            return str_error
        plots = parameters[CONST_PLOTS_TAG]
        plots = plots.replace("'", "")
        outputs = json_content[i][CONST_OUTPUTS_TAG]
        if not isinstance(outputs, dict):
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_OUTPUTS_TAG, str(i+1)))
            str_error += ("\nError:\nContent is not a dictionary")
            return str_error
        if not CONST_OUTPUT_SHAPEFILE_TAG in outputs:
            str_error = ("\nInput JSON:\n{}".format(input_json))
            str_error += ("\nFor {} value: {} in list".format(CONST_OUTPUTS_TAG, str(i+1)))
            str_error += ("\nError:\nNot contains: {}".format(CONST_OUTPUT_SHAPEFILE_TAG))
            return str_error
        output_shapefile = outputs[CONST_OUTPUT_SHAPEFILE_TAG]
        output_shapefile = output_shapefile.replace("'", "")

        results = {}
        outputs = {}
        ctx = QgsProcessingContext()
        feedback = QgsProcessingFeedback()
        # Plot selection by id
        alg_params = {
            'FIELD': plot_id_attribute_name,
            'INPUT': plots,
            'OPERATOR': 0,  # =
            'VALUE': plot_id_value_for_selection,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PlotSelectionById'] = processing.run('native:extractbyattribute',
                                                      alg_params, context=ctx,
                                                      feedback=feedback,
                                                      is_child_algorithm=True)

        # NDVI Vegetation
        alg_params = {
            'CELL_SIZE': None,
            'CRS': None,
            'EXPRESSION': 'IF ("A@3"=4 OR "A@3"=5, "B@1" , 0/0)',
            'EXTENT': None,
            'LAYERS': [bands,ndvi],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NdviVegetation'] = processing.run('native:modelerrastercalc',
                                                   alg_params, context=ctx,
                                                   feedback=feedback,
                                                   is_child_algorithm=True)

        # Plots Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': -10,
            'END_CAP_STYLE': 2,  # Cuadrado
            'INPUT': outputs['PlotSelectionById']['OUTPUT'],
            'JOIN_STYLE': 1,  # Inglete
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PlotsBuffer'] = processing.run('native:buffer',
                                                alg_params, context=ctx,
                                                feedback=feedback,
                                                is_child_algorithm=True)

        # zonal statistics
        alg_params = {
            'INPUT': outputs['PlotsBuffer']['OUTPUT'],
            'INPUT_RASTER': outputs['NdviVegetation']['OUTPUT'],
            'RASTER_BAND': 1,
            'STATISTICS': [0,2,4],  # Número,Media,Desv. est.
            'OUTPUT': output_shapefile
        }
        outputs['EstadisticasDeZona'] = processing.run('native:zonalstatisticsfb',
                                                       alg_params, context=ctx,
                                                       feedback=feedback,
                                                       is_child_algorithm=True)
        results['Output_shapefile'] = outputs['EstadisticasDeZona']['OUTPUT']
    return str_error

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_json", help="Input JSON", type=str)
    args = parser.parse_args()
    if not args.input_json:
        parser.print_help()
        return
    input_json = args.input_json
    str_error = process(input_json)
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

