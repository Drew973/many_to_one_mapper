# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'many_to_one_mapper_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_manyToOneMapperDockWidgetBase(object):
    def setupUi(self, manyToOneMapperDockWidgetBase):
        manyToOneMapperDockWidgetBase.setObjectName("manyToOneMapperDockWidgetBase")
        manyToOneMapperDockWidgetBase.resize(973, 815)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainWidget = QtWidgets.QWidget(self.dockWidgetContents)
        self.mainWidget.setObjectName("mainWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.mainWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lastButton = QtWidgets.QPushButton(self.mainWidget)
        self.lastButton.setObjectName("lastButton")
        self.horizontalLayout.addWidget(self.lastButton)
        self.featuresBox = featureWidget(self.mainWidget)
        self.featuresBox.setObjectName("featuresBox")
        self.horizontalLayout.addWidget(self.featuresBox)
        self.nextButton = QtWidgets.QPushButton(self.mainWidget)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout.addWidget(self.nextButton)
        self.fromLayerButton = QtWidgets.QPushButton(self.mainWidget)
        self.fromLayerButton.setObjectName("fromLayerButton")
        self.horizontalLayout.addWidget(self.fromLayerButton)
        self.zoomBox = QtWidgets.QCheckBox(self.mainWidget)
        self.zoomBox.setChecked(True)
        self.zoomBox.setObjectName("zoomBox")
        self.horizontalLayout.addWidget(self.zoomBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.view = QtWidgets.QTableView(self.mainWidget)
        self.view.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.view.setObjectName("view")
        self.verticalLayout_2.addWidget(self.view)
        self.verticalLayout.addWidget(self.mainWidget)
        manyToOneMapperDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(manyToOneMapperDockWidgetBase)
        QtCore.QMetaObject.connectSlotsByName(manyToOneMapperDockWidgetBase)

    def retranslateUi(self, manyToOneMapperDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        manyToOneMapperDockWidgetBase.setWindowTitle(_translate("manyToOneMapperDockWidgetBase", "Many to One Mapper"))
        self.lastButton.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>Go to previous feature</p></body></html>"))
        self.lastButton.setText(_translate("manyToOneMapperDockWidgetBase", "<"))
        self.featuresBox.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>Current feature</p></body></html>"))
        self.nextButton.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>Go to next feature</p></body></html>"))
        self.nextButton.setText(_translate("manyToOneMapperDockWidgetBase", ">"))
        self.fromLayerButton.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>Set Value from selected feature of layer.</p></body></html>"))
        self.fromLayerButton.setText(_translate("manyToOneMapperDockWidgetBase", "From Layer"))
        self.zoomBox.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>Select features on layers and zoom to them when feature changed.</p></body></html>"))
        self.zoomBox.setText(_translate("manyToOneMapperDockWidgetBase", "Zoom on change"))
        self.view.setToolTip(_translate("manyToOneMapperDockWidgetBase", "<html><head/><body><p>id and join field for features of join layer mapped to current feature of layer.</p><p>Right click for options to add and remove.</p><p><br/></p></body></html>"))
from .widgets.featuresWidget import featureWidget