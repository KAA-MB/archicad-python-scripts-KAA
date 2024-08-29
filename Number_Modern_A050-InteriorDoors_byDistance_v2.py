######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
# Date Modified: 02/2023    JW + MB                                                            #
# Date Updated: 08/2024 for AC27 Template standards                                            #
#                                                                                              #
# Description:                                                                                 #
# This script generates unique ordered interior door element IDs. Sets the door                #
# element ID property value for all selected doors in the project. If no doors are             #
# selected, the script will number all interior doors in the project. The script sorts         #
# the door IDs in ascending order by distance from the user-defined property                   #
# “First_Door”.                                                                                #
################################################################################################




############ Archicad Connection #############
from archicad import ACConnection
from typing import List, Tuple, Iterable
from itertools import cycle
import math

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities
##############################################




################################################################################# CONFIGURATION INTERIOR DOORS ##############################################################################

# *** Doors grabbed reliant on selected elements ***
# This script assumes that there is an entry interior door (first door custom property)
# The script numbers all interior doors or just selected doors... hidden doors are still an issue.

# property ID for Doors
propertyId = acu.GetBuiltInPropertyId('General_ElementID')
propertyValueStringPrefix = ''

# Get Zones - ARE THESE VARIABLES IN USE?
#propertyIdZones = acu.GetBuiltInPropertyId('Zone_ZoneNumber')
#zoneElements = acc.GetElementsByType('Zone')

# Get all Doors
classificationItemDoor = acu.FindClassificationItemInSystem(
    'KAA CLASSIFICATIONS', 'Door')
doorElements = acc.GetElementsByClassification(
    classificationItemDoor.classificationItemId)

# Get Selected Doors
selectedDoors = acc.GetSelectedElements()

# Get Position PropertyId
positionPropertyId = acu.GetBuiltInPropertyId("Category_Position")
positionPropertyIdArrayItem = [act.PropertyIdArrayItem(positionPropertyId)]

# Get the Entry Door/Window PropertyId item
entryPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "First_Door")
entryPropertyIdArrayItem = [act.PropertyIdArrayItem(entryPropertyId)]

# Get the Building Number PropertyId item
buildingNumPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "BuildingNumber")
buildingNumPropertyIdArrayItem = [act.PropertyIdArrayItem(buildingNumPropertyId)]

# Get the Story Number PropertyId item
storyPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "StoryNumber")
storyPropertyIdArrayItem = [act.PropertyIdArrayItem(storyPropertyId)]


###### CONSTANT VALUES #####

STORY_GROUPING_LIMIT = 1

NUMBER_OF_STORIES = 4      # <- value will be number of Stories in the Project 

############################


##################################################################################################################################################################################################




########################################################################################## FUNCTIONS #############################################################################################

def GeneratePropertyValueString(storyIndex: int, elemIndex: str) -> str:
    # Function: used to generate a property Value string
    return f"{propertyValueStringPrefix}{storyIndex:1d}{elemIndex:02d}"


def generatePropertyValue(storyIndex: int, elemIndex: int) -> act.NormalStringPropertyValue:
    # Function: used to generate a property Value string
    return act.NormalStringPropertyValue(GeneratePropertyValueString(storyIndex, elemIndex))


def createClusters(positions: Iterable[float], limit: float) -> List[Tuple[float, float]]:
    # Function: creates clusters based on zValues of all the Zones. Clusters represent stories. NOT USING ZONES ANY MORE RIGHT?

    positions = sorted(positions)
    if len(positions) == 0:
        return []

    clusters = []
    posIter = iter(positions)
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
    # function: takes positions and the position of the entry room and returns positions sorted by their distance from the Entry room

    # sort positions by distance from entry point
    positions = sorted(positions, key=lambda e: math.dist((e[0], e[1]), entryPosition))

    # return sorted positions
    return positions

#############################################################################################################################################################################################




########################################################################################### Begin Logic #####################################################################################


# find bounding boxes of zone elements - ARE THESE VARIABLES IN USE?
#zoneBoundingBoxes = acc.Get3DBoundingBoxes(zoneElements)
#zoneElementBoundingBoxes = list(zip(zoneElements, zoneBoundingBoxes))
# story clusters: range of (zMin, zMax) that represent each story
#zClusters = createClusters((bb.boundingBox3D.zMin for bb in zoneBoundingBoxes), STORY_GROUPING_LIMIT)

# Check if there are selected elements
# Check if there are selected elements
if len(selectedDoors) == 0:  # no doors selected
    countAll = True
    # Filter doorElements to include only "Interior" doors
    elementsPosVals = acc.GetPropertyValuesOfElements(doorElements, positionPropertyIdArrayItem)
    elements = []
    for i in range(len(elementsPosVals)):
        if elementsPosVals[i].propertyValues[0].propertyValue.value.nonLocalizedValue == "Interior":
            elements.append(doorElements[i])
else:  # use selected doors
    countAll = False
    elementsPosVals = acc.GetPropertyValuesOfElements(selectedDoors, positionPropertyIdArrayItem)
    elements = []
    for i in range(len(elementsPosVals)):
        if elementsPosVals[i].propertyValues[0].propertyValue.value.nonLocalizedValue == "Interior":
            elements.append(selectedDoors[i])

boundingBoxes = acc.Get3DBoundingBoxes(elements)
doorBoundingBoxes = list(zip(elements, boundingBoxes))
isCounted = list(zip(elements, [False for _ in range(len(elements))]))



storyIndex = 0
elemPropertyValues = []
for story in range(NUMBER_OF_STORIES):
    elemIndex = 1


        # sort elements by story
    doorsOnStory = [] # list of elements in the story
    elementsStoryVals = acc.GetPropertyValuesOfElements(elements, storyPropertyIdArrayItem)

    for i in range(0, len(elementsStoryVals)):
        if (hasattr(elementsStoryVals[i].propertyValues[0].propertyValue, "value")):
            if (elementsStoryVals[i].propertyValues[0].propertyValue.value == story):
                doorsOnStory.append(doorBoundingBoxes[i])
                #dwElements.append(elements[i])
        else:
            print(f"Door/Window (ID: {elements[i].elementId.guid}) does not have a StoryNumber. Ensure each exterior Door/Window has the appropriate StoryNumber set.")
            exit(-1)

    if (len(doorsOnStory) == 0):
        storyIndex += 1
        continue


    # Get the building number of each story
    elementsBuildingVals = acc.GetPropertyValuesOfElements([e[0] for e in doorsOnStory], buildingNumPropertyIdArrayItem)
    totalNumberOfBuildings = 1 # possibly add logic to check if there is only 1 building
    for i in range(len(elementsBuildingVals)):
        if (hasattr(elementsBuildingVals[i].propertyValues[0].propertyValue, "value")):
            if (elementsBuildingVals[i].propertyValues[0].propertyValue.value > totalNumberOfBuildings):
                totalNumberOfBuildings = elementsBuildingVals[i].propertyValues[0].propertyValue.value
    for building in range(1, totalNumberOfBuildings+1): #the first number needs to be the lowest BuildingNumber in the array
        elemIndex = 1
        doorsInBuilding = []
        for i in range(len(elementsBuildingVals)):
            if (hasattr(elementsBuildingVals[i].propertyValues[0].propertyValue, "value")):
                if (elementsBuildingVals[i].propertyValues[0].propertyValue.value == building):
                    doorsInBuilding.append(doorsOnStory[i])
            else:
                print(f"Door/Window (ID: {doorsOnStory[i].elementId.guid}) does not have a BuildingNumber. Ensure each exterior Door/Window has the appropriate BuildingNumber set.")
                exit(-1)
            # Get the element bounding boxes of dwOnStory
        if (len(doorsInBuilding) == 0): # if there are not exterior elements in the building, then there is only one building and we need to use all exterior elements
            boundingBoxes = acc.Get3DBoundingBoxes(doorsOnStory)
            elementBoundingBoxes = list(zip(doorsOnStory, boundingBoxes))
            elementsEntryVals = acc.GetPropertyValuesOfElements(doorsOnStory, entryPropertyIdArrayItem)

        else:
            boundingBoxes = acc.Get3DBoundingBoxes([e[0] for e in doorsInBuilding])
            elementBoundingBoxes = list(zip(doorsInBuilding, boundingBoxes))
            elementsEntryVals = acc.GetPropertyValuesOfElements([e[0] for e in doorsInBuilding], entryPropertyIdArrayItem)


        # Find Entry Door
        entryElement = 0
        entryElementIdx = 0 # If there is no entry door/window we assume the first element will be entry
        for i in range(0, len(elementsEntryVals)):
            if(elementsEntryVals[i].propertyValues[0].propertyValue.status != "notAvailable"):
                if (elementsEntryVals[i].propertyValues[0].propertyValue.value == True):
                    entryElement = elementBoundingBoxes[i]
                    entryElementIdx = i

        if (entryElement == 0): # No first door or first window found
            print(f"No First_Door Found in Building {building} on story {story}. Ensure one door or window has the appropriate property set for each story.")
            exit(-1)

        minMaxZ = [(e[1].boundingBox3D.zMin, e[1].boundingBox3D.zMax) for e in elementBoundingBoxes]

        minZElem = min(minMaxZ, key=lambda tup: tup[1])[0]
        maxZElem = max(minMaxZ, key=lambda tup: tup[1])[1]

        minMaxValues = (minZElem, maxZElem)   # <- the min and max values


         # Call function to sort Doors by distance
        sortedDoors = sortPositionsByDistance(((e[1].boundingBox3D.xMin, e[1].boundingBox3D.yMin, e[1].boundingBox3D.zMin, e[1].boundingBox3D.xMax, e[1].boundingBox3D.yMax) for e in doorsOnStory), (doorsOnStory[entryElementIdx][1].boundingBox3D.xMin, doorsOnStory[entryElementIdx][1].boundingBox3D.yMin))       
        
        # Iterate sorted positions and map them to its given element
        for (xMin, yMin, zMin, xMax, yMax) in sortedDoors:
            # map the positon to its given element
            elem = [e for e in doorsOnStory if xMin == e[1].boundingBox3D.xMin and yMin == e[1].boundingBox3D.yMin and zMin == e[1].boundingBox3D.zMin and xMax == e[1].boundingBox3D.xMax and yMax == e[1].boundingBox3D.yMax]

            # Check if the element has been counted already
            countedElement = [d for d in isCounted if elem[0][0].elementId.guid == d[0].elementId.guid]

            if (countedElement[0][1]):
                continue
            else:
                idx = isCounted.index((countedElement[0][0], False))
                isCounted[idx] = (countedElement[0][0], True)
    
            # Add new property value to the element
            elemPropertyValues.append(act.ElementPropertyValue(
                elem[0][0].elementId, propertyId, generatePropertyValue(storyIndex, elemIndex)))

            # Increment element index
            elemIndex += 1
        # Increment story index    
        storyIndex += 1

  

# sets the property value of all the elements in the project
acc.SetPropertyValuesOfElements(elemPropertyValues)


#############################################################################################################################################################################################




####################################################################### Print the results - Room ID and Room Number ########################################################################
newValues = acc.GetPropertyValuesOfElements(elements, [propertyId])
elemAndValuePairs = [(elements[i].elementId.guid, v.propertyValue.value) for i in range(len(newValues)) for v in newValues[i].propertyValues]
for elemAndValuePair in sorted(elemAndValuePairs, key=lambda p: p[1]):
    print(elemAndValuePair)
#############################################################################################################################################################################################
