# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MakeFieldMaps
                                 A QGIS plugin
 Makes Field Maps for Site Classifications
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-01-01
        copyright            : (C) 2019 by David
        email                : david@tasmangeotechnics.com.au
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
    """Load MakeFieldMaps class from file MakeFieldMaps.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .field_maps import MakeFieldMaps
    return MakeFieldMaps(iface)
