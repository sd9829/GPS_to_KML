'''
Soumya Dayal
Tiffany-Louisa Ibok
Teresa Schatz

CSCI 420
Project
'''

import csv
import math

import numpy as np
import sys
import collections
import itertools

from numpy import median
from sklearn.cluster import KMeans

csvFileName1 = "2021_09_AA__GPS_CHECK"
csvFileName2 = "2021_09_BB__GPS_CHECK"

def AgglomerativeAlgo(datapoints):
    # initialize clusters
    clusters = []
    # Size of the smallest cluster merged each time
    sizeOfSmallestClusterMerged = []
    for point_num in range(0,len(datapoints)):
        # hash map with center and members
        cluster = dict({"center": "", "members": ""}) # create new, empty cluster

        center = [datapoints[point_num]]
        cluster['center'] = center # add data point to its own cluster
        member_list = [center]
        cluster['members'] = member_list
        clusters.append(cluster)

    # Agglomerate
    while len(clusters) > 1:
        # initialize to empty and infinity
        closest_cluster1 = ""
        closest_cluster2 = ""
        closest_distance = math.inf
        for index1 in range(0, len(clusters) - 1):
            for index2 in range(index1+1, len(clusters)):
                # get cluster1 center and cluster2 center
                cluster = clusters[index1] #cluster1
                cluster1Center = cluster['center']
                cluster = clusters[index2] #cluster2
                cluster2Center = cluster['center']

                # calculate Euclidean distance
                distance = Euclidean_calculations(cluster1Center,cluster2Center)

                # If closer then
                if distance < closest_distance:
                    closest_distance = distance
                    closest_cluster1 = clusters[index1]
                    closest_cluster2 = clusters[index2]

        # get cluster 2 info
        cluster2_info = closest_cluster2['members']
        sizeOfCluster2 = len(cluster2_info)
        # get cluster1 members
        member_list = closest_cluster1['members']
        sizeOfCluster1 = len(member_list)

        # keep track of smallest cluster merged
        sizeOfSmallestClusterMerged.append(min(sizeOfCluster1, sizeOfCluster2))

        # merge closest_cluster1 and closest_cluster2
        for member in cluster2_info:
            member_list.append(member)
        closest_cluster1['members'] = member_list

        # remove cluster 2
        clusters.remove(closest_cluster2)

        # new center with the median of values
        new_members = closest_cluster1['members']
        # find median of each attribute to form new center of mass
        new_center = []
        for attributeIndex in range(0, 2):
            attributeData = []
            for clusterIndex in range(0, len(new_members)):
                tempCluster = new_members[clusterIndex]
                attributeData.append(tempCluster[0][attributeIndex])
            new_center.insert(attributeIndex, median(attributeData))

        closest_cluster1['center'] = [new_center]

    return sizeOfSmallestClusterMerged

'''
Calculates the euclidean distance between two Center of Masses
Uses each attribute
'''
def Euclidean_calculations(x,y):
    summation = 0
    xlat = x[0][0]
    xlong = x[0][1]
    ylat = y[0][0]
    ylong = y[0][1]
    subtraction = xlat - ylat
    squared = pow(subtraction, 2)
    summation += squared
    subtraction = xlong - ylong
    squared = pow(subtraction, 2)
    summation += squared
    distance = pow(summation, .5)
    return distance

def ProcessAgglomeration(coordinates):
    sizeOfSmallestClusterMerged = AgglomerativeAlgo(coordinates)
    # determine the first big jump at the end of sizeOfSmallestClusterMerged
    # then count from that jump to end of list + 1 = number of natural clusters

    # currently set to 5, but should be calculated
    kMeans = KMeans(n_clusters=5).fit(coordinates)

    clusterCenters = kMeans.cluster_centers_
    return clusterCenters

def CreateCoordinate(point):
    if str(point[0]) == "$GPGGA":
        latitudeField = str(point[2])
        latitudeDegree = int(str(latitudeField[0:2]).strip('0'))
        latitudeMinutes = float(str(latitudeField[2:]).strip('0'))
        latitudeMinutes = latitudeMinutes / 60
        latitude = round(latitudeDegree + latitudeMinutes, 6)
        if str(point[3]) == "S":
            latitude = 0 - latitude

        longitudeField = str(point[4])
        longitudeDegree = int(str(longitudeField[0:3]).strip('0'))
        longitudeMinutes = float(str(longitudeField[3:]).strip('0'))
        longitudeMinutes = longitudeMinutes / 60
        longitude = round(longitudeDegree + longitudeMinutes, 6)
        if str(point[5]) == "W":
            longitude = 0 - longitude

        altitude = str(point[9])

        return [latitude, longitude, altitude, "$GPGGA"]

    elif str(point[0]) == "$GPRMC":
        latitudeField = str(point[3])
        latitudeDegree = int(str(latitudeField[0:2]).strip('0'))
        latitudeMinutes = float(str(latitudeField[2:]).strip('0'))
        latitudeMinutes = latitudeMinutes / 60
        latitude = round(latitudeDegree + latitudeMinutes, 6)
        if str(point[4]) == "S":
            latitude = 0 - latitude

        longitudeField = str(point[5])
        longitudeDegree = int(str(longitudeField[0:3]).strip('0'))
        longitudeMinutes = float(str(longitudeField[3:]).strip('0'))
        longitudeMinutes = longitudeMinutes / 60
        longitude = round(longitudeDegree + longitudeMinutes, 6)
        if str(point[6]) == "W":
            longitude = 0 - longitude

        speedInKnots = str(point[7])

        return [latitude, longitude, speedInKnots, "$GPRMC"]

def unitVector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angleBetween(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2':: """
    v1_u = unitVector(v1)
    v2_u = unitVector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def CreateLatLongArray(fileNames):
    both = []
    index = 0
    for fileName in fileNames:
        # read in data
        with open(fileName, 'r') as csvFile:
            csvReader = csv.reader(csvFile)
            for row in csvReader:
                if len(row) > 0 and (str(row[0]).startswith("$GPGGA") | str(row[0]).startswith("$GPRMC")):
                    coordinate = CreateCoordinate(row)
                    both.append([coordinate[0],coordinate[1]])
                    index += 1
    return both

def CreateDictionary(fileName):
    allData = []
    dictionaries = []
    # read in data
    with open(fileName, 'r') as csvFile:
        csvReader = csv.reader(csvFile)
        for row in csvReader:
            if len(row) > 0 and (str(row[0]).startswith("$GPGGA") | str(row[0]).startswith("$GPRMC")):
                allData.append(row)

    for index in range(0, len(allData)):
        pt1 = CreateCoordinate(allData[index])
        tempDict = {"type": "", "members": []}
        if len(dictionaries) > 0:
            tempDict["type"] = dictionaries[-1]["type"]
            tempDict["members"] = dictionaries[-1]["members"]

        if (index + 1 < len(allData) and index + 13 < len(allData)
                and index + 14 < len(allData)):
            # find other points to create vectors
            pt2 = CreateCoordinate(allData[index + 1])
            pt3 = CreateCoordinate(allData[index + 13])
            pt4 = CreateCoordinate(allData[index + 14])

            vect1 = [pt1[0] - pt2[0], pt1[1] - pt2[1]]
            vect2 = [pt3[0] - pt4[0], pt3[1] - pt4[1]]

            # find angle
            angle = np.degrees(angleBetween(vect1, vect2))
            if (abs(angle) > 60 and abs(angle) < 125):
                # is a turn
                x = np.array([vect1[0], vect1[1], 0])
                y = np.array([vect2[0], vect2[1], 0])
                result = np.cross(x, y)
                id = ""
                if result[2] < 0:
                    id = "LeftTurn"
                else:
                    id = "RightTurn"

                if tempDict["type"] == id:
                    members = tempDict["members"]
                    members.append(pt1)
                    tempDict["members"] = members
                    dictionaries[-1] = tempDict
                else:
                    newTurn = {"type": id, "members" : [pt1]}
                    dictionaries.append(newTurn)
            else:
                if tempDict["type"] == "line":
                    members = tempDict["members"]
                    members.append(pt1)
                    tempDict["members"] = members
                    dictionaries[-1] = tempDict
                else:
                    newTurn = {"type": "line", "members" : [pt1]}
                    dictionaries.append(newTurn)

        elif (str(pt1[3]) == "$GPRMC" and float(pt1[2]) < 0.50):
           # is a stop (less than 1 knot)
           if tempDict["type"] == "stop":
               members = tempDict["members"]
               members.append(pt1)
               tempDict["members"] = members
               dictionaries[-1] = tempDict
           else:
               newTurn = {"type": "stop", "members": [pt1]}
               dictionaries.append(newTurn)

        else:
            if tempDict["type"] == "line":
                members = tempDict["members"]
                members.append(pt1)
                tempDict["members"] = members
                dictionaries[-1] = tempDict
            else:
                newTurn = {"type": "line", "members": [pt1]}
                dictionaries.append(newTurn)
    return dictionaries

'''
Creates a kml file with turn markers and plain line
'''
def CreateKmlFile(fileName, listOfFileDictionaries):
    # Open the file to be written.
    newKmlFile = open(fileName, 'w')
    newKmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    newKmlFile.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
    newKmlFile.write("<Document>\n")
    newKmlFile.write("\n<Style id=\"line\">"
                     "\n    <LineStyle>"
                     "\n        <color>50f0ff14</color>"
                     "\n    </LineStyle>"
                     "\n</Style>")

    for fileDictionaries in listOfFileDictionaries:
        for dict in fileDictionaries:
            if dict["type"] == "line":
                newKmlFile.write("<Placemark>"
                                 "\n <description>No turn, no stop, not a common location</description>"
                                 "\n    <LineString>"
                                 "\n    <styleUrl>#line</styleUrl>"
                                 "\n    <coordinates>")
                for member in dict["members"]:
                    newKmlFile.write("\n          " + str(member[1]) + ", " + str(member[0]))
                newKmlFile.write("\n    </coordinates>"
                                 "\n    </LineString>"
                                 "\n</Placemark>\n")

            elif dict["type"] == "RightTurn":
                newKmlFile.write("\n<Placemark>"
                                 "\n    <description>Green pin for a right turn</description>"
                                 "\n    <Style id=\"RightTurn\">"
                                 "\n        <IconStyle>"
                                 "\n            <color>ff00ff00</color>"
                                 "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href></Icon>"
                                 "\n        </IconStyle>"
                                 "\n    </Style>"
                                 "\n    <Point>"
                                 # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                 "\n        <coordinates>" +
                                 str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                 + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                 "\n        </coordinates>"
                                 "\n    </Point>"
                                 "\n</Placemark>\n")

            elif dict["type"] == "LeftTurn":
                newKmlFile.write("\n<Placemark>"
                                 "\n    <description>Yellow pin for a left turn</description>"
                                 "\n    <Style id=\"LeftTurn\">"
                                 "\n        <IconStyle>"
                                 "\n            <color>ff00ffff</color>"
                                 "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png</href></Icon>"
                                 "\n        </IconStyle>"
                                 "\n    </Style>"
                                 "\n    <Point>"
                                 # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                 "\n        <coordinates>"
                                 + str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                 + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                 "\n        </coordinates>"
                                 "\n    </Point>"
                                 "\n</Placemark>\n")

            elif dict["type"] == "stop":
                newKmlFile.write("\n<Placemark>"
                                 "\n    <description>Red pin for a stop</description>"
                                 "\n    <Style id=\"Stop\">"
                                 "\n        <IconStyle>"
                                 "\n            <color>ff0000ff</color>"
                                 "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-blank.png</href></Icon>"
                                 "\n        </IconStyle>"
                                 "\n    </Style>"
                                 "\n    <Point>"
                                 # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                 "\n        <coordinates>"
                                 + str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                 + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                 "\n        </coordinates>"
                                 "\n    </Point>"
                                 "\n</Placemark>")

            elif dict["type"] == "frequentPlace":
                newKmlFile.write("\n<Placemark>"
                                     "\n    <description>Blue pin for a frequent place</description>"
                                     "\n    <Style id=\"FrequentPlace\">"
                                     "\n        <IconStyle>"
                                     "\n            <color>ffff0000</color>"
                                     "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-blank.png</href></Icon>"
                                     "\n        </IconStyle>"
                                     "\n    </Style>"
                                     "\n    <Point>"
                                     "\n        <coordinates>"
                                     + str(dict["members"][0][1])
                                     + ", " + str(dict["members"][0][0]) +
                                     "\n        </coordinates>"
                                     "\n    </Point>"
                                     "\n</Placemark>")

    newKmlFile.write(" </Document>\n" +
                     "</kml>")
    newKmlFile.close()

'''
Creates a kml file with turn markers and plain line
'''
def CreateIndivKmlFile(fileName, listOfFileDictionaries):
    index = 0
    needNewFile = False

    fullFileName = fileName + "__" + str(index) + ".kml"
    newKmlFile = open(fullFileName, 'w')
    newKmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    newKmlFile.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
    newKmlFile.write("<Document>\n")
    newKmlFile.write("\n<Style id=\"line\">"
                     "\n    <LineStyle>"
                     "\n        <color>50f0ff14</color>"
                     "\n    </LineStyle>"
                     "\n</Style>")

    for fileDictionaries in listOfFileDictionaries:
        for dict in fileDictionaries:
            if needNewFile:
                newKmlFile.write(" </Document>\n" +
                                 "</kml>")
                newKmlFile.close()
                index += 1
                fullFileName = fileName + "__" + str(index) + ".kml"
                newKmlFile = open(fullFileName, 'w')
                newKmlFile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
                newKmlFile.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
                newKmlFile.write("<Document>\n")
                newKmlFile.write("\n<Style id=\"line\">"
                                 "\n    <LineStyle>"
                                 "\n        <color>50f0ff14</color>"
                                 "\n    </LineStyle>"
                                 "\n</Style>")
                needNewFile = False

            if dict["type"] == "line":
                newKmlFile.write("<Placemark>"
                                     "\n <description>No turn, no stop, not a common location</description>"
                                     "\n    <LineString>"
                                     "\n    <styleUrl>#line</styleUrl>"
                                     "\n    <coordinates>")
                for member in dict["members"]:
                    newKmlFile.write("\n          " + str(member[1]) + ", " + str(member[0]))
                newKmlFile.write("\n    </coordinates>"
                                     "\n    </LineString>"
                                     "\n</Placemark>\n")

            elif dict["type"] == "RightTurn":
                newKmlFile.write("\n<Placemark>"
                                     "\n    <description>Green pin for a right turn</description>"
                                     "\n    <Style id=\"RightTurn\">"
                                     "\n        <IconStyle>"
                                     "\n            <color>ff00ff00</color>"
                                     "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href></Icon>"
                                     "\n        </IconStyle>"
                                     "\n    </Style>"
                                     "\n    <Point>"
                                     # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                     "\n        <coordinates>" +
                                     str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                     + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                     "\n        </coordinates>"
                                     "\n    </Point>"
                                     "\n</Placemark>\n")

            elif dict["type"] == "LeftTurn":
                newKmlFile.write("\n<Placemark>"
                                     "\n    <description>Yellow pin for a left turn</description>"
                                     "\n    <Style id=\"LeftTurn\">"
                                     "\n        <IconStyle>"
                                     "\n            <color>ff00ffff</color>"
                                     "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/ylw-blank.png</href></Icon>"
                                     "\n        </IconStyle>"
                                     "\n    </Style>"
                                     "\n    <Point>"
                                     # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                     "\n        <coordinates>"
                                     + str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                     + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                     "\n        </coordinates>"
                                     "\n    </Point>"
                                     "\n</Placemark>\n")

            elif dict["type"] == "stop":
                newKmlFile.write("\n<Placemark>"
                                     "\n    <description>Red pin for a stop</description>"
                                     "\n    <Style id=\"Stop\">"
                                     "\n        <IconStyle>"
                                     "\n            <color>ff0000ff</color>"
                                     "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/red-blank.png</href></Icon>"
                                     "\n        </IconStyle>"
                                     "\n    </Style>"
                                     "\n    <Point>"
                                     # "\n <coordinates>" + str(pt1[1]) + ", " + str(pt1[0]) + ", " + str(pt1[2]) +
                                     "\n        <coordinates>"
                                     + str(dict["members"][(int)(len(dict["members"]) / 2)][1])
                                     + ", " + str(dict["members"][(int)(len(dict["members"]) / 2)][0]) +
                                     "\n        </coordinates>"
                                     "\n    </Point>"
                                     "\n</Placemark>")

            elif dict["type"] == "frequentPlace":
                newKmlFile.write("\n<Placemark>"
                                     "\n    <description>Blue pin for a frequent place</description>"
                                     "\n    <Style id=\"FrequentPlace\">"
                                     "\n        <IconStyle>"
                                     "\n            <color>ffff0000</color>"
                                     "\n            <Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-blank.png</href></Icon>"
                                     "\n        </IconStyle>"
                                     "\n    </Style>"
                                     "\n    <Point>"
                                     "\n        <coordinates>"
                                     + str(dict["members"][1])
                                     + ", " + str(dict["members"][0]) +
                                     "\n        </coordinates>"
                                     "\n    </Point>"
                                     "\n</Placemark>")

            #size = os.path.getsize(newKmlFile)
            size = newKmlFile.tell()
            if size >= 3500000:
                needNewFile = True
        needNewFile = True
    newKmlFile.write(" </Document>\n" +
                     "</kml>")
    newKmlFile.close()

'''Main'''
def main(listOfFiles, kmlFileName):
    fileDictionaries = []
    for fileName in listOfFiles:
        dictionary = CreateDictionary(fileName)
        fileDictionaries.append(dictionary)

    # find frequent places
    latitudeLongitude = CreateLatLongArray(listOfFiles)
    counts = collections.defaultdict(int)
    for coordinate in latitudeLongitude:
        for pair in itertools.combinations(coordinate, 2):
            counts[pair] += 1

    frequentPlaces = []
    for pair, freq in counts.items():
        if(freq > 100):
            frequentPlaces.append([pair[0], pair[1]])

    frequentPlacesClusterCenters = ProcessAgglomeration(frequentPlaces)
    frequentPlaces = []
    for pair in frequentPlacesClusterCenters:
        frequentPlaces.append({"type": "frequentPlace", "members": [pair[0], pair[1]]})

    fileDictionaries.append(frequentPlaces)
    CreateIndivKmlFile("TestFreqPlacesWithEverything", fileDictionaries)
    #***
    # create one kml file from all the data
    #CreateIndivKmlFile(kmlFileName[:-4], fileDictionaries)
    #CreateKmlFile(kmlFileName, fileDictionaries)

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        list = sys.argv[1:-1]
        kmlFileName = sys.argv[-1]
        main(list, kmlFileName)
    else:
        print("Number of command line args not correct")
