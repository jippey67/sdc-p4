import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob

def get_camera_matrices(mode = 'load'):

    if mode == 'save':
        images = glob.glob('./camera_cal/calib*.*')
        objpoints = []
        imgpoints = []
        show_dest = True

        for fname in images:
            print(fname)
            img = cv2.imread(fname) #used cv2 as this reads in the png-file directly in uint format

            # two images have different image size; those are resized here
            if img.shape[:2] != (720, 1280):
                img = cv2.resize(img, (1280, 720))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # iterate with various grid sizes, to find valid parameters for finding chessboardcorners
            found = False
            xdir = 9
            while (not found and(xdir>2)):
                ydir = 6
                while (not found and (ydir>2)):
                    ret, corners = cv2.findChessboardCorners(gray, (xdir, ydir), None)
                    if ret == True:
                        objp = np.zeros((ydir * xdir, 3), np.float32)
                        objp[:, :2] = np.mgrid[0:xdir, 0:ydir].T.reshape(-1, 2)
                        imgpoints.append(corners)
                        objpoints.append(objp)
                        found = True
                        img = cv2.drawChessboardCorners(img, (xdir, ydir), corners, ret)
                        plt.imshow(img)

                        plt.show()
                        #cv2.imwrite('./camera_cal/ChessBoardCorners.jpg',img)
                    ydir -= 1
                xdir -= 1

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        if show_dest == True:
            for fname in images:
                print(fname)
                img = cv2.imread(fname)
                dst = cv2.undistort(img, mtx, dist, None, mtx)
                plt.imshow(dst)
                plt.show()

    if mode == 'load':
        mtx = np.load('cam_mtx.npy')
        dist = np.load('cam_dist.npy')

    return mtx, dist

def undistort(img):
    mtx = np.load('cam_mtx.npy')
    dist = np.load('cam_dist.npy')
    dst = cv2.undistort(img, mtx, dist, None, mtx)
    return dst

get_camera_matrices(mode = 'save')