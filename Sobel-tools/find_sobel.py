"""
How to run:
python find_sobel.py <image path>
"""

import argparse
import cv2
import os

from guiutils import Sobel


def main():
    parser = argparse.ArgumentParser(description='Visualizes the line for hough transform.')
    parser.add_argument('filename')

    args = parser.parse_args()

    img = cv2.imread(args.filename)

    cv2.imshow('input', img)

    edge_finder = Sobel(img, filter_size=25, threshold1=55, threshold2=140, colorspace=2, layer=2, method=0)

    print ("Edge parameters:")
    print ("Method: %s" % edge_finder.method())
    print ("Colorspace: %s" % edge_finder.colorspace())
    print ("Layer: %s" % edge_finder.layer())

    print ("Filter Size: %f" % edge_finder.filterSize())
    print ("Threshold1: %f" % edge_finder.threshold1())
    print ("Threshold2: %f" % edge_finder.threshold2())

    (head, tail) = os.path.split(args.filename)

    (root, ext) = os.path.splitext(tail)

    smoothed_filename = os.path.join("output_images", root + "-smoothed" + ext)
    edge_filename = os.path.join("output_images", root + "-edges" + ext)

    cv2.imwrite(edge_filename, edge_finder.edgeImage())

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
