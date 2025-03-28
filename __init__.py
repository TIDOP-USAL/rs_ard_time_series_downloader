# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RemoteSensingARDTimeSeriesDownloader
                                 A QGIS plugin
 Remote Sensing ARD time series downloader using OPENEO
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-04-01
        copyright            : (C) 2025 by David Hernández López
        email                : david.hernandez@uclm.es
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ForestFireSeverityEstimation class from file ForestFireSeverityEstimation.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rs_ard_time_series_downloader import RemoteSensingARDTimeSeriesDownloader
    return RemoteSensingARDTimeSeriesDownloader(iface)
