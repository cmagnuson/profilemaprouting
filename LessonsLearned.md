# Introduction #

These are some thoughts and possible improvements to the system that came about while building it.


# Details #

Improvements/Ideas
  * use of multiple user's data - routing off a single users data is not an ideal solution, there is not enough data available for lesser or never used roads.  A wider range of input would allow for more precise routing and higher resolution data model to route based off of say specific timeframes (rush hour, last hour, etc.)
  * Multiple users data does bring up some issues though - it needs to be easy to input and more sanitization must take place to get rid of junk or malicious data.  Privacy issues would need to be addressed as well.
  * A web based interface to input data and do route searches would be beneficial.  A typical end user would struggle to set up PostgreSQL, Python 3.0+, py-postgresql, pgrouting, etc.  A typical user may be able to handle uploading a GPX file however.
  * An API to access the web interface and retrieve an OSM road identifier and road traversal cost could create some interesting opportunities to build other apps around the system.
  * OSM import presented some issues. osm2pgrouting could use some help to improve error messages and memory management.  Cloudmade OSM downloads would vary in quality depending on the time downloaded and had issues assigning the correct road classification.  A tool which analyzed the userdata and ran Osmosis to download the needed roadway data could be useful.