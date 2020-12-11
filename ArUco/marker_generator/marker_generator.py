import cv2 as cv
from cv2 import aruco
import numpy as np
import argparse

# parser = argparse.ArgumentParser(description='ArUco marker generator')
# parser.add_argument('--id', help='ArUco id to be generated.')

parser = argparse.ArgumentParser(description='ArUco marker generator')
parser.add_argument('-i','--ids', nargs='+', help='<Required> ArUco id to be generated.', required=True)

# To show the results of the given option to screen.
for _, values in parser.parse_args()._get_kwargs():
    if values is not None:
        for val in values:
            val = int(val)

            # Load the predefined dictionary
            dictionary = aruco.Dictionary_get(aruco.DICT_6X6_250)

            # Generate the marker
            markerImage = np.zeros((200, 200), dtype=np.uint8)
            markerImage = aruco.drawMarker(dictionary, val, 200, markerImage, 1)

            cv.imwrite(('marker_id_%d.png' % (val)), markerImage)
