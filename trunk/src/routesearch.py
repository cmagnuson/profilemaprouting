'''
Created on July 18, 2009

@author: Carl Magnuson
'''

import sys, os, optparse, postgresql, subprocess
from data import *


def main():
    #process command line options and arguments
    #TODO: move reading command line options to separate module
    #TODO: add help for each argument
    p = optparse.OptionParser()
    p.add_option('--strategy', default="shortesttime")
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--cs', default="WGS84")
    p.add_option('--verbose', '-v', action="store_true", default=False)
    options, arguments = p.parse_args()

    if len(arguments) < 4 :
        print("No Coordinates Specified For Search!")
        sys.exit()
        
    src_lon =  arguments[0]
    src_lat =  arguments[1]
    dst_lon =  arguments[2]
    dst_lat =  arguments[3]

    #TODO: move db code to separate module
    #connect to database and prepare statements
    #TODO: more informative error code for say wrong db, username, duplicated tracks, etc
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()
    
    search = db.prepare("""SELECT gid, AsText(the_geom) AS the_geom FROM dijkstra_sp_delta('ways', $1, $2, 0.1)""")
    get_gid = db.prepare("""SELECT find_nearest_link_within_distance(AsText(setsrid(makepoint($1,$2),4326)), .1, 'ways')""")
    get_node = db.prepare("""SELECT source FROM ways WHERE gid=$1""")
    
    gid = get_gid(float(src_lon), float(src_lat))
    src = get_node(gid[0][0])

    gid = get_gid(float(dst_lon), float(dst_lat))
    dst = get_node(gid[0][0])


    route = search(src[0][0], dst[0][0])
    print(route)
    

if __name__ == '__main__':
    main()