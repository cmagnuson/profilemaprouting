'''
Created on Jun 8, 2009

@author: Carl Magnuson
'''

import sys, os, optparse, postgresql, subprocess

FILE_EXTENSION = ".profileimport"

def main():
    #process command line options and arguments
    #TODO: move reading command line options to separate module
    p = optparse.OptionParser()
    p.add_option('--db_ip', default="localhost")
    p.add_option('--db_user', default="route")
    p.add_option('--db_pass', default="route")
    p.add_option('--db_name', default="osm")
    p.add_option('--cs', default="WGS84")
    p.add_option('--gpsbabel_path', default=None)
    options, arguments = p.parse_args()

    if len(arguments) < 1 :
        print("No Input File Specified!")
        sys.exit()

    #use gpsbabel to process file into something easier to digest
    file = arguments[0]
    path = options.gpsbabel_path
    args = " -i gpx -f "+ file + " -t -o garmin_txt,date=\"DD.MM.YYYY\",datum=\"WGS 84\",dist=m,prec=6,time=\"HH:mm:ss\",grid=0 -F "+ file+FILE_EXTENSION
    if path==None:
        f = subprocess.Popen("gpsbabel"+args, shell=True)     
    else:
        f = subprocess.Popen(path+args, shell=True)
        
    #read processed file to memory and remove it from disk
    cleaned_input_file = open(file+FILE_EXTENSION,"r")
    cleaned_input = cleaned_input_file.read()
    cleaned_input_file.close()
    os.remove(file+FILE_EXTENSION)

    #TODO: move db code to separate module
    db = postgresql.open("pq://"+options.db_user+":"+options.db_pass+"@"+
                         options.db_ip+"/"+options.db_name)
    db.connect()


if __name__ == '__main__':
    main()