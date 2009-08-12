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
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--method', default="simple")
    p.add_option('--verbose', '-v', action="store_true", default=False)
    options, arguments = p.parse_args()

    #TODO: try other db drivers to get something Python 2.x compatible.
    #TODO: move db code to separate module
    #connect to database and prepare statements
    #TODO: more informative error code for say wrong db, username, duplicated tracks, etc
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()

    transaction = db.xact()
    transaction.start()

    clear_weights = db.prepare("""UPDATE ways SET to_cost=length/1""")
    clear_weights()

    if options.verbose:
        print("Roadway weightings cleared")
        
    #TODO: read this from a config file or something similar
    weights = [(100,1),(101,55),(102,30),(104,40),(105,25),(106,35),(107,25),(108,25),(109,25),(201,30)]
    
    #TODO: default speeds for roadways based on classification
    default_weight = db.prepare("""UPDATE ways SET to_cost=length/$2 WHERE class_id=$1""")
    for wt in weights:
        default_weight(wt[0],wt[1])
    
    if options.verbose:
        print("Default weights assigned")
    
    simple_weight = db.prepare("""UPDATE ways SET to_cost=length/spavg.sp FROM (SELECT AVG(speed) AS sp, COUNT(gid) AS cnt, gid AS g FROM userdata WHERE gid IS NOT NULL GROUP BY gid) AS spavg
 WHERE gid=spavg.g AND spavg.cnt>10 AND spavg.sp>0""")

    simple_weight()
   
    transaction.commit()
  
    if options.verbose:
        print("Road network data assigned user weights")
    

if __name__ == '__main__':
    main()