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

        
    #TODO: move db code to separate module
    #connect to database and prepare statements
    #TODO: more informative error code for say wrong db, username, duplicated tracks, etc
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()

    #TODO: default speeds for roadways based on classification
    #default_weights = db.prepare("....)
    simple_weight = db.prepare("""UPDATE ways SET to_cost=spavg.sp*length FROM (SELECT AVG(speed) AS sp, gid AS g FROM userdata WHERE gid IS NOT NULL GROUP BY gid) AS spavg
 WHERE gid=spavg.g""")

    simple_weight()
   
  
    if options.verbose:
        print("Road network data assigned weights")
    

if __name__ == '__main__':
    main()