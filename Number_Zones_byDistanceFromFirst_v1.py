######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
#                                                                                              #
# Description:                                                                                 #
# This script generates unique ordered zone numbers. Sets the zone number                      #
# property value for all selected zones in the project. If no zones are selected, the          #
# script will set the zone number property value for all zones in the project. The             #
# script sorts the zone numbers in ascending order by distance from the user-defined zone      #
# property “First_Zone”.                                                                       #
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




############################ CONFIGURATION: By distance from Entry Zone ################################

# Get Zones
propertyId = acu.GetBuiltInPropertyId('Zone_ZoneNumber')
propertyValueStringPrefix = ''
allZoneElements = acc.GetElementsByType('Zone') # holds all zones
selectedElements = acc.GetSelectedElements() # holds selected zones

# Get property values of "Entry"
entryPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "First_Zone")
entryPropertyIdArrayItem = [act.PropertyIdArrayItem(entryPropertyId)]


###### Constant Values #####
STORY_GROUPING_LIMIT = 1   #
############################

########################################################################################################




############################################################################## FUNCTIONS ##################################################################################

def GeneratePropertyValueString(storyIndex: int, elemIndex: int) -> str:
    return f"{propertyValueStringPrefix}{storyIndex:1d}{elemIndex:02d}"


def generatePropertyValue(storyIndex: int, elemIndex: int) -> act.NormalStringPropertyValue:
    return act.NormalStringPropertyValue(GeneratePropertyValueString(storyIndex, elemIndex))


def createClusters(positions: Iterable[float], limit: float) -> List[Tuple[float, float]]:
  # Function: creates clusters based on zValues of all the Zones. Clusters represent stories

  # sort Zvalues in ascending order
    positions1 = sorted(positions) 

    if len(positions1) == 0:
        return []

    clusters = []
    posIter = iter(positions1)
    firstPos = lastPos = next(posIter)

    for pos in posIter:
        if pos - lastPos <= limit:
            lastPos = pos
        else:
            clusters.append((firstPos, lastPos))
            firstPos = lastPos = pos

    clusters.append((firstPos, lastPos))
    return clusters



def sortPositionsByDistance(positions: Iterable[Tuple[float, float, float, float, float]], entryPosition: Tuple[float, float]) -> List[Tuple[float, float, float, float, float]]:
    # Function: takes positions and the position of the entry room and returns positions sorted by their distance from the Entry room

    # sort positions by distance from entry point
    positions = sorted(positions, key=lambda e: math.dist((e[0], e[1]), entryPosition))

    # return sorted positions
    return positions

################################################################################################################################################################################




############################################################################ Begin Logic #######################################################################################

# -- positions are based on zone stamp -- #

# find bounding boxes of elements to get correct story zClusters      
boundingBoxes = acc.Get3DBoundingBoxes(allZoneElements)
elementBoundingBoxes = list(zip(allZoneElements, boundingBoxes))

# story clusters: range of (zMin, zMax) that represent each story
zClusters = createClusters((bb.boundingBox3D.zMin for bb in boundingBoxes), STORY_GROUPING_LIMIT)


# check if there are any elements selected
if (len(selectedElements) == 0):
    selected = False
    elements = acc.GetElementsByType('Zone')
    selectedBoundingBoxes = acc.Get3DBoundingBoxes(elements)
    selectedElementBoundingBoxes = list(zip(elements, boundingBoxes))
else:
    # find bounding boxes of selected zones  
    selected =  True
    elements = acc.GetSelectedElements() 
    selectedBoundingBoxes = acc.Get3DBoundingBoxes(elements)
    selectedElementBoundingBoxes = list(zip(elements, selectedBoundingBoxes))


storyIndex = 0
elemPropertyValues = []


# Iterate through each story
for (zMin, zMax) in zClusters:

    elemIndex = 1 # Counter to keep track of element number


    # find zones on the current story from all zones
    elemsOnStory = [e for e in elementBoundingBoxes if zMin <= e[1].boundingBox3D.zMin <= zMax] # has coordinates and guid
    storyElems = [e[0] for e in elemsOnStory] # only has guid


    # check if selected zones are in current story
    isSelectedOnCurrStory = False
    for zone in storyElems:
        for selZone in elements:
            if (zone.elementId.guid == selZone.elementId.guid):
                isSelectedOnCurrStory = True

    # If selected zones are not on current story, skip numbering
    if (not isSelectedOnCurrStory):
        storyIndex += 1
        continue


    # find zones on the current story from selected zones
    zonesOnStory = [e for e in selectedElementBoundingBoxes if zMin <= e[1].boundingBox3D.zMin <= zMax] # has coordinates and guid

    #find entry zone on current story
    elementsEntryVals = acc.GetPropertyValuesOfElements([e[0] for e in zonesOnStory], entryPropertyIdArrayItem)

    entryElement = 0
    entryElementIdx = 0
    for i in range(0, len(elementsEntryVals)):
        if (elementsEntryVals[i].propertyValues[0].propertyValue.value == True):
            entryElement = elements[i]
            entryElementIdx = i


    if (entryElement == 0): # no entry element found on this floor! Inform the user and exit the script
        print(f"No First_Zone found on {storyIndex} story. Ensure you have set an entry Zone for each story.")
        exit(-1)

    # sort current story zones by distance of entry room
    sortedPos = sortPositionsByDistance(((e[1].boundingBox3D.xMin, e[1].boundingBox3D.yMin, e[1].boundingBox3D.zMin, e[1].boundingBox3D.xMax, e[1].boundingBox3D.yMax) for e in zonesOnStory), (zonesOnStory[entryElementIdx][1].boundingBox3D.xMin, zonesOnStory[entryElementIdx][1].boundingBox3D.yMin)) 


    # iterate sorted positions and map them to its given element
    for (xMin, yMin, zMin, xMax, yMax) in sortedPos:
        # map the positon to its given element
        elem = [e for e in zonesOnStory if xMin == e[1].boundingBox3D.xMin and yMin == e[1].boundingBox3D.yMin and zMin == e[1].boundingBox3D.zMin and xMax == e[1].boundingBox3D.xMax and yMax == e[1].boundingBox3D.yMax]
   
        # Add new property value to the element
        elemPropertyValues.append(act.ElementPropertyValue(
               elem[0][0].elementId, propertyId, generatePropertyValue(storyIndex, elemIndex)))

        # Increment element index for every Zone
        elemIndex += 1
    # Increment Story Index to keep track of what story is being numbered
    storyIndex += 1

# sets the property value of all the elements in the project
acc.SetPropertyValuesOfElements(elemPropertyValues)

#######################################################################################################################################################################################




##################################################################### Print the result - Zone ID and Zone Number ######################################################################
if (selected):
    newValues = acc.GetPropertyValuesOfElements(elements, [propertyId])
    elemAndValuePairs = [(elements[i].elementId.guid, v.propertyValue.value) for i in range(len(newValues)) for v in newValues[i].propertyValues]
    for elemAndValuePair in sorted(elemAndValuePairs, key=lambda p: p[1]):
        print(elemAndValuePair)
else:
    newValues = acc.GetPropertyValuesOfElements(allZoneElements, [propertyId])
    elemAndValuePairs = [(allZoneElements[i].elementId.guid, v.propertyValue.value) for i in range(len(newValues)) for v in newValues[i].propertyValues]
    for elemAndValuePair in sorted(elemAndValuePairs, key=lambda p: p[1]):
        print(elemAndValuePair) 
#######################################################################################################################################################################################