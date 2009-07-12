'''
Created on Jun 8, 2009

@author: Carl Magnuson
'''

import sys, os, optparse, postgresql, subprocess
from data import *


FILE_EXTENSION = ".profileimport"

def main():
    #process command line options and arguments
    #TODO: move reading command line options to separate module
    #TODO: add help for each argument
    p = optparse.OptionParser()
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--cs', default="WGS84")
    p.add_option('--format', default="GPX")
    p.add_option('--gpsbabel_path', default=None)
    p.add_option('--no-sanitize', '--ns', action="store_false", dest="sanitize", default=True)
    p.add_option('--sanitize', '-s', action="store_true", dest="sanitize", default=True)
    p.add_option('--verbose', '-v', action="store_true", default=False)
    options, arguments = p.parse_args()

    if len(arguments) < 1 :
        print("No Input File Specified!")
        sys.exit()

    #use gpsbabel to process file into something easier to digest
    file = arguments[0]
    path = options.gpsbabel_path
    args = " -i "+options.format+" -f "+ file + " -t -o garmin_txt,date=\"DD.MM.YYYY\",datum=\"WGS 84\",dist=ft,prec=6,time=\"HH:mm:ss\",grid=0 -F "+ file+FILE_EXTENSION
    if path==None:
        f = subprocess.Popen("gpsbabel"+args, shell=True)     
    else:
        f = subprocess.Popen(path+args, shell=True)
        
    #read processed file to memory and remove it from disk
    cleaned_input_file = open(file+FILE_EXTENSION,"r")
    cleaned_input = (cleaned_input_file.read()).splitlines()
    cleaned_input_file.close()
    #TODO: fix so this actualy removes the file we created
    os.remove(file+FILE_EXTENSION)

    #parse input file to py 
    segment_list = [Segment()]

    last_lon = 0.0
    last_lat = 0.0
    
    for line in cleaned_input:
        if ((not line.startswith("Trackpoint"))) and (segment_list[-1].get_num_points()>0):
            segment_list.append(Segment())
            last_lon = 0.0
            last_lat = 0.0
            if options.verbose:
                print("processed segment of length: "+str(segment_list[-2].get_num_points()))
        if line.startswith("Trackpoint") and len(line)>75: #is not first point in track
            p = SegmentPoint(line)
            if not (options.sanitize and ((last_lon==p.lon and last_lat==p.lat) or (last_lat==0.0 and last_lon==0.0))):
                #if this is the same as last input - sign of no satelite fix, or the first in the series of valid input
                #not a big deal to throw away one point
                segment_list[-1].add_point(p)
            last_lon = p.lon
            last_lat = p.lat
            
    if options.verbose:
        print(str(len(segment_list))+" segments processed")
        
    #TODO: move db code to separate module
    #connect to database and prepare statements
    #TODO: more informative error code for say wrong db, username, duplicated tracks, etc
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()
    addpt = db.prepare("INSERT INTO userdata VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)")
    setgeom = db.prepare("""UPDATE userdata SET geom=geomfromtext('POINT(' || lon || ' ' || lat || ')', 4326) 
        WHERE geom IS NULL""")
    transaction = db.xact()
    
    #insert each segment to db
    ps = db.prepare("SELECT MAX(trackid) FROM userdata")
    init_trackid = ps()
    if init_trackid[0]==(None,):
        init_trackid=1
        
    transaction.start()
    for segment in segment_list:
        trackid = ps()
        if trackid[0]==(None,):
            trackid=1
        else:
            trackid=trackid[0][0]+1

        pointid=1
        for pt in segment.get_points():
            addpt(trackid, pointid, pt.lon, pt.lat, pt.time, pt.speed, pt.course, pt.altitude,
                  None,pt.distance,None)
            setgeom()
            pointid+=1
            prev_pt = pt
            
    setgeom()
    transaction.commit()
    
    if options.verbose:
        print("All segments committed to database")

    #TODO: just match newly inserted data
    #assign matching roadways to unassigned segments
    #ORIGINAL MATCHING METHOD
    #ps = db.prepare("UPDATE userdata SET gid=find_nearest_link_within_distance(AsText(geom), 0.05, 'ways') WHERE gid IS NULL")
    #ps()
    pointid=1
    trackid=init_trackid
    prev_pt = None
    prev_rd = None
    prev_class = None
    for pt in segment.get_points():
        res = match_with_history(pt, prev_pt, prev_rd, prev_class, pointid, trackid, db)
        if res==None:
            prev_rd = None
            prev_class = None
        else:
            prev_rd = res[0]
            prev_class = res[3]
        pointid+=1
        prev_pt = pt
    
    if options.verbose:
        print("Segments matched to road network data")
    

#derived from map matching method used in:
#"Map matching for intelligent speed adaptation", 
#IET Intelligent Transport Systems
#N. Tradisauskas, J. Juhl, H. Lahrmann, C.S. Jensen
#www.ietdl.org    
def match_with_history(point, previous_point, previous_roadway, previous_class, pointid, trackid, db):
    parmaxdi = 10 #.0001
    parnuldi = 80 #.0008
    parcmaxdi = 100 #.001
    multiplier = 100000
    
    match = db.prepare("""SELECT ways.gid, distance(userdata.geom, ways.the_geom)*"""+str(multiplier)+""" AS distance, LEAST(distance(userdata.geom, geomfromtext('POINT(' || ways.x1 || ' ' || ways.y1 || ')', 4326)), distance(userdata.geom, geomfromtext('POINT(' || ways.x2 || ' ' || ways.y2 || ')', 4326)))*"""+str(multiplier)+""" AS to_intersection, ways.class_id, (ways.reverse_cost<>ways.length) AS one_way, ST_azimuth(geomfromtext('POINT(' || ways.x1 || ' ' || ways.y1 || ')', 4326), geomfromtext('POINT(' || ways.x2 || ' ' || ways.y2 || ')', 4326)) AS heading, (ways.source=w2.source OR ways.target=w2.target OR ways.source=w2.target OR ways.target=w2.source) AS cont_roadway 
    FROM userdata, ways, ways w2 
    WHERE userdata.trackid=$1 AND userdata.pointid=$2 AND expand(userdata.geom, $3) && ways.the_geom AND distance(userdata.geom, ways.the_geom) <= $3 AND w2.gid=$4
    ORDER BY distance ASC""")
    if previous_roadway==None:
        results = match(trackid, pointid, parcmaxdi*2/multiplier, 1)
    else:
        results = match(trackid, pointid, parcmaxdi*2/multiplier, previous_roadway)
        
    weight = []
    for rd in results:
        if rd[1]<parmaxdi:
            weight.append((parcmaxdi + (parmaxdi - rd[1])/2))
        elif rd[1]<parnuldi:
            #aa = parcmaxdi*100/(parmaxdi-parnuldi)  #-142  #500         #50     #DIFF = parcmaxdi-parcnuldi/dist-parcnuldi
            #kk = parcmaxdi - aa*parmaxdi/100        #100 + 142*10/100=114
            #weight.append((kk+aa*rd[1]))            #114 + -142*rd
            weight.append(100*((parnuldi-parmaxdi)-(rd[1]-parmaxdi))/(parnuldi-parmaxdi))   #70/70... 70/60... 100*(70-dist)/70
        else:
            weight.append(0)
    
    row = 0
    for rd in results:
        if rd[0]==previous_roadway: #for continuity of same roadway
            weight[row]+=30
        elif rd[2]<(parmaxdi*2): #if nearby intersection
            weight[row]+=10
            
        #weighting for speed and road classification change
        if rd[3]==previous_class:
            if point.speed>55:
                weight[row]+=20+20*point.speed/55
            else:
                k = 20*point.speed/50
                if k>20:
                    k=20
                weight[row]+=20+k
                
        #weighting for one way streets
        if rd[4]==True:  #is a one way street
            if abs(point.course-rd[5])>85 and point.speed>2:  #not driving close to same heading as one way
                weight[row]-=100
        
        #weighting for direction similarity
        if point.speed>2:  #do not use direction data if car might be stationary with gps direction floating
            weight[row]+=150*(90-(abs(point.course-rd[5])%90))/90
            
        #weighting for topology
        if rd[6]==True:
            weight[row]+=150*50/100 #TODO: adjust this based on measurement certinity... if possible

        row+=1
    
    #TODO: add weighting for shortest distance (W7)
    
    #Find maximum weighted road (with non-negative weight) and assign in db to this data     
    max_weight = 0
    max_road = None
    row = 0
    #print(str(weight)+" "+str(results))
    for rd in results:
        if weight[row]>max_weight:
            max_weight = weight[row]
            max_road = rd
        row+=1

    setgid = db.prepare("UPDATE userdata SET gid=$1 WHERE trackid=$2 AND pointid=$3")
    if max_road!=None:
        setgid(max_road[0], trackid, pointid)
    return max_road

if __name__ == '__main__':
    main()