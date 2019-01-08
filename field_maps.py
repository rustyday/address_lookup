# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MakeFieldMaps
                                 A QGIS plugin
 Makes Field Maps for Site Classifications
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-01-01
        git sha              : $Format:%H$
        copyright            : (C) 2019 by David
        email                : david@tasmangeotechnics.com.au
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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject, QgsPointXY, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsLayoutItemMap, \
    QgsPrintLayout, QgsLayoutSize, QgsUnitTypes, QgsReadWriteContext, QgsRectangle
from qgis.gui import QgsMessageBar
from qgis.PyQt.QtXml import QDomDocument
from qgis.PyQt.QtCore import QFile, QIODevice

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .field_maps_dialog import MakeFieldMapsDialog
import os.path
import sys
import os


def resolve_file(name, basepath=None):
    if not basepath:
      basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath)


filep = resolve_file('address_parser.py')

sys.path.append(filep)
import address_parser

results = {}
pt = QgsPointXY(0.0, 0.0)

class MakeFieldMaps:
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
            'MakeFieldMaps_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Make Field Maps')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.dlg = MakeFieldMapsDialog()
        self.dlg.lineEdit.clear()

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
        return QCoreApplication.translate('MakeFieldMaps', message)

    def select_output_file(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ", "", '*.txt')
        self.dlg.lineEdit.setText(filename)

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
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/field_maps/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Address lookup'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Make Field Maps'),
                action)
            self.iface.removeToolBarIcon(action)

    def selectionchange(self):
        global results
        if results and self.dlg.comboBox.currentText() is not '':
            coords_tuple = results[self.dlg.comboBox.currentText()]
            coords_str = str(coords_tuple[0]) + ', ' + str(coords_tuple[1])
            self.dlg.label_3.setText(coords_str)
        else:  # dict is false it is empty
            self.dlg.label_3.setText('No data')

    def search(self):
        data_entered = self.dlg.lineEdit.text()
        if data_entered == '':
            self.iface.messageBar().pushCritical("Error", "The search field cannot be blank")
        else:
            global results
            results = address_parser.main(data_entered)  # note this is a dictionary - address is key, coords is value
            if not results is None:
                self.dlg.comboBox.clear()  # remove old items if present
                if results:
                    self.dlg.comboBox.addItems(list(results.keys()))
                    self.dlg.comboBox.currentIndexChanged.connect(self.selectionchange)
                    self.selectionchange()
                    self.dlg.pushButton_2.clicked.connect(self.go)
                    self.dlg.pushButton_3.clicked.connect(self.make_layout)
                else:
                    self.dlg.comboBox.addItems(['No results found'])

    def go(self):
        global results
        global pt
        if results:
            coords_tuple = results[self.dlg.comboBox.currentText()]
            new_point = QgsPointXY(coords_tuple[0], coords_tuple[1])
            transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem("EPSG:4326"),
                                               QgsCoordinateReferenceSystem("EPSG:28355"), QgsProject.instance())
            pt = transform.transform(new_point.x(), new_point.y())
            self.iface.mapCanvas().setCenter(pt)
            self.iface.mapCanvas().refreshAllLayers()

    def make_layout(self):
        projectInstance = QgsProject.instance()
        manager = projectInstance.layoutManager()
        # make a new print layout object
        layout = QgsPrintLayout(projectInstance)
        # needs to call this according to API documentaiton
        # layout.initializeDefaults()  - no, because loading from template
        # load from template

        global filep
        global pt
        filename = filep + '/a4_portrait_500.qpt'
        file = QFile(filename)
        if file.open(QIODevice.ReadOnly):
            document = QDomDocument()
            readok = document.setContent(file)  # content is .qpt file content
            loaded = layout.loadFromTemplate(document, QgsReadWriteContext())
            refmap = layout.referenceMap()
            # note scaling here works for 1:500 and this particular template only
            xmin = pt.x() - 45.0375
            ymin = pt.y() - 56.7855
            xmax = pt.x() + 45.0375
            ymax = pt.y() + 56.7855
            # set extent
            bb = QgsRectangle(xmin, ymin, xmax, ymax)
            refmap.setExtent(bb)
        else:
            print('failed')
        layout.setName('console')
        # remove old layouts
        for item in manager.layouts():
            manager.removeLayout(item)
        # add new layout to manager
        manager.addLayout(layout)
        # create a map item to add
        # itemMap = QgsLayoutItemMap.create(layout)
        # add some settings

        # using ndawson's answer below, do this before setting extent
        # itemMap.attemptResize(QgsLayoutSize(6, 4, QgsUnitTypes.LayoutInches))
        # set an extent
        # itemMap.setExtent(self.iface.mapCanvas().extent())
        # add the map to the layout
        # layout.addLayoutItem(itemMap)

    def run(self):
        """Run method that performs all the real work"""

        # layers = [tree_layer.layer() for tree_layer in QgsProject.instance().layerTreeRoot().findLayers()]
        # layer_list = []
        # for layer in layers:
        #     layer_list.append(layer.name())
        #     self.dlg.comboBox.addItems(layer_list)

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = MakeFieldMapsDialog()

        self.dlg.pushButton.clicked.connect(self.search)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass
            # output_file = open(filename, 'w')
            # 
            # selectedLayerIndex = self.dlg.comboBox.currentIndex()
            # selectedLayer = layers[selectedLayerIndex]
            # fields = selectedLayer.pendingFields()
            # fieldnames = [field.name() for field in fields]
            # 
            # for f in selectedLayer.getFeatures():
            #     line = ','.join(unicode(f[x]) for x in fieldnames) + '\n'
            #     unicode_line = line.encode('utf-8')
            #     output_file.write(unicode_line)
            # output_file.close()
