# Introduction #

The components of the system are the following:
  * GPS data importer.
  * Data sanitizer
  * Map matching and assignment of user points to corresponding polylines
  * Assignment of speed to polylines
  * Route search

Some additional utilities that will be provided are:
  * A tool to create the database schema and set any initial settings
  * A tool to export all user collected data to a KML file also including the weighted polylines (with lines colored by weight) to confirm that data import and route weighting is happening correctly

# Details #

The data importer will take GPX files as input and insert them into a database table storing all user generated data.  It will compare timestamps to make sure that no duplicate data can be entered into the database.

The data sanitizer will initially ask the user for the time windows that correspond with driving data, ideally it will automatically recognize what data is associated with driving and what is with other GPS usage.

The map matching module will compare the newly imported data with a known road network and use some measure of similarity to assign each segment of a GPS track to a roadway.  The database will be updated to equate a point and a roadway.

The assignment of speed to polylines will take all points which are equated to roadways, and associate an expected speed with the roadway.  There are many possibilities of how this module could work - looking only at recent data, only data around the current time, data from multiple users, etc.  Initially this module will use an average of all user collected data.

The route search will use pgRouting along with the weighted polylines to generate a route for user selected start and destination points.