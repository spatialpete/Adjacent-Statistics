#### Peter Sherman
#### GIS Programming Project
#### Spring 2013
#### Input: Census Blocks, Breeding Bird Survey (BBS) routes
#### Output: Population density and population counts for 3 defined radii around BBS routes
#### Note: this is CPU intensive, a selection of 225 routes took ~10 hours to complete.

####importing modules
import arcpy, os, time, string
from datetime import datetime, date, time
from arcpy import env
arcpy.env.overwriteOutput = True
env.workspace = "C:/Temp/PeterS_demo"
BBSroutes = "routes_proj.shp"  #routes input file
CensusBlocks = "Buffalo.shp" #census input file
#table = "C:/Temp/PeterS_demo/usCB.gdb/table"

arcpy.CopyFeatures_management(BBSroutes, "routesCP.shp")
routesCP = "routesCP.shp"

######creating a file geodatabase to store the master block file
arcpy.CreateFileGDB_management("C:/Temp/PeterS_demo", "usCB.gdb")

######Creating a feature class and appending state Census Blocks to it
##out_path = "usCB.gdb"
##out_name = "usCensusB.shp"
##geometry_type = "POLYGON"
##template = ""
##has_m = "DISABLED"
##has_z = "DISABLED"
####### Use Describe to get a SpatialReference object
###spatial_ref = arcpy.Describe("C:\\Users\\Peter S\\Documents\\A School Stuff\\thesis\\bbsRoutes").spatialReference
##dataset = "Buffalo.shp"
##spatialRef = arcpy.Describe(dataset).spatialReference
####### Execute CreateFeatureclass
##arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type,
##                                    template, has_m, has_z, spatialRef)
##

## Script below this line only needs to be run once, then comment out.
## iterate through folder of feature classes
## http://forums.arcgis.com/threads/20604-List-Feature-Classes-within-Subfolders-using-Python
##def fcs_in_workspace(workspace): #also possible to create a list of all the file locations....
##  arcpy.env.workspace = workspace
##  for fc in arcpy.ListFeatureClasses():
##    yield os.path.join(workspace, fc)
##  for ws in arcpy.ListWorkspaces():
##    for fc in fcs_in_workspace(os.path.join(workspace, ws)):
##        yield fc
##
##for fc in fcs_in_workspace("C:\\Temp\\CensusFiles"):
##    ####appending each Census Block file to usCensusB.shp
##    arcpy.Append_management(fc, "C:/Temp/ProgProj/usCB.gdb/usCensusB", "NO_TEST", "", "")#input, target, schema, field, subtype
##    #NO_TEST means it will not import fields that are not in the initial file.
##    print fc

#### preparing the BBS file for adding the population density and population counts
#arcpy.AddField_management(BBSroutes, "PopD", "LONG", 9, 4, "", "")
#arcpy.AddField_management(BBSroutes, "POP10", "LONG", 9, 4, "", "")

#### Loops to select each BBS route, and surrounding landscape
arcpy.MakeFeatureLayer_management(BBSroutes, "BBS_lyr")
#dataset = "Buffalo.shp"
#spatialRef = arcpy.Describe(dataset).spatialReference
#out_coordinate_system = ("C:/Program Files (x86)/ArcGIS/Desktop10.0/Coordinate Systems/Projected Coordinate Systems/Continental/North America/North_America_Equidistant_Conic.prj")
#arcpy.Project_management("BBS_lyr", "BBS_lyrp", spatialRef, "NAD_1983_to_WGS_1984_1")
arcpy.MakeFeatureLayer_management(CensusBlocks, "census_lyr")




###creating the rtenoList to select individual routes
rtenoList = []
BBScur = arcpy.SearchCursor(BBSroutes)
for route in BBScur:
    rtenoList.append(route.rteno)
print rtenoList
del route
del BBScur

arcpy.MakeFeatureLayer_management(BBSroutes, "BBS_lyr")
arcpy.MakeFeatureLayer_management(CensusBlocks, "census_lyr")

####Main script section
#### selects the route, selects the landscape, outputs the stats
Radius = [2500, 19700]#change to desired radii 2500 10000
for radii in Radius:
    outFile = open("C:\\Temp\\Stats"+str(radii)+".txt", "w")
    for rteno in rtenoList:#change to max number of routes
        where = '"rteno" = '+str(rteno) #' "FID" = %d ' %FID
        arcpy.SelectLayerByAttribute_management("BBS_lyr", "NEW_SELECTION", where)
        arcpy.SelectLayerByLocation_management("census_lyr", "WITHIN_A_DISTANCE",
                                               "BBS_lyr", radii, "NEW_SELECTION")
        #getting the mean popdens of selected BBS routes
        #output must be to a geodatabase table
        whereEC = '"PopD" > 400'
        arcpy.SelectLayerByAttribute_management("census_lyr", "REMOVE_FROM_SELECTION", whereEC)
        arcpy.Statistics_analysis("census_lyr", "table", [["PopD", "MEAN"],["POP10", "SUM"]])
        statsTable = arcpy.SearchCursor("table")
        for stats in statsTable:
            print stats.MEAN_PopD, rteno
            outFile.write(str(rteno) + "\t" + str(stats.MEAN_PopD) + "\t" + 
                          str(stats.SUM_POP10) + "\t" + str(datetime.now() - start) +"\n")
            del stats
            del statsTable
    outFile.close()
del radii
print "main script complete, updating routes now"


#### preparing the BBS file for adding the population density and population counts
arcpy.AddField_management(routesCP, "PopD2500", "LONG", 9, 4, "", "")
arcpy.AddField_management(routesCP, "POP2500", "LONG", 9, 4, "", "")
arcpy.AddField_management(routesCP, "PopD19700", "LONG", 9, 4, "", "")
arcpy.AddField_management(routesCP, "POP19700", "LONG", 9, 4, "", "")

for radii in Radius:
    #### preparing the BBS file for adding the population density and population counts
    #arcpy.AddField_management(routesCP, "PopD"+str(radii), "LONG", 9, 4, "", "")
    #arcpy.AddField_management(routesCP, "POP"+str(radii), "LONG", 9, 4, "", "")
    #### opening the text file to read it into the BBSroute file
    statFile = open("C:\\Temp\\PeterS_demo\\Stats"+str(radii)+".txt", "r")
    
    for row in statFile: # for each row in the Stat output file
        rowList = row.strip("\n").split("\t")# splits into [rteno, PopD, POP10, time]
        ## update cursor to add the PopD and Pop10 to the BBS route file
        BBScur = arcpy.UpdateCursor(routesCP,'"rteno" = '+str(rowList[0]))
        for i in BBScur:
            if radii == 2500:
                i.PopD2500 = rowList[1] # then make the PopD for that route equal 
                i.POP2500 = rowList[2]  # to PopD from the list
                BBScur.updateRow(i)
            if radii == 10000:
                i.PopD10000 = rowList[1]
                i.POP10000 = rowList[2]
                BBScur.updateRow(i)
            if radii == 19700:
                i.PopD19700 = rowList[1]
                i.POP19700 = rowList[2]
                BBScur.updateRow(i)
        del BBScur
        
    statFile.close()
    
print "routes updated, now to find routes near cities"
#### Now to iterate through cities and select nearby routes

cityFile = open("C:\\Temp\\PeterS_demo\\CityStats.txt", "w")

cityList = []# creating a cityList, similar to rtenoList above
CityCur = arcpy.SearchCursor("BuffaloUA.shp")#change citylayer
for city in CityCur:
    cityList.append(city.NAME)
print cityList
del city
del CityCur

####making feature layer for the selections below
arcpy.MakeFeatureLayer_management("BuffaloUA.shp", "Census_UA")
arcpy.MakeFeatureLayer_management(routesCP, "BBS_lyr2")

for city in cityList:
    start = datetime.now()
    where = '"NAME" = '+"'%s'" %city#+ "'%s'" %Name
    arcpy.SelectLayerByAttribute_management("Census_UA", "NEW_SELECTION", where)#census UAs (find this file)
    arcpy.SelectLayerByLocation_management("BBS_lyr2", "WITHIN_A_DISTANCE",
                                               "Census_UA", 80467, "NEW_SELECTION")
    arcpy.Statistics_analysis("BBS_lyr2", "tableCity", [["PopD19700", "MEAN"],["POP19700", "SUM"]])

    statsTable = arcpy.SearchCursor("tableCity")
    for stats in statsTable:
        print stats.MEAN_PopD19700, city
        cityFile.write(str(city) + "\t" + str(stats.MEAN_PopD19700) + "\t" + 
                      str(stats.SUM_POP19700) + "\t" + str(datetime.now() - start) +"\n")
        del stats
        del statsTable
cityFile.close()




    
