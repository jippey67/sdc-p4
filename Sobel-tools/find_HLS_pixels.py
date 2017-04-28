"""
How to run:
python find_HLS_pixels.py <image path>
"""

import argparse
import cv2
import os

from guiutils import HLS


def main():
    parser = argparse.ArgumentParser(description='Visualizes the line for hough transform.')
    parser.add_argument('filename')

    args = parser.parse_args()

    img = cv2.imread(args.filename)

    cv2.imshow('input', img)

    edge_finder = HLS(img, 0, 255, 1)


    print ("Edge parameters:")
    print ("Layer: %s" % edge_finder.layer())
    print ("Threshold1: %f" % edge_finder.threshold1())
    print ("Threshold2: %f" % edge_finder.threshold2())

    (head, tail) = os.path.split(args.filename)

    (root, ext) = os.path.splitext(tail)

    smoothed_filename = os.path.join("output_images", root + "-smoothed" + ext)
    edge_filename = os.path.join("output_images", root + "-edges" + ext)



    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
