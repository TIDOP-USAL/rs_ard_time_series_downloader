"""
Model exported as python.
Name : CropFilteredNDVI
Group : Herramientas de archivo
With QGIS : 33411
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
import processing


class Cropfilteredndvi(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('bands', 'BANDS', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('ndvi', 'NDVI', defaultValue=None))
        self.addParameter(QgsProcessingParameterString('plot_id_attribute_name', 'Plot id attribute name', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterNumber('plot_id_value_for_selection', 'Plot id value for selection', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=10000, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('plots', 'Plots', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Output_shapefile', 'output_shapefile', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        # Plot selection by id
        alg_params = {
            'FIELD': parameters['plot_id_attribute_name'],
            'INPUT': parameters['plots'],
            'OPERATOR': 0,  # =
            'VALUE': parameters['plot_id_value_for_selection'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PlotSelectionById'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # NDVI Vegetation
        alg_params = {
            'CELL_SIZE': None,
            'CRS': None,
            'EXPRESSION': 'IF ("A@3"=4 OR "A@3"=5, "B@1" , 0/0)',
            'EXTENT': None,
            'LAYERS': [parameters['bands'],parameters['ndvi']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NdviVegetation'] = processing.run('native:modelerrastercalc', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

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
        outputs['PlotsBuffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Estadisticas de zona
        alg_params = {
            'INPUT': outputs['PlotsBuffer']['OUTPUT'],
            'INPUT_RASTER': outputs['NdviVegetation']['OUTPUT'],
            'RASTER_BAND': 1,
            'STATISTICS': [0,2,4],  # Número,Media,Desv. est.
            'OUTPUT': parameters['Output_shapefile']
        }
        outputs['EstadisticasDeZona'] = processing.run('native:zonalstatisticsfb', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Output_shapefile'] = outputs['EstadisticasDeZona']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Cambiar nombre de capa
        alg_params = {
            'INPUT': QgsExpression(' @Estadisticas_de_zona_OUTPUT ').evaluate(),
            'NAME': QgsExpression("replace(left(right(layer_property(@ndvi, 'name'),11),8),'-','')").evaluate()
        }
        outputs['CambiarNombreDeCapa'] = processing.run('native:renamelayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'CropFilteredNDVI'

    def displayName(self):
        return 'CropFilteredNDVI'

    def group(self):
        return 'Herramientas de archivo'

    def groupId(self):
        return 'Herramientas de archivo'

    def createInstance(self):
        return Cropfilteredndvi()
