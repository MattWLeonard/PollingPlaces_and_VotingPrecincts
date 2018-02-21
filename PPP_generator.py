#-------------------------------------------------------------------------------
# Name:         PPP_generator
#               a.k.a. Polling Place and Precinct Generator
#
# Purpose:      (Creates and )builds a network dataset, creates a location-allocation
#               analysis layer, and then solves a location allocation problem to select
#               optimal polling place locations and generate voting precinct boundaries.
#
# Author:       Matthew Leonard
#
# Created:      12/09/2017
#-------------------------------------------------------------------------------

import arcpy
from arcpy import na
from arcpy import gp
from arcpy import env
from arcpy.sa import *

# Check out the ArcGIS extension licenses
arcpy.CheckOutExtension("GeoStats")
arcpy.CheckOutExtension("Network")
arcpy.CheckOutExtension("Spatial")

# Input: set workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)

########################################

# Define variables...

# Input: Existing Network Dataset to be used in analysis
Network = arcpy.GetParameterAsText(1)

# Input: Specify suffix and name for Location Allocation Analysis Layer (suffix can be reused later)
suffix = arcpy.GetParameterAsText(2)
AnalysisLayer = "LAanalysisLayer_" + suffix

# Input: Specify a value for Impedance Cutoff (maximum distance from a facility for which a voter will be assigned)
cutoff = str(arcpy.GetParameterAsText(3))

# Input: Facilities point FC to be added as Facilities (potential polling places)
polling_facilities = str(arcpy.GetParameterAsText(4))

# Input: Voters point FC to be added as Demand Points (subset of given percentage of voter points)
Voters = arcpy.GetParameterAsText(5)

Solve_Succeeded = "true"


# Run Processes...

# Process: Build Network
arcpy.BuildNetwork_na(Network)

# Process: Make Location-Allocation Layer
LAlayer = arcpy.MakeLocationAllocationLayer_na(Network, str(AnalysisLayer), "Length", "DEMAND_TO_FACILITY",
    "MINIMIZE_FACILITIES", "1", cutoff, "LINEAR", "1", "10", "", "ALLOW_UTURNS", "", "NO_HIERARCHY",
    "STRAIGHT_LINES", "1", "")

# Process: Add Locations: Facilities (Potential Polling Places)
arcpy.AddLocations_na(LAlayer, "Facilities", polling_facilities,
    "Name Name #;Capacity Capacity #", "1000 Feet", "NAME",
    "street_network SHAPE", "MATCH_TO_CLOSEST", "APPEND", "SNAP", "", "INCLUDE", "#")

# Process: Add Locations: Demand Points (Voters)
arcpy.AddLocations_na(LAlayer, "Demand Points", Voters, "", "1000 Feet", "",
    "street_network SHAPE", "MATCH_TO_CLOSEST", "APPEND", "SNAP", "", "INCLUDE", "#")

# Process: Solve
arcpy.Solve_na(AnalysisLayer, "SKIP", "CONTINUE", "", "")

########################################

# Define more variables...

# Get the layer object from the result object. The location allocation layer can
# now be referenced using the layer object.
LAoutLayer = LAlayer.getOutput(0)

# Get the names of all the sublayers within the service area layer.
subLayerNames = arcpy.na.GetNAClassNames(LAoutLayer)

# Store the layer names to be used in Select tool below.
DemandPoints = subLayerNames["DemandPoints"]
Facilities = subLayerNames["Facilities"]

# Output: name/path for output FC of voters (demand points) with assigned polling place
VotersAssigned = arcpy.GetParameterAsText(6)

# Output: name/path for output FC of polling places (facilities) that were selected
PPselected = arcpy.GetParameterAsText(7)


# Run More Processes...

# Select voter points with facility assigned and create new feature class from selection.
arcpy.Select_analysis(DemandPoints, VotersAssigned, '"FacilityID" IS NOT NULL')

# Select facilities that were chosen by analysis, and create new feature class from selection.
# "FacilityType" = 3 indicates facilities that were chosen to serve as polling places.
arcpy.Select_analysis(Facilities, PPselected, '"FacilityType" = 3')

########################################

# Input: City limit boundary (polygon FC) to serve as mask for Euclidean Allocation Raster tool
CityLimit = arcpy.GetParameterAsText(8)

# Output Euclidean Allocation Raster
PrecRaster = arcpy.GetParameterAsText(9)

# unspecified variable (not needed)
Output_distance_raster = ""

# unspecified variable (not needed)
Output_direction_raster = ""

# Process: Euclidean Allocation with mask & extent environment settings per city limit boundary
arcpy.env.mask = CityLimit
arcpy.env.extent = CityLimit
arcpy.gp.EucAllocation_sa(VotersAssigned, PrecRaster, "", "", "50", "FacilityID", Output_distance_raster, Output_direction_raster)

# Output Voting Precincts (polygon feature class)
Precincts = "Precincts_" + suffix

# Process: Raster to Polygon
arcpy.RasterToPolygon_conversion(PrecRaster, Precincts, "SIMPLIFY", "VALUE")