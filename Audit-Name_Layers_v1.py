######################################### General Info #########################################
# Written by: Jessica Wood w/ Meghan Beckmann, for KAA Design Group                            #
# Date Created: 09/2022                                                                        #
#                                                                                              #
# Description:                                                                                 #
# This script checks the naming convention of all layers in a project. It will iterate         #
# over all layers in a project and check if the naming convention complies to KAA              #
# standards.                                                                                   #
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

# Print Info begin Auditing
print("Begin Auditing for Layer Names.")

# Keep track of whether there is an error
hasError = False

# Get Layers and names
layerAttributes = acc.GetAttributesByType("Layer")
layAttr = acc.GetLayerAttributes(layerAttributes)

# iterate the layers and check the names
for layer in layAttr:
    if (layer.layerAttribute.name == "Archicad Layer"):
        continue
    if (layer.layerAttribute.name[0] == "A" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "L" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "G" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "M" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "P" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "E" and layer.layerAttribute.name[1] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "S" and layer.layerAttribute.name[1] == "-"):
        continue
    elif ((layer.layerAttribute.name[0] == "S" or layer.layerAttribute.name[0] == "Z") and layer.layerAttribute.name[1] == "9"):
        continue
    elif (layer.layerAttribute.name[0] == "9" and layer.layerAttribute.name[1] == " " and layer.layerAttribute.name[2] == "|"):
        continue
    elif (layer.layerAttribute.name[0] == "L" and layer.layerAttribute.name[1] == "T" and layer.layerAttribute.name[2] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "O" and layer.layerAttribute.name[1] == "P" and layer.layerAttribute.name[2] == "T" and layer.layerAttribute.name[3] == "I" and layer.layerAttribute.name[4] == "O" and layer.layerAttribute.name[5] == "N" and layer.layerAttribute.name[6] == "-"):
        continue
    elif (layer.layerAttribute.name[0] == "N" and layer.layerAttribute.name[1] == "P" and layer.layerAttribute.name[2] == "L" and layer.layerAttribute.name[3] == "T"):
        continue
    elif ((layer.layerAttribute.name[0] == "X" or layer.layerAttribute.name[0] == "Z") and layer.layerAttribute.name[1] == "-"):
        continue
    else:
        hasError = True
        print(f"Layer: {layer.layerAttribute.name} does not match the naming convention!\n")

# Print End message
if (hasError):
    print("Audit finished - please fix these names that don't match our standards!")
else:
    print("Audit finished - no errors found, hooray! Nice layer management.")

#########################################################################################################################################################################################
