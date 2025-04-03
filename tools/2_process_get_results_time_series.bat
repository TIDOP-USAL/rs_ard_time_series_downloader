@echo off
SETLOCAL
set OSGEO4W_ROOT=C:/Program Files/QGIS 3.34.11
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
set input_path="C:\PrTeledeteccion\Sentinel_2_L2A\output_shapefiles"
set output_path="C:\PrTeledeteccion\resultados"
set output_name="prTeledeteccion_2_0"
set field_id="id"
set common_fields="id;IdAlumno"
echo on
python .\process_time_series.py --input_path %input_path% --output_path %output_path% --output_name %output_name% --field_id %field_id% --common_fields %common_fields%
@echo off
ENDLOCAL