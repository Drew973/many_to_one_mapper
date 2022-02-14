# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ManyToOneMapper
                                 A QGIS plugin
 plugin to make csv mapping many features of layer to another layer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-04-08
        copyright            : (C) 2021 by Drew
        email                : drew.bennett@ptsinternational.co.uk
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
    """Load ManyToOneMapper class from file ManyToOneMapper.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .many_to_one_mapper import ManyToOneMapper
    return ManyToOneMapper(iface)