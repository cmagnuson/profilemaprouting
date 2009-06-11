'''
Created on Jun 8, 2009

@author: Carl Magnuson
'''

import sys, os, optparse, postgresql, subprocess
from data import *

def main():
    #process command line options and arguments
    #TODO: move reading command line options to separate module
    p = optparse.OptionParser()
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--verbose', '-v', action="store_true", default=False)
    options, arguments = p.parse_args()

    if len(arguments) < 1 :
        print("No Output File Specified!")
        sys.exit()
        
    kmlfile = open(arguments[0],"w")
    kmlfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    kmlfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    kmlfile.write("<Folder>\n")
    kmlfile.write("<Style id=\"trkStyle\"><LineStyle><color>ffff0000</color><width>4</width></LineStyle><PolyStyle><color>7f00ff00</color></PolyStyle></Style>\n")


    #TODO: move db code to separate module
    #connect to database and prepare statements
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()
    getpt = db.prepare("SELECT * FROM userdata ORDER BY trackid, pointid ASC")

    points = getpt()
    if len(points)==0:
        sys.exit()

    trackid = 0    
    for pt in points:
        if pt[0]>trackid:
            if trackid>0:
                kmlfile.write("</coordinates>\n</LineString>\n</Placemark>\n")
            trackid = pt[0]
            kmlfile.write("<Placemark>\n")
            kmlfile.write("<styleUrl>#trkStyle</styleUrl>\n")
            kmlfile.write("<name>Track: "+str(trackid)+"</name>\n")
            kmlfile.write("<LineString>\n<coordinates>\n")
        kmlfile.write(str(pt[2])+","+str(pt[3])+","+str(pt[7])+"\n")
        
    kmlfile.write("</coordinates>\n</LineString>\n</Placemark>\n")
    kmlfile.write("</Folder>\n</kml>\n")
    kmlfile.close()
    
if __name__ == '__main__':
    main()