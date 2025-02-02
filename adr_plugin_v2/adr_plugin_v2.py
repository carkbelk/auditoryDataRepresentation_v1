# -*- coding: utf-8 -*-
"""
/***************************************************************************
 adr_plugin
                                 A QGIS plugin
 Version 2 of ADR QGIS Plugin
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-04-28
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Carley Belknap and J. Mitchell Green
        email                : belknacc@dukes.jmu.edu and green3jm@dukes.jmu.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsPointXY, QgsRaster, QgsRasterBandStats, QgsProject
import subprocess
import os
import sys
import random
import math

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .adr_plugin_v2_dialog import adr_pluginDialog
import os.path


class adr_plugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'adr_plugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ADR Plugin')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('adr_plugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/adr_plugin_v1/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ADR'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ADR Plugin'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that identifies user click on QGIS canvas and sends point to display_point function"""
        #calls Class from adr_plugin_v2_dialog.py 
        self.dlg = adr_pluginDialog()
        self.dlg.show()
        self.canvas = self.iface.mapCanvas()
        #creates the info cursor for the current map canvas
        self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        #Sets the map tool.
        self.mapTool = self.canvas.setMapTool(self.emitPoint)
        #Triggers the display_point function every time the map is clicked on
        click = self.emitPoint.canvasClicked.connect(self.display_point)
        
    def display_point(self,emitPoint):
        """Everytime the user clicks, produces sound (via external program spiano) from map"""
        #Takes coordinates from run function.
        self.coord_x = emitPoint.x()
        self.coord_y = emitPoint.y()
        #Transform click point from map coords (in string form) to QgsPointXY format.
        self.transform = QgsPointXY(self.coord_x,self.coord_y)

        #Retrieves normalization ranges and hearability data from dialog object.
        normalizationVals, layer_hearable, band_hearable = self.dlg.getAllInputs() 
        #print(self.dlg.getAllInputs())

        #Retrieves all of the layers in the project.
        self.layers = QgsProject.instance().layerTreeRoot().children()

        #Data structure to hold the data values which will be converted to sound.
        data_values = []

        #Loops through and gets the data point value from each hearable layer/band.
        for layer in self.layers:
            layer_name = layer.name()
            layer = layer.layer()
            #If layer is hearable...
            if layer_hearable[layer_name]:
                #For each band in the layer...
                for band_index in range(len(band_hearable[layer_name])):
                    #Band numbers in QGIS are indexed starting at 1, not 0. This variable is used whenever accessing a band using a library function.
                    band_num = band_index + 1
                    band_name = layer.bandName(band_num)
                    #If band is hearable...
                    if band_hearable[layer_name][band_index]:
                        #Retrieves the data at the clicked location for the band.
                        val, result = layer.dataProvider().sample(self.transform, band_num)
                        #Prints the value of the band at the clicked location.
                        print("Layer:", layer_name, "  Band:", band_name, "  Value:", val)
                        #If the value is valid...
                        if not math.isnan(val):
                            #Retrieves the statistics data about the band.
                            stats = layer.dataProvider().bandStatistics(band_num, QgsRasterBandStats.All)

                            #Grabs the min and max value to normalize the data to.
                            normalized_min = normalizationVals[layer_name][band_name][0]
                            normalized_max = normalizationVals[layer_name][band_name][1]

                            #Mathmatics for normalizing the sound data. Uses feature scaling, also called min-max normalization.
                            normalized_val = normalized_min + (((val - stats.minimumValue) * (normalized_max-normalized_min)) / (stats.maximumValue-stats.minimumValue))
                            normalized_val = round(normalized_val)
                                
                            #Add value to the list of data to be converted to sound.
                            data_values.append(normalized_val)
       
        #Prints all of the values that will be outputed to the named pipe.
        print("Sound Values", data_values, "\n")

        #Path for creating a named pipe.   
        path = "/tmp/myfifo" 

        if len(data_values) > 0:
            #Checks if path exists, creates new path
            if not os.path.exists(path):
                os.mkfifo(path)
            #Writes to 'named pipe' with the list of data values.
            with open(path,'w') as f:
                #Process data values to be printed on a single line.
                data_values = [str(i) for i in data_values]
                s = " ".join(data_values)
                #Writes to the named pipe.
                f.write(s)
                f.flush()
                f.close()


        
