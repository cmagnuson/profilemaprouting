'''
Created on Jun 25, 2009

@author: Carl Magnuson
'''

import sys, os, optparse, postgresql, subprocess
from data import *

def main():
    #process command line options and arguments
    #TODO: move reading command line options to separate module
    #TODO: add help for each argument
    p = optparse.OptionParser()
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--verbose', '-v', action="store_true", default=False)
    options, arguments = p.parse_args()


    #TODO: move db code to separate module
    #connect to database and prepare statements
    #TODO: more informative error code for say wrong db, username, duplicated tracks, etc
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()
    db.execute("""
        -- ----------------------------
        --  Table structure for "userdata"
-- ----------------------------
DROP TABLE IF EXISTS "userdata";
CREATE TABLE "userdata" (
    "trackid" int4 NOT NULL DEFAULT NULL,
    "pointid" int4 NOT NULL DEFAULT NULL,
    "lon" float8 NOT NULL DEFAULT NULL,
    "lat" float8 NOT NULL DEFAULT NULL,
    "time" timestamp NOT NULL DEFAULT NULL,
    "speed" float4 NOT NULL DEFAULT NULL,
    "course" int2 NOT NULL DEFAULT NULL,
    "altitude" int2 NOT NULL DEFAULT NULL,
    "geom" "geometry" DEFAULT NULL,
    "distance" float4 NOT NULL DEFAULT NULL,
    "gid" int4 DEFAULT NULL
)
WITH (OIDS=FALSE);
ALTER TABLE "userdata" OWNER TO "routing";

-- ----------------------------
--  Uniques structure for table "userdata"
-- ----------------------------
ALTER TABLE "userdata" ADD CONSTRAINT "uniquetrack" UNIQUE ("lat", "lon", "time");

-- ----------------------------
--  Checks structure for table "userdata"
-- ----------------------------
ALTER TABLE "userdata" ADD CONSTRAINT "enforce_srid_geom" CHECK ((srid(geom) = 4326));
ALTER TABLE "userdata" ADD CONSTRAINT "enforce_dims_geom" CHECK ((ndims(geom) = 2));
ALTER TABLE "userdata" ADD CONSTRAINT "enforce_geotype_geom" CHECK (((geometrytype(geom) = 'POINT'::text) OR (geom IS NULL)));

-- ----------------------------
--  Indexes structure for table "userdata"
-- ----------------------------
CREATE INDEX "geom_index" ON "userdata" USING gist(geom);

""")
    
    
    if options.verbose:
        print("Table created")
    
if __name__ == '__main__':
    main()