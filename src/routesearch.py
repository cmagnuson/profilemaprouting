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
    
    search = db.prepare("""SELECT gid, ST_AsKML(the_geom) AS the_geom, AsText(the_geom) FROM dijkstra_sp_delta('ways', $1, $2, 0.1)""")
    get_gid = db.prepare("""SELECT find_nearest_link_within_distance(AsText(setsrid(makepoint($1,$2),4326)), .1, 'ways')""")
    get_node = db.prepare("""SELECT source FROM ways WHERE gid=$1""")
    get_dist = db.prepare("""SELECT length, to_cost, name FROM ways WHERE gid=$1""")
    
    gid = get_gid(float(src_lon), float(src_lat))
    src = get_node(gid[0][0])

    gid = get_gid(float(dst_lon), float(dst_lat))
    dst = get_node(gid[0][0])


    route = search(src[0][0], dst[0][0])
    #print(route)
    total_distance = 0
    total_time = 0
    
    kmlfile = open("search.kml","w")
    kmlfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    kmlfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    kmlfile.write("<Folder>\n")
    kmlfile.write("<Style id=\"trkStyle\"><LineStyle><color>ffff0000</color><width>4</width></LineStyle><PolyStyle><color>7f00ff00</color></PolyStyle></Style>\n")
    print("Road | Cumulative Distance | Cumulative Time")

    for link in route:
        roadinfo = get_dist(link[0])[0]
        total_distance += float(roadinfo[0])
        total_time += float(roadinfo[1]*60)
        print(roadinfo[2]+" | "+str(total_distance)+" | "+str(total_time))
        
        kmlfile.write("<Placemark>\n")
        kmlfile.write(link[1])
        kmlfile.write("\n</Placemark>\n")
        
    kmlfile.write("</Folder>\n</kml>\n")
    kmlfile.close()

    

if __name__ == '__main__':
    main()