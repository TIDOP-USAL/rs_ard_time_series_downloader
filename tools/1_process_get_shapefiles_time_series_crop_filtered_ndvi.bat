@echo off
SETLOCAL
set OSGEO4W_ROOT=C:/Program Files/QGIS 3.34.11
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
set input_json="C:/PrTeledeteccion/resultados/configuracion_proceso_0.json"
echo on
python .\TimeSeriesCropFilteredNDVI.py --input_json %input_json%
@echo off
ENDLOCAL