'''
Created on Jun 9, 2009

@author: Carl Magnuson
'''

import datetime

class SegmentPoint:

    lat = 0.0
    lon = 0.0
    time = 0
    speed = 0.0
    course = 0
    altitude = 0.0
    distance = 0.0


    def __init__(self, lat, lon, time, speed, course, altitude, distance):
        self.lat = float(lat)
        self.lon = float(lon)
        d = datetime.datetime
        self.time = d.strptime(time, "%d.%m.%Y %H:%M:%S")
        self.speed = float(speed)
        self.course = int(course)
        self.altitude = int(altitude)
        self.distance = float(distance)
        
class Segment:
    points = []

    def add_point(self, point):
        self.points.append(point)
        
    def get_points(self):
        return self.points
    
    def get_num_points(self):
        return len(self.points)
    
    def add_point_string(self, input):
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
        point = SegmentPoint(lat,lon,time,speed,course,altitude,distance)
        self.add_point(point)
        
    def __init__(self):
        self.points = []
