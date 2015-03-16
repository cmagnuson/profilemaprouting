

# Introduction #

This document will provide a description of the different tools a user will interact with and their options and behaviors.

Tools:
  * profileimport
  * weighlinks
  * routesearch
  * kmldump
  * tablecreate


# Details #


## Data Collection ##
The data collection command line tool will be called in the following way:
```
profileimport [flags] filename
[flags]
--s				perform sanitization/cleaning of input data (default)
--ns				do not perform any sanitization on the input data
--format fileformat		format of the input data (as recognized by GPSbabel - CSV, GPX, etc) (default is GPX)
--gpsbabel_path path	path to gpsbabel executable (tries user path if flag not seen)
--db_ip	ip			ip address of database (localhost by default)
--dp_user user		username to login to db (default: route)
--db_pass pass		database password (default: route)
--db_name name        database name (default: osm)
--verbose                     verbose output
```
Input: (optional) command line flags and data file

Output: error messages if appropriate, or no output on successful import

Operation: The profileimport tool will read in user generated data, optionally sanitize it by removing data which does not appear to be actual driving data, match it to the roadway model loaded in the postgres database, and import it to the database with each segment of driving data tagged with its associated roadway. Input data which does not have a minimum of lon/lon points and timestamp will be rejected.


## Link Weighting ##
The link weight assignment tool will be called in the following way:
```
weighlinks [flags]

[flags]
--method method	 simple (default), ..., additional weighting methods could be added here
--db_ip	ip			ip address of database (localhost by default)
--dp_user user		username to login to db (default: route)
--db_pass pass		database password (default: route)
--db_name name        database name (default: osm)
--verbose                     verbose output
```
Input: (optional) command line options.

Output: error messages if appropriate, or no output on successful import

Operation: The link weighting tool will assign weights to the roadway network data from the tagged user data based on the algorithm chosen. It will not alter the store of user submitted data, but will assign estimated traversal times to the roadway network.  This is not a destructive update, so weighlinks can be called many times without the need to reload any user or road network data.


## Search ##
The route search command line tool will be called in the following way:
```
routesearch [flags] source_longitude source_latitude destination_longitude destination_latitude

[flags]
-strategy strategy	shortesttime (default), additional strategies could be added to say avoid right turns or prefer parkways
--db_ip	ip			ip address of database (localhost by default)
--dp_user user		username to login to db (default: route)
--db_pass pass		database password (default: route)
--db_name name        database name (default: osm)
--cs system			coordinate system (default: WGS84)
--verbose                     verbose output
```
Input: (optional) command line options, source and destination coordinates.

Output: error messages if appropriate, on successful search the found route is output to the console as well as a KML file containing the route and markers of the turns and expected distances/times.

Operation: The search tool will find the nearest roadways to the start and destination coordinates and calculate an optimal route from source to destination using the given method.


## Utilities ##
The KML export utility will be called in the following way
```
kmldump [flags] outputfile

[flags]
--db_ip	ip			ip address of database (localhost by default)
--dp_user user		username to login to db (default: route)
--db_pass pass		database password (default: route)
--db_name name        database name (default: osm)
--verbose                     verbose output
```
Input: (optional) command line options, output filename.

Output: error messages if appropriate, else KML file written to given destination.

Operation: The KML export utility will output all user data stored in the database to a KML file which will show different trips, times road segments took to traverse and the road segment ID that was assigned to each of the data.  This tool is useful in designing the system to ensure that data is being processed correctly and testing different road assignment methods, as well as being an easy way to visualize all data which has been input to the system.


---


The table creation utility will be called in the following way
```
tablecreate [flags]

[flags]
--db_ip	ip			ip address of database (localhost by default)
--dp_user user		username to login to db (default: route)
--db_pass pass		database password (default: route)
--db_name name        database name (default: osm)
--verbose                     verbose output
```
Input: (optional) command line options.

Output: error messages if appropriate, otherwise will create the needed PostgreSQL table to store the user data, and any required PostgreSQL stored procedures.

Operation: The table creation utility will modify the pgrouting and OSM database schema adding a table to store user data and any stored procedures needed for this application.