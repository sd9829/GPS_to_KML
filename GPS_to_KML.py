"""
this file's purpose is to convert multiple or individual txt files to
kml files. this kml file is made out of clean data, with noise removed.
so we are assuming the resulting kml file to be clean, with its path
being shown in cyan.
contributors: Soumya Dayal, Tiffany-Louisa Ibok, Teresa Schatz
"""

# modules imported in the program
import math
import os

import sys


def addHeader(kmlFile):
    """
    Adds the header to the kml file that we are going to be writing
    :param kmlFile: File name of the program writing to
    :return: none
    """
    header = ''
    header += '<?xml version = "1.0" encoding = "UTF-8"?>\n'
    header += '<kml xmlns = "http://www.opengis.net/kml/2.2">\n'
    header += '<Document>\n'
    header += '\t<Style id = "cyanPoly">\n'
    header += '\t\t<LineStyle>\n'
    header += '\t\t\t<color>Afffff00</color>\n'
    header += '\t\t\t<width>6</width>\n'
    header += '\t\t</LineStyle>\n'
    header += '\t\t<PolyStyle>\n'
    header += '\t\t\t<color>7fffff00</color>\n'
    header += '\t\t</PolyStyle>\n'
    header += '\t</Style>\n'

    kmlFile.write(header)


def getLatAndLong(degreesAndMins, direction):
    """
    this function gets the latitude and longitude from the gps files
    to the kml files, using the degrees and minues.
    :param degreesAndMins: string representing the degrees and mins in latitude/longitude
    :param direction: string representing the direction in latitude/longitude: 'N', 'S', 'E', 'W'
    :returns: float value of the degrees
    """
    try:
        # the degreesAndmins is in the form {degrees}{minutes}.{minutesDecimal}
        # we are finding where degrees ends and minutes starts based on the decimal
        # placement
        dot_index = degreesAndMins.index('.')
        startOfmins = dot_index - 2
        degrees = float(degreesAndMins[:startOfmins])
        mins = float(degreesAndMins[startOfmins:])

        # convert the mins to degrees by dividing by 60 and add it to degrees
        minsIndegrees = mins / 60
        degrees = degrees + minsIndegrees

        # If we're in the southern or western hemisphere, then the degrees should be negative
        if (direction == 'S' or direction == 'W'):
            degrees = degrees * -1
        return degrees

    except:
        # If we run into a problem, then we just return None since we could not get a coordinate
        return None


def getSpeedInMPH(knotSpeed):
    """
    gets the knot speed from the data provided and converts it to mph.
    :param knotSpeed the string value of the speed in knots
    :return: the float value of the speed in mph
    """

    # Convert the speed in knots to a float, and multiply it by 1.151 to convert to mph
    speedInFloat = float(knotSpeed)
    speedInMph = speedInFloat * 1.151
    return speedInMph


def convert_to_kml(gpsFile):
    """
    takes a gps file and coverts the points to a list
    :param gpsFile: gps file pointer
    :return: list of coordinates
    """
    coordinates = []
    # Go through every line in the gps file
    for line in gpsFile:
        try:
            # we are only taking those lines which are starting with GPRMC gps data. this is 
            # the form of noise removal we are doing. the other lines of data are either redundant
            # or contain information we do not want to make the kml file. 
            if line.startswith('$GPRMC'):
                arr = line.split(',')

                # we are going through the line until we find a character 'A' which is a way of
                # determining that the data sentence is valid. if it does not contain that
                # character, it means that there were positioning problems.
                if arr[2] == 'A':

                    # converting the gps value we need: latitude, longitude, speed and headingDirection
                    # into float
                    latitude = getLatAndLong(arr[5], arr[6])
                    longitude = getLatAndLong(arr[3], arr[4])
                    speed = getSpeedInMPH(arr[7])
                    headingDirection = float(arr[8])

                    # if we got a latitude and longitude, it gets appended.
                    if (latitude is not None) and (longitude is not None):
                        coordinate = [longitude, latitude, speed, headingDirection]
                        coordinates.append(coordinate)
        except:
            print('Skipping invalid line.')
    return coordinates


def distFrom(c1, c2):
    """
    finds distance between two coordinates using thr haversine formula for 
    which the following resource was used: https://www.movable-type.co.uk/scripts/latlong.html
    :param c1 the first coordinate
    :param c2 the second coordinate
    :return: the distance between them in meters
    """
    lat1 = c1[0]
    lat2 = c2[0]
    lon1 = c1[1]
    lon2 = c2[1]

    R = 6371000  # metres
    phi1 = lat1 * math.pi / 180  # φ = phi, λ  = lambda in radians
    phi2 = lat2 * math.pi / 180
    changeInPhi = (lat2 - lat1) * math.pi / 180
    changeInLambda = (lon2 - lon1) * math.pi / 180

    # implemtning the haversine formula directly
    a = math.sin(changeInPhi / 2) * math.sin(changeInPhi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(changeInLambda / 2) * math.sin(changeInLambda / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c  # in metres
    return distance


def clean_data(coordinate_list):
    """
    this functions cleans data of any huge jumps or if the car is being parked
    :param coordinate_list: the list of coordinates of the form[long, lat, speed, headingDirection]
    :returns:list of lists of coordinates. if the car is not moving, the data is removed and there are 
                            segmented lists for all huge jumps.
    """

    segment_list = []
    current_segment = []

    # to keep track of previous coordinate
    previousCoordinate = None

    for currentCoordinate in coordinate_list:
        if previousCoordinate == None:
            # always adding if it is the first coordinate
            current_segment.append(currentCoordinate)
            previousCoordinate = currentCoordinate
        else:
            # speed is in mph, distance is in meters.
            currentSpeed = currentCoordinate[2]
            previousSpeed = previousCoordinate[2]

            distanceBetweenCoordinates = distFrom(currentCoordinate, previousCoordinate)
            differenceInSpeeds = abs(currentSpeed - previousSpeed)

            if distanceBetweenCoordinates > 500:
                # this is to ensure that if there are any jumps more
                # than 500 m, it will become a new segmented list
                segment_list.append(current_segment)
                current_segment = [currentCoordinate]
                previousCoordinate = currentCoordinate

            elif differenceInSpeeds > 1 or distanceBetweenCoordinates > 10:
                # this is to ensure that all the points where the car is not
                # moving are removed. both of these processes were to clean the data.
                current_segment.append(currentCoordinate)
                previousCoordinate = currentCoordinate

    # if we finished the loop and still have a current_segment, then we can
    # add it to the list of segments
    if len(current_segment) > 0:
        segment_list.append(current_segment)

    for segment in segment_list:
        # this process resulted in segments which had only 1 point. so we 
        # added a second point so it will be an actual segement so it can be 
        # seen in the kml file. to increase its calrity, we increased the 
        # altitude by 5
        if len(segment) == 1:
            segment[0][2] = 5
            segment.append(segment[0])

    return segment_list


def write_data(segment_list, kmlFile):
    """
    writes a list of coordinates to a kml file
    :param cleaned: list of coordinates to write to the file
    :param kmlFile: kml file pointer
    :return: None
    """
    program = ''

    # For every segment we add a placemark which is a lineString
    for segment in segment_list:

        program += '\t<Placemark>\n'
        program += '\t<styleUrl>#cyanPoly</styleUrl>\n'
        program += '\t<LineString>\n'
        program += '\t\t<Description>Speed in MPH, instead of altitude.</Description>\n'
        program += '\t\t<extrude>1</extrude>\n'
        program += '\t\t<tesselate>1</tesselate>\n'
        program += '\t\t<altitudeMode>absolute</altitudeMode>\n'
        program += '\t\t<coordinates>\n'

        # We add a coordinate to the kml file for every coordinate in the segment
        # here we are setting the z value, which is the altitude, to the speed, so
        # it is easy to tell how fast we are going
        for c in segment:
            latitude = "%6.6f" % c[0]
            longitude = "%6.6f" % c[1]
            speed = "%3.2f" % c[2]
            program += (f"\t\t\t{longitude},{latitude},{speed}\n")

        # Close the placemark
        program += '\t\t</coordinates>\n'
        program += '\t</LineString>\n'
        program += '\t</Placemark>\n'

    # After all the segments, close the document
    program += '</Document>\n'
    program += '</kml>\n'

    # Finally write the file
    kmlFile.write(program)


def runOneFile(gpsFilepath, kmlFilepath):
    """
    this fucntion takes in one single gos file and converts it to a kml file.
    :param gpsFilepath filepath of the gps file to read
    :param kmlFilepath filepath of the kml file to write
    """
    # Open both of the files, the gps file for reading and the kml file for writing
    with open(gpsFilepath, 'r') as gpsFile, open(kmlFilepath, 'w') as kmlFile:
        # First add the header to the kml file
        addHeader(kmlFile)
        # Then convert the gps file to coordinates, clean the list
        coordinate_list = convert_to_kml(gpsFile)
        segment_list = clean_data(coordinate_list)
        # And write the segment data to the file
        write_data(segment_list, kmlFile)


def runAllFiles():
    """
    Converts all the gps files in the FILES_T0_WORK directory
    to kml files in the Results directory.
    """
    # Get all the files in the FILES_ON_MYCOURSES directory using the os module
    files = os.listdir("FILES_ON_MYCOURSES")
    for file in files:
        gpsFilepath = f"FILES_ON_MYCOURSES\\{file}"

        gpsFilename = os.path.splitext(file)[0]
        kmlFilepath = f"Results\\{gpsFilename}.kml"

        runOneFile(gpsFilepath, kmlFilepath)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        # If it was run with no arguments, then convert all files in FILES_ON_MYCOURSES
        runAllFiles()
    elif len(args) == 2:
        # run it with the specific files specified in sys.args
        runOneFile(args[0], args[1])
    else:
        print(
            "Incorrect number of parameters. \nEnter two arguments: one txt file path, and one kml file path. \n Or use with no args to run all the test files")