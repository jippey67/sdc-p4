# advanced lane line finding using various techniques

This repository contains the work I did for the advanced lane line project in the Udacity Self-Driving Car Nanodegree program.

The objective of the project is to find the lane lines on the road, lay them over the road image and show in the image the curvature of the road and the distance of the car from the center of the lane.
There are a couple of steps in the process:
          
1.  correcting the distorture of the camera lens
2.  transforming the image to obtain a bird's view
3.  finding pixels that are part of a lane line
4.  approximate a quadratic function for the lane lines
5.  calculate lane curvature and position of the car relative to the center of the lane
6.  drawing the lane over the camera image

I will go over a these steps now, one by one.

## correcting for camera distorture

With the project came 20 images of a chess board that can be used to calculate the camera matrix and the distance coefficients. The OpenCV function findChessboardCorners can find corners that should be evely distributed on a rectangular grid. With all the corners found from chessboards in multiple positions relative to the camera, another OpenCV function - calibrateCamera - will calculate the camera matrix and the distance coefficients. Those matrices are required as input to another OpenCV function, called undistort, together with a source image to calculate an undistorted image.

The images of the provides chessboards varied along a couple of dimensions:
* most images had a size of 1280x720, but two had to be resized to this format
* most images were in jpg format, but one was in png format.
* the number of corners visible/findable on the chess boards varied considerably. To accomodate for this I looped over a range of possible combinations of corners in x and y direction, for the findChessboardCorners function to provide corners.

