######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
# Date Modified: 02/03/2023                                                                    #
#                                                                                              #
# Description:                                                                                 #
# This script organizes all layers in a project into different folders. It iterates over all   #
# layers and places it into the given folder based on the name of the layer.                   #
################################################################################################




############ Archicad Connection #############
from archicad import ACConnection
from typing import List, Tuple, Iterable
from itertools import cycle
import copy
import math

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities
##############################################




################################################################################## BEGIN LOGIC ##################################################################################

# Create lists of different layers
architectural = []
landscape = []
general = []
engineering = []
option = []
nplt = []
context = []
structural = []
non_compliant = []

# Organize layer attributes
layerAttributes = acc.GetAttributesByType("Layer")
layAttr = acc.GetLayerAttributes(layerAttributes)

allLayers = list(zip(layerAttributes, layAttr))

# Iterate all attributes and place them in the given folder (checks each character)
for layer in allLayers:

    if (layer[1].layerAttribute.name == "Archicad Layer"):
        continue
    if (layer[1].layerAttribute.name[0] == "A" and layer[1].layerAttribute.name[1] == "-"):
        architectural.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "L" and layer[1].layerAttribute.name[1] == "-"):
        landscape.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "G" and layer[1].layerAttribute.name[1] == "-"):
        general.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "M" and layer[1].layerAttribute.name[1] == "-"):
        engineering.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "P" and layer[1].layerAttribute.name[1] == "-"):
        engineering.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "E" and layer[1].layerAttribute.name[1] == "-"):
        engineering.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "S" and layer[1].layerAttribute.name[1] == "-"):
        engineering.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "L" and layer[1].layerAttribute.name[1] == "T" and layer[1].layerAttribute.name[2] == "-"):
        engineering.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "O" and layer[1].layerAttribute.name[1] == "P" and layer[1].layerAttribute.name[2] == "T" and layer[1].layerAttribute.name[3] == "I" and layer[1].layerAttribute.name[4] == "O" and layer[1].layerAttribute.name[5] == "N" and layer[1].layerAttribute.name[6] == "-"):
        option.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "N" and layer[1].layerAttribute.name[1] == "P" and layer[1].layerAttribute.name[2] == "L" and layer[1].layerAttribute.name[3] == "T"):
        nplt.append(layer[0])
    elif ((layer[1].layerAttribute.name[0] == "X" or layer[1].layerAttribute.name[0] == "Z") and layer[1].layerAttribute.name[1] == "-"):
        context.append(layer[0])
    elif ((layer[1].layerAttribute.name[0] == "S" or layer[1].layerAttribute.name[0] == "Z") and layer[1].layerAttribute.name[1] == "9"):
        structural.append(layer[0])
    elif (layer[1].layerAttribute.name[0] == "9" and layer[1].layerAttribute.name[1] == " " and layer[1].layerAttribute.name[2] == "|"):
        structural.append(layer[0])
    else:
        non_compliant.append(layer[0])


# Folder Names
folderNames = ["ARCHITECTURAL", "LANDSCAPE", "GENERAL", "ENGINEERING", "OPTIONS", "NPLT", "CONTEXT", "STRUCTURAL RSC", "AUDIT: NON-COMPLIANT"]

# Put all attributes into a list (order of list matters, ensure the element matches the folder name)
allAttributes = [architectural, landscape, general, engineering, option, nplt, context, structural, non_compliant]

#Move attributes to DUMMY folder before starting sorting process
# Create new folder
dummyFolder = act.AttributeFolder("Layer", attributeFolderId=layAttr[0].layerAttribute.attributeId.guid, path=["DUMMY"])
acc.CreateAttributeFolders([dummyFolder])
newDummyFolder = acc.GetAttributeFolder(dummyFolder)

# Iterate Folder Names and create folders
idx = 0 # to keep track of which list to use
for folder in folderNames:
    # Create new folder
    layerFolder = act.AttributeFolder("Layer", attributeFolderId=layAttr[0].layerAttribute.attributeId.guid, path=[folder])
    acc.CreateAttributeFolders([layerFolder])
    newFolder = acc.GetAttributeFolder(layerFolder)

    print(f"Created folder: {folder}")

    attrFolderContent = acc.GetAttributeFolderContent(layerFolder)
    if (len(attrFolderContent.attributeIds) > 0):
        newDummyFolder = acc.GetAttributeFolder(dummyFolder)
        acc.MoveAttributesAndFolders([], attrFolderContent.attributeIds, newDummyFolder)

# Move appropriate attributes to the new folder
    if (len(allAttributes[idx]) > 0):
        acc.MoveAttributesAndFolders([], allAttributes[idx], newFolder)

    # Increment idx
    idx += 1

#Delete Dummy Folder
acc.DeleteAttributeFolders([dummyFolder])
#########################################################################################################################################################################################
