######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
#                                                                                              #
# Description:                                                                                 #
# This script generates unique ordered exterior door and window element IDs. Sets              #
# the door and window’s element ID property value for all selected exterior                    #
# doors/windows in the project. If no doors/windows are selected, the script will              #
# number all exterior doors in the project. The script starts at a “First_door” or             #
# “First_Window” and numbers it clockwise around the perimeter of the project.                 #
################################################################################################




############ Archicad Connection #############
import re
from archicad import ACConnection
from typing import List, Tuple, Iterable
import math

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities
##############################################




###################################### CONFIGURATION EXTERIOR DOORS/WINDOWS #######################################

# property ID for Doors/windows
propertyId = acu.GetBuiltInPropertyId('General_ElementID')
propertyValueStringPrefix = ''

# Get doors
classificationItemDoor = acu.FindClassificationItemInSystem(
    'KAA CLASSIFICATIONS', 'Door')
elementsDoor = acc.GetElementsByClassification(
    classificationItemDoor.classificationItemId)

# get windows
classificationItemWindow = acu.FindClassificationItemInSystem(
    'KAA CLASSIFICATIONS', 'Window')
elementsWindow = acc.GetElementsByClassification(
    classificationItemWindow.classificationItemId)

# Get Selected Elements
selectedElements = acc.GetSelectedElements()

# combine windows and doors to one list
elementsDW = elementsDoor + elementsWindow


# Get property values of "Position", "First_Door", "First_Window", "StoryNumber", "BuildingNumber" and "ExteriorSide"
positionPropertyId = acu.GetBuiltInPropertyId("Category_Position")
positionPropertyIdArrayItem = [act.PropertyIdArrayItem(positionPropertyId)]
entryPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "First_Door") 
entryPropertyIdArrayItem = [act.PropertyIdArrayItem(entryPropertyId)]
entryWinPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "First_Window") 
entryWinPropertyIdArrayItem = [act.PropertyIdArrayItem(entryWinPropertyId)]
storyPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "StoryNumber")
storyPropertyIdArrayItem = [act.PropertyIdArrayItem(storyPropertyId)]
locationPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "ExteriorSide")
locationPropertyIdArrayItem = [act.PropertyIdArrayItem(locationPropertyId)]
buildingNumPropertyId = acu.GetUserDefinedPropertyId("KAA Python", "BuildingNumber")
buildingNumPropertyIdArrayItem = [act.PropertyIdArrayItem(buildingNumPropertyId)]

# Extract exterior doors and windows
elementsPosVals = acc.GetPropertyValuesOfElements(elementsDW, positionPropertyIdArrayItem)

exteriorElementsDW = []
for i in range(0, len(elementsPosVals)):
    if (elementsPosVals[i].propertyValues[0].propertyValue.value.nonLocalizedValue == "Exterior"):
        exteriorElementsDW.append(elementsDW[i])

###### CONSTANT VALUES #####
NUMBER_OF_STORIES = 4      # <- value will be number of Stories in the Project 
############################

########################################################################################################################




########################################################################################## FUNCTIONS #############################################################################################

def GeneratePropertyValueString(storyIndex: int, elemIndex: int) -> str:
    # Function: used to generate a property Value string
    return f"{propertyValueStringPrefix}{storyIndex:1d}{elemIndex:02d}"



def generatePropertyValue(storyIndex: int, elemIndex: int) -> act.NormalStringPropertyValue:
    # Function: used to generate a property Value string
    return act.NormalStringPropertyValue(GeneratePropertyValueString(storyIndex, elemIndex))



def sortPositions(entryElement: Tuple[act.ElementIdArrayItem, act.BoundingBox3D], minMaxVals: Tuple[float, float], elements: List[Tuple[act.ElementIdArrayItem, act.BoundingBox3D]]) -> List[Tuple[float, float]]: # need a user defined entry door
    # Function: †akes all Doors/Windows on the current story and the position of the entry Door/Window and returns positions sorted clockwise around the perimeter starting with entry Door/Window

    # If there is only one Door/Window return
    if (len(elements) == 1):
        return [elements[0]]

    # create Z-midpoint
    midpointZ = (minMaxVals[1] + minMaxVals[0])/2

    # sort positions by midpoint
    bottomRow = [e for e in elements if e[1].boundingBox3D.zMin <= midpointZ]
    bottomPos = [p[0] for p in bottomRow]
    topRow = [e for e in elements if e[1].boundingBox3D.zMin > midpointZ]
    topPos = [p[0] for p in topRow]
    
    # create list to represent sorted points
    sortedPositions = []

    # first numbered element will be entry door/window
    sortedPositions.append(entryElement)
    currentPos = entryElement

    # loop through each row and append the closest point to the sorted list

    # loop through bottom row first
    for i in range(len(bottomPos)-1):
        if (currentPos == "error"):
            print("error!")

        # determine which side the element is on 
        elementsLocationVals = acc.GetPropertyValuesOfElements([currentPos[0]], locationPropertyIdArrayItem)

        # Call function to find the next closest door/window
        tempPos = determineClosestPoint(currentPos, bottomRow, elementsLocationVals[0].propertyValues[0].propertyValue.value.displayValue, sortedPositions)
        currentPos = tempPos
        sortedPositions.append(currentPos)

    # If there are no doors/windows in the top row, skip the top row iteration
    if (len(topRow) == 0):
        return sortedPositions

    # set up current pos for top row
    elementsLocationVals = acc.GetPropertyValuesOfElements([entryElement[0]], locationPropertyIdArrayItem)

    currentPos = determineClosestPoint(entryElement, topRow, elementsLocationVals[0].propertyValues[0].propertyValue.value.displayValue, sortedPositions)
    sortedPositions.append(currentPos)

    # loop through top row
    for i in range(len(topPos)-1):
        if (currentPos == "error"):
            print("error!")

        # determine which side the element is on 
        elementsLocationVals = acc.GetPropertyValuesOfElements([currentPos[0]], locationPropertyIdArrayItem)

        # Call function to find the next closest door/window
        tempPos = determineClosestPoint(currentPos, topRow, elementsLocationVals[0].propertyValues[0].propertyValue.value.displayValue, sortedPositions)
        currentPos = tempPos
        sortedPositions.append(currentPos)
    
    return sortedPositions




def determineClosestPoint(point: Tuple[act.ElementIdArrayItem, act.BoundingBox3D], positions: Iterable[Tuple[act.ElementIdArrayItem, act.BoundingBox3D]], side: str, sortedPositions: List[Tuple[float, float]]):
    # Function: Returns the next closest door/window of the given door/window

    # sort objects by the side in which they belong
    top = []
    bottom = []
    left = []
    right = []
    elementsLocationVals = acc.GetPropertyValuesOfElements([p[0] for p in positions], locationPropertyIdArrayItem)
    for i in range(len(elementsLocationVals)):
        if (elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue == "Top"):
            if (positions[i][0].elementId.guid != point[0].elementId.guid):
                if (side == elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue):
                    if (not isInArray(positions[i], sortedPositions)): 
                        top.append(positions[i])
                else:
                    top.append(positions[i])
        if (elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue == "Bottom"):
            if (positions[i][0].elementId.guid != point[0].elementId.guid):
                if (side == elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue):
                    if (not isInArray(positions[i], sortedPositions)): 
                        bottom.append(positions[i])
                else:
                    bottom.append(positions[i])
        if (elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue == "Right"):
            if (positions[i][0].elementId.guid != point[0].elementId.guid):
                if (side == elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue):
                    if (not isInArray(positions[i], sortedPositions)): 
                        right.append(positions[i])
                else:
                    right.append(positions[i])
        if (elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue == "Left"):
            if (positions[i][0].elementId.guid != point[0].elementId.guid):
                if (side == elementsLocationVals[i].propertyValues[0].propertyValue.value.displayValue):
                    if (not isInArray(positions[i], sortedPositions)): 
                        left.append(positions[i])
                else:
                    left.append(positions[i])


    # Find which side the current Door/Window belongs to
    if (side == 'Top'): 
        # Check if there are any other elements that have not been numbered on the Top side, if not move to the right, bottom, then left and check if they have elements to be numbered
        if (len([t for t in top if t[1].boundingBox3D.xMin >= point[1].boundingBox3D.xMin]) == 0): 
            if (len(right) == 0):
                if (len(bottom) == 0):
                    if (len(left) == 0):
                        if (len([t for t in top if not isInArray(t, sortedPositions)]) == 0):
                            return "error"
                        else:
                            top = sorted([t for t in top if not isInArray(t, sortedPositions)], key=lambda b: b[1].boundingBox3D.xMin)
                            return top[0]
                    else:
                        left = sorted(left, key=lambda e: e[1].boundingBox3D.yMin)
                        for i in range(len(left)):
                            if (not isInArray(left[i], sortedPositions)):
                                return left[i]
                else:
                    bottom = sorted(bottom, key=lambda e: e[1].boundingBox3D.xMin, reverse=True)
                    for i in range(len(bottom)):
                        if (not isInArray(bottom[i], sortedPositions)):
                            return bottom[i]
            else:
                right = sorted(right, key=lambda e: e[1].boundingBox3D.yMin, reverse=True)
                for i in range(len(right)):
                        if (not isInArray(right[i], sortedPositions)):
                            return right[i]
        else: # If we are finding the next element on the same side, we must account for several corner cases (listed below)
            lowestTop = sorted([b for b in top if not isInArray(b, sortedPositions)], key=lambda b: b[1].boundingBox3D.yMin)
            top = sorted([t for t in top if t[1].boundingBox3D.xMin >= point[1].boundingBox3D.xMin], key=lambda e: e[1].boundingBox3D.xMin)
            for i in range(len(top)):
                if (top[i][1].boundingBox3D.xMin == point[1].boundingBox3D.xMin): # sort the windows/doors on the same axis
                    topY = sorted([t for t in top if t[1].boundingBox3D.xMin == point[1].boundingBox3D.xMin], key=lambda t: t[1].boundingBox3D.yMin)
                    for x in range(len(topY)):
                        if (not isInArray(topY[x], sortedPositions)):
                            for y in range(len(lowestTop)):
                                if (math.dist(((lowestTop[y][1].boundingBox3D.xMin + lowestTop[y][1].boundingBox3D.xMax)/2, (lowestTop[y][1].boundingBox3D.yMin + lowestTop[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((topY[x][1].boundingBox3D.xMin + topY[x][1].boundingBox3D.xMax)/2, (topY[x][1].boundingBox3D.yMin + topY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestTop[y][1].boundingBox3D.xMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                    return lowestTop[y]
                            return topY[x]
                if (not isInArray(top[i], sortedPositions)):
                    if (point[1].boundingBox3D.yMin > top[i][1].boundingBox3D.yMin): # divet down
                        topY = sorted([t for t in top if t[1].boundingBox3D.xMin == top[i][1].boundingBox3D.xMin], key=lambda t: t[1].boundingBox3D.yMin, reverse=True)
                        for x in range(len(topY)):
                            if (not isInArray(topY[x], sortedPositions)):
                                for y in range(len(lowestTop)):
                                    if (math.dist(((lowestTop[y][1].boundingBox3D.xMin + lowestTop[y][1].boundingBox3D.xMax)/2, (lowestTop[y][1].boundingBox3D.yMin + lowestTop[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((topY[x][1].boundingBox3D.xMin + topY[x][1].boundingBox3D.xMax)/2, (topY[x][1].boundingBox3D.yMin + topY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestTop[y][1].boundingBox3D.xMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                        return lowestTop[y]
                                return topY[x]
                    elif (point[1].boundingBox3D.yMin < top[i][1].boundingBox3D.yMin): # divet up
                        topY = sorted([t for t in top if t[1].boundingBox3D.xMin == top[i][1].boundingBox3D.xMin], key=lambda t: t[1].boundingBox3D.yMin)
                        for x in range(len(topY)):
                            for y in range(len(lowestTop)):
                                if (math.dist(((lowestTop[y][1].boundingBox3D.xMin + lowestTop[y][1].boundingBox3D.xMax)/2, (lowestTop[y][1].boundingBox3D.yMin + lowestTop[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((topY[x][1].boundingBox3D.xMin + topY[x][1].boundingBox3D.xMax)/2, (topY[x][1].boundingBox3D.yMin + topY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestTop[y][1].boundingBox3D.xMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                    return lowestTop[y]
                            if (not isInArray(topY[x], sortedPositions)):
                                return topY[x]
                    return top[i]

    elif (side == "Bottom"):
        # Check if there are any other elements that have not been numbered on the Bottom side, if not move to the left, top, then right and check if they have elements to be numbered
        if (len([t for t in bottom if t[1].boundingBox3D.xMin <= point[1].boundingBox3D.xMin]) == 0):
            if (len(left) == 0):
                if (len(top) == 0):
                    if (len(right) == 0):
                        if (len([t for t in bottom if not isInArray(t, sortedPositions)]) == 0):
                            return "error"
                        else:
                            bottom = sorted([t for t in bottom if not isInArray(t, sortedPositions)], key=lambda b: b[1].boundingBox3D.xMin, reverse=True)
                            return bottom[0]
                    else:
                        right = sorted(right, key=lambda e: e[1].boundingBox3D.yMin, reverse=True)
                        for i in range(len(right)):
                            if (not isInArray(right[i], sortedPositions)):
                                return right[i]
                else:
                    top = sorted(top, key=lambda e: e[1].boundingBox3D.xMin)
                    for i in range(len(top)):
                        if (not isInArray(top[i], sortedPositions)):
                            return top[i]
            else:
                left = sorted(left, key=lambda e: e[1].boundingBox3D.yMin)
                for i in range(len(left)):
                    if (not isInArray(left[i], sortedPositions)):
                        return left[i]
        else: # If we are finding the next element on the same side, we must account for several corner cases (listed below)
            lowestBottom = sorted([b for b in bottom if not isInArray(b, sortedPositions)], key=lambda b: b[1].boundingBox3D.yMin, reverse=True)
            bottom = sorted([t for t in bottom if t[1].boundingBox3D.xMin <= point[1].boundingBox3D.xMin], key=lambda e: e[1].boundingBox3D.xMin, reverse=True)
            for i in range(len(bottom)):
                if (bottom[i][1].boundingBox3D.xMin == point[1].boundingBox3D.xMin): # sort the windows/doors on the same axis
                    bottomY = sorted([b for b in bottom if b[1].boundingBox3D.xMin == point[1].boundingBox3D.xMin], key=lambda b: b[1].boundingBox3D.yMin)
                    for x in range(len(bottomY)):
                        if (not isInArray(bottomY[x], sortedPositions)):
                            for y in range(len(lowestBottom)):
                                if (math.dist(((lowestBottom[y][1].boundingBox3D.xMin + lowestBottom[y][1].boundingBox3D.xMax)/2, (lowestBottom[y][1].boundingBox3D.yMin + lowestBottom[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((bottomY[x][1].boundingBox3D.xMin + bottomY[x][1].boundingBox3D.xMax)/2, (bottomY[x][1].boundingBox3D.yMin + bottomY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestBottom[y][1].boundingBox3D.xMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                        return lowestBottom[y]
                            return bottomY[x]
                if (not isInArray(bottom[i], sortedPositions)):
                    if (point[1].boundingBox3D.yMin > bottom[i][1].boundingBox3D.yMin): # divet down
                        bottomY = sorted([t for t in bottom if t[1].boundingBox3D.xMin == bottom[i][1].boundingBox3D.xMin], key=lambda t: t[1].boundingBox3D.yMin, reverse=True)
                        for x in range(len(bottomY)):
                            if (not isInArray(bottomY[x], sortedPositions)):
                                for y in range(len(lowestBottom)):
                                    if (math.dist(((lowestBottom[y][1].boundingBox3D.xMin + lowestBottom[y][1].boundingBox3D.xMax)/2, (lowestBottom[y][1].boundingBox3D.yMin + lowestBottom[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((bottomY[x][1].boundingBox3D.xMin + bottomY[x][1].boundingBox3D.xMax)/2, (bottomY[x][1].boundingBox3D.yMin + bottomY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestBottom[y][1].boundingBox3D.xMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                        return lowestBottom[y]
                                return bottomY[x]
                    elif (point[1].boundingBox3D.yMin < bottom[i][1].boundingBox3D.yMin): # divet up
                        bottomY = sorted([t for t in bottom if t[1].boundingBox3D.xMin == bottom[i][1].boundingBox3D.xMin], key=lambda t: t[1].boundingBox3D.yMin)
                        for x in range(len(bottomY)):
                            if (not isInArray(bottomY[x], sortedPositions)):
                                for y in range(len(lowestBottom)):
                                    if (math.dist(((lowestBottom[y][1].boundingBox3D.xMin + lowestBottom[y][1].boundingBox3D.xMax)/2, (lowestBottom[y][1].boundingBox3D.yMin + lowestBottom[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((bottomY[x][1].boundingBox3D.xMin + bottomY[x][1].boundingBox3D.xMax)/2, (bottomY[x][1].boundingBox3D.yMin + bottomY[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestBottom[y][1].boundingBox3D.xMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.xMin):
                                        return lowestBottom[y]
                                return bottomY[x]
                    return bottom[i]

    elif (side == "Left"):
        # Check if there are any other elements that have not been numbered on the Left side, if not move to the top, right, then bottom and check if they have elements to be numbered
        if (len([t for t in left if t[1].boundingBox3D.yMin >= point[1].boundingBox3D.yMin]) == 0):
            if (len(top) == 0):
                if (len(right) == 0):
                    if (len(bottom) == 0):
                        if (len([t for t in left if not isInArray(t, sortedPositions)]) == 0):
                            return "error"
                        else:
                            left = sorted([t for t in left if not isInArray(t, sortedPositions)], key=lambda b: b[1].boundingBox3D.yMin)
                            return left[0]
                    else:
                        bottom = sorted(bottom, key=lambda e: e[1].boundingBox3D.xMin, reverse=True)
                        for i in range(len(bottom)):
                            if (not isInArray(bottom[i], sortedPositions)):
                                return bottom[i]
                else:
                    right = sorted(right, key=lambda e: e[1].boundingBox3D.yMin, reverse=True)
                    for i in range(len(right)):
                            if (not isInArray(right[i], sortedPositions)):
                                return right[i]
            else:
                top = sorted(top, key=lambda e: e[1].boundingBox3D.xMin)
                for i in range(len(top)):
                        if (not isInArray(top[i], sortedPositions)):
                            return top[i]
        else: # If we are finding the next element on the same side, we must account for several corner cases (listed below)
            lowestLeft = sorted([b for b in left if not isInArray(b, sortedPositions)], key=lambda b: b[1].boundingBox3D.xMin, reverse=True)
            left = sorted([t for t in left if t[1].boundingBox3D.yMin >= point[1].boundingBox3D.yMin], key=lambda e: e[1].boundingBox3D.yMin)
            for i in range(len(left)):
                if (left[i][1].boundingBox3D.yMin == point[1].boundingBox3D.yMin): # sort the windows/doors on the same axis
                    leftX = sorted([l for l in left if l[1].boundingBox3D.yMin == point[1].boundingBox3D.yMin], key=lambda b: b[1].boundingBox3D.xMin)
                    for x in range(len(leftX)):
                        if (not isInArray(leftX[x], sortedPositions)):
                            for y in range(len(lowestLeft)):
                                if (math.dist(((lowestLeft[y][1].boundingBox3D.xMin + lowestLeft[y][1].boundingBox3D.xMax)/2, (lowestLeft[y][1].boundingBox3D.yMin + lowestLeft[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((leftX[x][1].boundingBox3D.xMin + leftX[x][1].boundingBox3D.xMax)/2, (leftX[x][1].boundingBox3D.yMin + leftX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestLeft[y][1].boundingBox3D.yMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                        return lowestLeft[y]
                            return leftX[x]
                if (not isInArray(left[i], sortedPositions)):
                    if (point[1].boundingBox3D.xMin > left[i][1].boundingBox3D.xMin): # divet left
                        leftX = sorted([t for t in left if t[1].boundingBox3D.yMin == left[i][1].boundingBox3D.yMin], key=lambda t: t[1].boundingBox3D.xMin, reverse=True)
                        for x in range(len(leftX)):
                            if (not isInArray(leftX[x], sortedPositions)):
                                for y in range(len(lowestLeft)):
                                    if (math.dist(((lowestLeft[y][1].boundingBox3D.xMin + lowestLeft[y][1].boundingBox3D.xMax)/2, (lowestLeft[y][1].boundingBox3D.yMin + lowestLeft[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((leftX[x][1].boundingBox3D.xMin + leftX[x][1].boundingBox3D.xMax)/2, (leftX[x][1].boundingBox3D.yMin + leftX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestLeft[y][1].boundingBox3D.yMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                        return lowestLeft[y]
                                return leftX[x]
                    elif (point[1].boundingBox3D.xMin < left[i][1].boundingBox3D.xMin): # divet right 
                        leftX = sorted([t for t in left if t[1].boundingBox3D.yMin == left[i][1].boundingBox3D.yMin], key=lambda t: t[1].boundingBox3D.xMin)
                        for x in range(len(leftX)):
                            for y in range(len(lowestLeft)):
                                if (math.dist(((lowestLeft[y][1].boundingBox3D.xMin + lowestLeft[y][1].boundingBox3D.xMax)/2, (lowestLeft[y][1].boundingBox3D.yMin + lowestLeft[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((leftX[x][1].boundingBox3D.xMin + leftX[x][1].boundingBox3D.xMax)/2, (leftX[x][1].boundingBox3D.yMin + leftX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and lowestLeft[y][1].boundingBox3D.yMin >= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                    return lowestLeft[y]
                            return leftX[x]
                    return left[i]

    elif (side == "Right"):
        # Check if there are any other elements that have not been numbered on the Right side, if not move to the bottom, left, then top and check if they have elements to be numbered
        if (len([t for t in right if t[1].boundingBox3D.yMin <= point[1].boundingBox3D.yMin]) == 0):
            if (len(bottom) == 0):
                if (len(left) == 0):
                    if (len(top) == 0):
                        if (len([t for t in right if not isInArray(t, sortedPositions)]) == 0):
                            return "error"
                        else:
                            right = sorted([t for t in right if not isInArray(t, sortedPositions)], key=lambda b: b[1].boundingBox3D.yMin, reverse=True)
                            return right[0]
                    else:
                        top = sorted(top, key=lambda e: e[1].boundingBox3D.xMin)
                        for i in range(len(top)):
                            if (not isInArray(top[i], sortedPositions)):
                                return top[i]
                else:
                    left = sorted(left, key=lambda e: e[1].boundingBox3D.yMin)
                    for i in range(len(left)):
                        if (not isInArray(left[i], sortedPositions)):
                            return left[i]
            else:
                bottom = sorted(bottom, key=lambda e: e[1].boundingBox3D.xMin, reverse=True)
                for i in range(len(bottom)):
                        if (not isInArray(bottom[i], sortedPositions)):
                            return bottom[i]
        else: # If we are finding the next element on the same side, we must account for several corner cases (listed below)
            leftestRight = sorted([r for r in right if not isInArray(r, sortedPositions)], key=lambda e: e[1].boundingBox3D.xMin)
            right = sorted([t for t in right if t[1].boundingBox3D.yMin <= point[1].boundingBox3D.yMin], key=lambda e: e[1].boundingBox3D.yMin, reverse=True)
            for i in range(len(right)):
                if (right[i][1].boundingBox3D.yMin == point[1].boundingBox3D.yMin): # sort the windows/doors on the same axis
                    rightX = sorted([r for r in right if r[1].boundingBox3D.yMin == point[1].boundingBox3D.yMin], key=lambda b: b[1].boundingBox3D.xMin, reverse=True)
                    for x in range(len(rightX)):
                        if (not isInArray(rightX[x], sortedPositions)):
                            for y in range(len(leftestRight)):
                                if (math.dist(((leftestRight[y][1].boundingBox3D.xMin + leftestRight[y][1].boundingBox3D.xMax)/2, (leftestRight[y][1].boundingBox3D.yMin + leftestRight[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((rightX[x][1].boundingBox3D.xMin + rightX[x][1].boundingBox3D.xMax)/2, (rightX[x][1].boundingBox3D.yMin + rightX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and leftestRight[y][1].boundingBox3D.yMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                    return leftestRight[y]
                            return rightX[x]
                if (not isInArray(right[i], sortedPositions)):
                    if (point[1].boundingBox3D.xMin > right[i][1].boundingBox3D.xMin): # divet left
                        rightX = sorted([r for r in right if r[1].boundingBox3D.yMin == right[i][1].boundingBox3D.yMin], key=lambda t: t[1].boundingBox3D.xMin, reverse=True)
                        for x in range(len(rightX)):
                            if (not isInArray(rightX[x], sortedPositions)):
                                for y in range(len(leftestRight)):
                                    if (math.dist(((leftestRight[y][1].boundingBox3D.xMin + leftestRight[y][1].boundingBox3D.xMax)/2, (leftestRight[y][1].boundingBox3D.yMin + leftestRight[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((rightX[x][1].boundingBox3D.xMin + rightX[x][1].boundingBox3D.xMax)/2, (rightX[x][1].boundingBox3D.yMin + rightX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and leftestRight[y][1].boundingBox3D.yMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                        return leftestRight[y]
                                return rightX[x]
                    elif (point[1].boundingBox3D.xMin < right[i][1].boundingBox3D.xMin): # divet right
                        rightX = sorted([r for r in right if r[1].boundingBox3D.yMin == right[i][1].boundingBox3D.yMin], key=lambda t: t[1].boundingBox3D.xMin)
                        for x in range(len(rightX)):
                            if (not isInArray(rightX[x], sortedPositions)):
                                for y in range(len(leftestRight)):
                                    if (math.dist(((leftestRight[y][1].boundingBox3D.xMin + leftestRight[y][1].boundingBox3D.xMax)/2, (leftestRight[y][1].boundingBox3D.yMin + leftestRight[y][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) <= math.dist(((rightX[x][1].boundingBox3D.xMin + rightX[x][1].boundingBox3D.xMax)/2, (rightX[x][1].boundingBox3D.yMin + rightX[x][1].boundingBox3D.yMax)/2), ((point[1].boundingBox3D.xMin + point[1].boundingBox3D.xMax)/2, (point[1].boundingBox3D.yMin + point[1].boundingBox3D.yMax)/2)) and leftestRight[y][1].boundingBox3D.yMin <= sortedPositions[len(sortedPositions)-2][1].boundingBox3D.yMin):
                                        return leftestRight[y]
                                return rightX[x]
                    return right[i]

    # Return an error if we do not find a next-closest element (we should never get here)
    return "error"


def isInArray(element: Tuple[act.ElementIdArrayItem, act.BoundingBox3D], sortedPositions: List[Tuple[float, float]]):
    # Function: checks if the element has already been numbered
    for i in range(len(sortedPositions)):
        if (sortedPositions[i][0].elementId.guid == element[0].elementId.guid):
            return True
    return False

#############################################################################################################################################################################################




################################################################################### BEGIN LOGIC #############################################################################################

# create new list of exterior doors/windows
dwElements = []

# Check to see if there are selected Elements
if (len(selectedElements) == 0): # No selected Elements
    elements = exteriorElementsDW
else: # Use selected elements
    elementsPosVals = acc.GetPropertyValuesOfElements(selectedElements, positionPropertyIdArrayItem)

    elements = []
    for i in range(0, len(elementsPosVals)):
        if (elementsPosVals[i].propertyValues[0].propertyValue.value.nonLocalizedValue == "Exterior"):
            elements.append(selectedElements[i])

### Begin to loop through each story ###

storyIndex = 0
elemPropertyValues = []
for story in range(NUMBER_OF_STORIES):
    elemIndex = 1

    # sort elements by story
    dwOnStory = [] # list of elements in the story
    elementsStoryVals = acc.GetPropertyValuesOfElements(elements, storyPropertyIdArrayItem)

    for i in range(0, len(elementsStoryVals)):
        if (hasattr(elementsStoryVals[i].propertyValues[0].propertyValue, "value")):
            if (elementsStoryVals[i].propertyValues[0].propertyValue.value == story):
                dwOnStory.append(elements[i])
                dwElements.append(elements[i])
        else:
            print(f"Door/Window (ID: {elements[i].elementId.guid}) does not have a StoryNumber. Ensure each exterior Door/Window has the appropriate StoryNumber set.")
            exit(-1)

    if (len(dwOnStory) == 0):
        storyIndex += 1
        continue


    # Get the building number of each story
    elementsBuildingVals = acc.GetPropertyValuesOfElements(dwOnStory, buildingNumPropertyIdArrayItem)
    totalNumberOfBuildings = 1 # possibly add logic to check if there is only 1 building
    for i in range(len(elementsBuildingVals)):
        if (hasattr(elementsBuildingVals[i].propertyValues[0].propertyValue, "value")):
            if (elementsBuildingVals[i].propertyValues[0].propertyValue.value > totalNumberOfBuildings):
                totalNumberOfBuildings = elementsBuildingVals[i].propertyValues[0].propertyValue.value
    for building in range(1, totalNumberOfBuildings+1): #the first number needs to be the lowest BuildingNumber in the array
        elemIndex = 1
        dwInBuilding = []
        for i in range(len(elementsBuildingVals)):
            if (hasattr(elementsBuildingVals[i].propertyValues[0].propertyValue, "value")):
                if (elementsBuildingVals[i].propertyValues[0].propertyValue.value == building):
                    dwInBuilding.append(dwOnStory[i])
            else:
                print(f"Door/Window (ID: {dwOnStory[i].elementId.guid}) does not have a BuildingNumber. Ensure each exterior Door/Window has the appropriate BuildingNumber set.")
                exit(-1)
            # Get the element bounding boxes of dwOnStory
        if (len(dwInBuilding) == 0): # if there are not exterior elements in the building, then there is only one building and we need to use all exterior elements
            boundingBoxes = acc.Get3DBoundingBoxes(dwOnStory)
            elementBoundingBoxes = list(zip(dwOnStory, boundingBoxes))
            elementsEntryVals = acc.GetPropertyValuesOfElements(dwOnStory, entryPropertyIdArrayItem)

        else:
            boundingBoxes = acc.Get3DBoundingBoxes(dwInBuilding)
            elementBoundingBoxes = list(zip(dwInBuilding, boundingBoxes))
            elementsEntryVals = acc.GetPropertyValuesOfElements(dwInBuilding, entryPropertyIdArrayItem)


        # Find Entry Door/Window
        entryElement = 0
        entryElementIdx = 0 # If there is no entry door/window we assume the first element will be entry
        for i in range(0, len(elementsEntryVals)):
            if(elementsEntryVals[i].propertyValues[0].propertyValue.status != "notAvailable"):
                if (elementsEntryVals[i].propertyValues[0].propertyValue.value == True):
                    entryElement = elementBoundingBoxes[i]
                    entryElementIdx = i

        if (entryElement == 0): # No First_Door found, look for First_Window
                elementsEntryVals = acc.GetPropertyValuesOfElements(dwOnStory, entryWinPropertyIdArrayItem)
                for i in range(0, len(elementsEntryVals)):
                    if (elementsEntryVals[i].propertyValues[0].propertyValue.status != "notAvailable"):
                        if (elementsEntryVals[i].propertyValues[0].propertyValue.value == True):
                            entryElement = elementBoundingBoxes[i]
                            entryElementIdx = i

        if (entryElement == 0): # No first door or first window found
            print(f"No First_Door or First_Window Found in Building {building} on story {story}. Ensure one door or window has the appropriate property set for each story.")
            exit(-1)


        # Check if any of the elements have missing Exterior sides
        elementsLocationVals = acc.GetPropertyValuesOfElements(dwInBuilding, locationPropertyIdArrayItem)
        for x in range(len(elementsEntryVals)):
            if (x == 0):
                continue
            if (not hasattr(elementsLocationVals[x].propertyValues[0].propertyValue, "value")):
                print(f"Door/Window (ID: {dwInBuilding[x].elementId.guid}) does not have an ExteriorSide. Ensure each exterior Door/Window has the appropriate ExteriorSide property set.")
                exit(-1)

        minMaxZ = [(e[1].boundingBox3D.zMin, e[1].boundingBox3D.zMax) for e in elementBoundingBoxes]

        minZElem = min(minMaxZ, key=lambda tup: tup[1])[0]
        maxZElem = max(minMaxZ, key=lambda tup: tup[1])[1]

        minMaxValues = (minZElem, maxZElem)   # <- the min and max values

        sortedDW = sortPositions( entryElement, minMaxValues, elementBoundingBoxes)

        for dw in sortedDW:
            # set door/window property value
            elemPropertyValues.append(act.ElementPropertyValue(dw[0].elementId, propertyId, generatePropertyValue(storyIndex, elemIndex)))

            # increment elemIndex
            elemIndex += 1
    storyIndex += 1


acc.SetPropertyValuesOfElements(elemPropertyValues)

######################################################################################################################################################################################################




############################################################# Print the result - Door/Window ID ##############################################################
newValues = acc.GetPropertyValuesOfElements(dwElements, [propertyId])
elemAndValuePairs = [(dwElements[i].elementId.guid, v.propertyValue.value) for i in range(len(newValues)) for v in newValues[i].propertyValues]
for elemAndValuePair in sorted(elemAndValuePairs, key=lambda p: p[1]):
    print(elemAndValuePair)
##############################################################################################################################################################