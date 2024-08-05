These python scripts were created for KAA Design Group by Jessica Wood, a programmer interning with us for the summer, and Meghan Beckmann (Director of Design Technology). 

ZONE NUMBERING BY DISTANCE FROM FIRST
•	Numbers Zones sequentially starting from "First Zone" (a custom property), and proceeding by closest distance from this first zone. If there's a selection, the script uses only selected zones; otherwise it uses all zones in project. Numbering series is unique per story level (e.g. 101, 102 for 1st floor; 201, 202 for 2nd floor).

ZONE NUMBERING BY DISTANCE FROM PREVIOUS
•	Numbers Zones sequentially starting from "First Zone" (a custom property), and proceeding by closest distance from the previous zone numbered. If there's a selection, the script uses only selected zones; otherwise it uses all zones in project. 

ZONE DIMENSIONS
•	Measures each Zone's length and width dimensions (feet-inches) based on Bounding Box, and writes it to a custom property. We use a Zone Label to display these dimensions in plan. The script takes a custom property called "Zone Angle" (user input) in order to calculate the dimensions correctly for rotated zones. We did not find a way to pull the rotation angle automatically, so it defaults to 0 degrees and is filled in by the user if different. The math formula breaks at 45 degrees (a compromise, since to fix this would require another user input). If there's a selection, the script uses only selected zones; otherwise it uses all zones in project. 

ATTRIBUTES - create folders and sort attributes into folders (layers example)
•	Creates attribute folders, and sorts attributes into the folders according to our firm’s naming convention. If folders have already been created, it moves all attributes into a temporary “dummy” folder, removes other folders and proceeds with creating/sorting (then erases dummy folder). Attributes not matching the naming convention are placed in a folder called “Audit Non-compliant”.  *script is broken in AC27 due to changes in JSON commands (need help fixing)

ATTRIBUTES - audit names (layers example)
•	Audits attribute names according to our firm’s naming convention, and prints a list of “non-compliant” attributes. 

INTERIOR DOORS - number sequentially
•	Numbers interior Doors sequentially starting from "First Door” (a custom property), and proceeding by closest distance from this first door. The script relies on correct Classification as Door, and uses the built-in property for Position: Interior. If there's a selection, the script uses only selected doors; otherwise it uses all doors in project. Numbering series is unique per story level (e.g. 101, 102 for 1st floor; 201, 202 for 2nd floor).

INTERIOR DOORS - number by zone
•	Numbers interior Doors based on associated Zone’s number + letter of alphabet (e.g. 101a, 101b). The script uses the built-in property for Position: Interior. If there's a selection, the script uses only selected doors; otherwise it uses all doors in project. Ideally this script would also have logic to move clockwise around each zone so the a, b, c sequence is more logical.

EXTERIOR DOORS/WINDOWS
•	Numbers interior Doors and Windows sequentially starting from "First Door” or “First Window” (a custom property), and proceeding clockwise around the building. The script relies on correct Classification as Door or Window, built-in property Position: Exterior, and also takes several custom properties. The clockwise direction is controlled by custom property “Exterior Side” to identify Top, Right, Bottom, Left position in plan (cardinal directions were more error prone since people get confused. Numbering series is unique per “Story Level” (e.g. 101, 102 for 1st floor; 201, 202 for 2nd floor) - we decided to make this a custom property also in order to have more control over numbering of clerestories, since “z bands” didn’t produce reliable results. The “Building Number” custom property defaults to 1, and if the site has multiple buildings the user can identify unique numbers for each (though the numbering starts at 101 for any building, the building’s number doesn’t become part of door/window’s number). This part of the script breaks right now if Building Numbers are not sequential - needs fixing. 
