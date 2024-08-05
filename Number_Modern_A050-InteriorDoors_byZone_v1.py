######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
#                                                                                              #
# Description:                                                                                 #
# This script generates unique ordered interior door element IDs. Sets the door                #
# element ID property value for all selected interior doors in the project. If no doors        # 
# are selected, all interior doors in the project will be numbered. The script                 #
# numbers the doors by the zone it belongs in.                                                 #
################################################################################################




############ Archicad Connection #############
from archicad import ACConnection

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities
##############################################




######################################### CONFIGURATION INTERIOR DOORS #################################################

# property ID for Doors
propertyId = acu.GetBuiltInPropertyId('General_ElementID')

# Get Position PropertyId
positionPropertyId = acu.GetBuiltInPropertyId("Category_Position")
positionPropertyIdArrayItem = [act.PropertyIdArrayItem(positionPropertyId)]

# Get related zone PropertyId item
relatedZonePropertyId = acu.GetBuiltInPropertyId('General_RelatedZoneNumber')
relatedZonePropertyIdArrayItem = [act.PropertyIdArrayItem(relatedZonePropertyId)]

# Get doors
classificationItemDoor = acu.FindClassificationItemInSystem(
    'KAA CLASSIFICATIONS', 'Door')
doorElements = acc.GetElementsByClassification(
    classificationItemDoor.classificationItemId)

# Get Selected Doors 
selectedElements = acc.GetSelectedElements()

#######################################################################################################################




################################################ BEGIN LOGIC ##########################################################

# Property values array
elemPropertyValues = []

# Check if there are selected elements
if (len(selectedElements) == 0): # no selected elements
    elementsPosVals = acc.GetPropertyValuesOfElements(doorElements, positionPropertyIdArrayItem)
    elements = doorElements
else: # use selected elements
    elementsPosVals = acc.GetPropertyValuesOfElements(selectedElements, positionPropertyIdArrayItem)
    elements = selectedElements

# get interior doors
interiorDoors = []
for i in range(len(elementsPosVals)):
    if (elementsPosVals[i].propertyValues[0].propertyValue.value.nonLocalizedValue == "Interior"):
        interiorDoors.append(elements[i])


# Get the zones related to interior doors 
interiorDoorsWithZoneNumber = []
defaultZoneNumber = '000' # if a door is not tied to a zone have a default zone number
elementsZoneVals = acc.GetPropertyValuesOfElements(interiorDoors, relatedZonePropertyIdArrayItem)
for i in range(len(elementsZoneVals)):
    if (elementsZoneVals[i].propertyValues[0].propertyValue.value != ""):
        interiorDoorsWithZoneNumber.append((interiorDoors[i], elementsZoneVals[i].propertyValues[0].propertyValue.value))
    else:
        # no zone related found! send an error message
        print(f"No zone related to door {interiorDoors[i].elementId.guid} found! Default Zone number for this door is 000\n")
        interiorDoorsWithZoneNumber.append((interiorDoors[i], defaultZoneNumber))


# Iterate doors with zone numbers and rename them
interiorDoorsWithZoneNumber = sorted(interiorDoorsWithZoneNumber, key=lambda d: int(d[1]))
previousZone = interiorDoorsWithZoneNumber[0][1]
charIdx = 'a'
for door in interiorDoorsWithZoneNumber:
    if (previousZone == door[1]):
        propertyValue = door[1] + charIdx
    else:
        charIdx = 'a'
        propertyValue = door[1] + charIdx
        previousZone = door[1]

    elemPropertyValues.append(act.ElementPropertyValue(
        door[0].elementId, propertyId, act.NormalStringPropertyValue(propertyValue)))
    next = chr(ord(charIdx) + 1)
    charIdx = next


# sets the property value of all the elements in the project
acc.SetPropertyValuesOfElements(elemPropertyValues)

#######################################################################################################################




############################################################# Print the result - Door ID ##############################################################
newValues = acc.GetPropertyValuesOfElements(interiorDoors, [propertyId])
elemAndValuePairs = [(interiorDoors[i].elementId.guid, v.propertyValue.value) for i in range(len(newValues)) for v in newValues[i].propertyValues]
for elemAndValuePair in sorted(elemAndValuePairs, key=lambda p: p[1]):
    print(elemAndValuePair)
#######################################################################################################################################################