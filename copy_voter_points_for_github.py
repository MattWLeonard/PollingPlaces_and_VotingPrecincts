#-------------------------------------------------------------------------------
# Name:        copy_voter_points
# Purpose:     See below...
#
# Author:      Matthew Leonard
#
# Created:     12/03/2017
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# This script was used in creating a hypothetical set of individual voters in Brookhaven.
# This script produces a point feature class with one point for each individual voter.
# The input is a point feature class with one point for each residential building, each of which has an attribute
# for the number of voters who are assumed to live in that building.
# The script selects points for which the number of voters per building = each specified value from a list,
# from that selection creates a new feature class, and then appends that to the original feature class a number of
# times, essentially making a specified number of copies of each point.  For example, if a point represents 8 voters,
# it will be appended 7 times, so there will now be 8 total points at that location (each representing one
# individual voter).
#-------------------------------------------------------------------------------

import arcpy

# list of all possible values for voters per building
vlist = [2,3,4,5,6,8,10,12,14,15,16,18,20,21,24,27,28,30,32,36,40,42,45,50,54,70,80,84,100,120,140,160]

# Same list. After each iteration of Select and Append, the first list item will be removed, so countlist[0]
# will refer to the correct value each time.
countlist = [2,3,4,5,6,8,10,12,14,15,16,18,20,21,24,27,28,30,32,36,40,42,45,50,54,70,80,84,100,120,140,160]


for v in vlist:

    # path for input point FC with one point for each residential building
    infc = 'path/bldg_point_FC'

    # Path for output FC to be generated with each iteration of Select. Each output will contain all points for which
    # the number of voters per building = the value from countlist.  Each output will have the
    # same value at the end of its file name, represented by countlist[0]
    outfc = 'path/Voters_Indv_temp'+str(countlist[0])

    # Selects all points for which the number of voters per building = the value from countlist.
    arcpy.Select_analysis(infc, outfc, 'Voters='+str(countlist[0]))

    # How many times each output should be appended to the original input FC.  This is one less than v because,
    # for example, all points that have 8 voters per building need to be appended 7 times to the
    # original FC, so there will be 8 total points (each representing an individual voter) for each such building.
    i = v-1

    # Tracks how many times each output FC is appended to the original FC
    count = 0

    # Appends each output FC to the original FC. Does this i times. Adds 1 to count variable after each append,
    # until count = the value from vlist.
    while count < i:
        arcpy.Append_management(outfc, infc, 'TEST')
        count = count + 1

    # Removes first item in countlist, so that in the next iteration of Select and Append, the value used
    # will be the next value in the list.
    countlist.remove(countlist[0])

    print 'Appended '+str(v)
