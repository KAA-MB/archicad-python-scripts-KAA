######################################### General Info #########################################
# Written by: Jessica Wood  w/ Meghan Beckmann, for KAA Design Group                           #
# Date Created: 09/2022                                                                        #
# Date Modified: 05/2023 Meghan Beckmann & Jessica Wood                                        #
#                                                                                              #
# Description:                                                                                 #
# This script assigns zone dimensions for each zone in a project and inserts it into the       #
# user-defined property "Zone Dimensions".                                                     #
################################################################################################


import math

############ Archicad Connection #############
from archicad import ACConnection

conn = ACConnection.connect()
assert conn

acc = conn.commands
act = conn.types
acu = conn.utilities
##############################################




############################################### CONFIGURATION ################################################

propertyId = acu.GetUserDefinedPropertyId("KAA Python", "ZoneDimension")
elements = acc.GetElementsByType('Zone')
selectedElements = acc.GetSelectedElements()

if (len(selectedElements) > 0):
    elements = selectedElements

##############################################################################################################




######################################################## FUNCTIONS ########################################################

def GeneratePropertyValueString(widthFt: float, widthIn: float, heightFt: float, heightIn: float) -> str:
    return f"{widthFt}'-{widthIn}\" x {heightFt}'-{heightIn}\""

def generatePropertyValue(widthFt: float, widthIn: float, heightFt: float, heightIn: float) -> act.NormalStringPropertyValue:
    return act.NormalStringPropertyValue(GeneratePropertyValueString(widthFt, widthIn, heightFt, heightIn))


###########################################################################################################################




################################################################### BEGIN LOGIC ###################################################################

# collect all the data
boundingBoxes = acc.Get2DBoundingBoxes(elements)

# bind bounding boxes to element ids
elementBoundingBoxDict = dict(zip(elements, boundingBoxes))

# calculate the widths and heights
elemPropertyValues = []
counter = 0
for key,value in elementBoundingBoxDict.items():
        boxWidth = abs(value.boundingBox2D.xMax - value.boundingBox2D.xMin) ### x axis is up-down
        boxLength = abs(value.boundingBox2D.yMax - value.boundingBox2D.yMin)  ### y axis is left-right
        
        #get angle from custom property in Zone
        anglePropertyId = acu.GetUserDefinedPropertyId("KAA Python", "ZoneAngle")
        anglePropertyIdArrayItem = [act.PropertyIdArrayItem(anglePropertyId)]
        anglePropertyValue = acc.GetPropertyValuesOfElements(elements, anglePropertyIdArrayItem)
        userAngle = anglePropertyValue[counter].propertyValues[0].propertyValue.value
        #counter goes through list of zones in order to get angle of next one

        #check appropriate angles and convert angle for use in formula
        #users should input angles between 0 and 44.99 (<45)
        #angle cannot be 45 degrees (forumla domain out of range, infinite solutions)
        #angle greater than 45 degrees works but display of Width (x) and Length (y) is reversed
        if userAngle > 45 and userAngle <= 90:
             print(f"input angle {userAngle} corrected*")
             angle = 90 - userAngle
        else:
             angle = float(userAngle)

        ####### ADD AN IF STATEMENT FOR ANGLES EXACTLY 45 DEGREES
        if angle == 45:
            print(f"input angle {angle} skipped; cannot be calculated*")
            counter+=1
            continue
        elif angle > 90:
            print(f"input angle = {angle} skipped; must be less than 45*")
            counter+=1
            continue
        else:
            print(f"calculation angle = {angle}")


        angleRad = math.radians(angle) #convert to radians for use in finding tangent
        tangent = math.tan(angleRad)

        #calculate side b
        b = ((boxWidth * tangent) - boxLength) / ((tangent * tangent) - 1)

        #calculate side a
        a = b * tangent

        #calculate side c (actual Width of room)
        c = math.sqrt((a*a)+(b*b))

        #calculate sides a1, b1, c1 (c1 is actual Length of room)
        a1 = boxLength - b
        b1 = boxWidth - a
        c1 = math.sqrt((a1*a1)+(b1*b1))

        # Convert width and height to inches
        boxWidthIn = round(c * 39.3701)
        boxLengthIn = round(c1 * 39.3701)

        # Use the previous values to find the feet and inches of the zone dimensions
        boxWidthFt = boxWidthIn//12
        boxLengthFt = boxLengthIn//12

        boxWidthIn = boxWidthIn%12
        boxLengthIn = boxLengthIn%12
        
        newPropertyValue = generatePropertyValue(boxWidthFt, boxWidthIn, boxLengthFt, boxLengthIn)
        elemPropertyValues.append(act.ElementPropertyValue(key.elementId, propertyId, newPropertyValue))
        counter+=1
 
# set the new property values
acc.SetPropertyValuesOfElements(elemPropertyValues)

print()
print("* ANGLE SHOULD BE LESS THAN 45 DEGREES")
print("* FORMULA CANNOT CALCULATE 45 DEGREE ANGLES;")
print("  IF 45, MEASURE MANUALLY OR TEMPORARILY ROTATE ZONES TO 0 DEGREES")

##################################################################################################################################################