Expresiones a utilizar para obtener los campos en el procesamiento en modo batch.

Plot id value for selection
to_int(replace(regexp_substr(@ndvi, '.*/(.*)/'),'_NDVI',''))

output_shapefile
'C:\\PrTeledeteccion\\Sentinel_2_L2A\\output_shapefiles\\' + replace(regexp_substr(@ndvi, '.*/(.*)/'),'_NDVI','') + '_' + replace(left(right(@ndvi,13),8),'-','') + '.shp'
