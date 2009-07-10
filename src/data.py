'''
Created on Jun 9, 2009

@author: Carl Magnuson
'''

import datetime

#a single point of driving data - constituting one moment in time and place
class SegmentPoint:

    lat = 0.0
    lon = 0.0
    time = 0
    speed = 0.0
    course = 0
    altitude = 0.0
    distance = 0.0

    #method to set initial values, time taken in a string in the format GPSBabel produces
    def setup(self, lat, lon, time, speed, course, altitude, distance):
        self.lat = float(lat)
        self.lon = float(lon)
        d = datetime.datetime
        self.time = d.strptime(time, "%d.%m.%Y %H:%M:%S")
        self.speed = float(speed)
        self.course = int(course)
        self.altitude = int(altitude)
        self.distance = float(distance)
        
    #constructor to build segmentpoint from input string from GPSBabel output
    def __init__(self, input):
        parts = input.split()
        
        if parts[1].startswith("N"):
            lat = float(parts[1].strip("N"))
        else:
            lat = 0 - float(parts[1].strip("S"))
         
        if parts[2].startswith("E"):
            lon = float(parts[2].strip("E"))
        else:
            lon = 0 - float(parts[2].strip("W"))

        time = parts[3]+" "+parts[4]
        speed = parts[12]
        course = parts[14][:len(parts[14])-1]
        altitude = parts[5]
        distance = parts[9]
        self.setup(lat,lon,time,speed,course,altitude,distance)

#constitutes a group of points recorded during one drive        
class Segment:
    points = []

    #appends a point to the end of this collection of points
    def add_point(self, point):
        self.points.append(point)
        
    def get_points(self):
        return self.points
    
    def get_num_points(self):
        return len(self.points)
        
    def __init__(self):
        self.points = []
