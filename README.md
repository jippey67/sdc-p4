# advanced lane line finding using various techniques

This repository contains the work I did for the advanced lane line project in the Udacity Self-Driving Car Nanodegree program.

The objective of the project is to find the lane lines on the road, lay them over the road image and show in the image the curvature of the road and the distance of the car from the center of the lane.
There are a couple of steps in the process:
          
1.  correcting the distortion of the camera lens
2.  transforming the image to obtain a bird's view
3.  finding pixels that are part of a lane line
4.  approximate a quadratic function for the lane lines
5.  calculate lane curvature and position of the car relative to the center of the lane
6.  drawing the lane over the camera image

I will go over a these steps now, one by one.

## correcting for camera distortion

With the project came 20 images of a chess board that can be used to calculate the camera matrix and the distance coefficients. The OpenCV function findChessboardCorners can find corners that should be evely distributed on a rectangular grid. With all the corners found from chessboards in multiple positions relative to the camera, another OpenCV function - calibrateCamera - will calculate the camera matrix and the distance coefficients. Those matrices are required as input to another OpenCV function, called undistort, together with a source image to calculate an undistorted image.

The images of the provides chessboards varied along a couple of dimensions:
* most images had a size of 1280x720, but two had to be resized to this format
* most images were in jpg format, but one was in png format.
* the number of corners visible/findable on the chess boards varied considerably. To accomodate for this I looped over a range of possible combinations of corners in x and y direction, for the findChessboardCorners function to provide corners.

Below are two sets of chessboards, with found corners and the undistorted version

<img src="https://cloud.githubusercontent.com/assets/23193240/22209623/7544a81a-e187-11e6-8a8e-23e0c38fc248.jpg" width="356" height="200" />

![chessboardcorners1](https://cloud.githubusercontent.com/assets/23193240/22209623/7544a81a-e187-11e6-8a8e-23e0c38fc248.jpg)Obviously distorted

![undistorted1](https://cloud.githubusercontent.com/assets/23193240/22209777/074825c0-e188-11e6-8eb4-1bb4e94d5f4f.jpg)Rectified

![chessboardcorners2](https://cloud.githubusercontent.com/assets/23193240/22209845/12d339d4-e188-11e6-9da9-5dca1add29c9.jpg)Corners are hard to find on a chessboard of which not all corners are visibles

![undistorted2](https://cloud.githubusercontent.com/assets/23193240/22209639/82526f60-e187-11e6-9405-a707655ef5da.jpg)Rectified

## transforming the image to a bird's view

The question arose whether to find lane lines first and subsequently do the bird's view transform, or do it the other way around. I chose to first change the perspective as the lane lines will then have more or less the same width regardless of the distance from the car. This makes sense as I will use a Sobel operator that uses a kernel size in relation to the edges it needs to find. 

OpenCV provides the warpPerspective function that can will do a perspectiv transform. Alongside the image to be warped, it needs a matrix as input. This matrix is calculated by another OpenCV function: getPerspectiveTransform. This function needs two sets of points: 
1.        points that form a rectangle on the image when seen from a bird's perspective
2.        the points of a rectangle for the image to be warped on
To be able to later on calculate the road curvature and the position of the car with respect to the center of the lane, I need to make a couple of assumptions here:
1.        The camera is at the center of the car, and aligned with the car.
2.        The car is aligned with the road
3.        The road segment used for calculating is straight and the dashed line is 3 meters long
Based on the assumptions a had the perspective transform matrix automatically calculated. The road and car details like lane width in pixels, dashed line length in pixels, and the center of the car with respect to the camera, were saved for later use.

Below are a picture of the road and it's warped version.
![test5](https://cloud.githubusercontent.com/assets/23193240/22211411/368db2b4-e18d-11e6-8098-d6c762348892.jpg) the original

![test5warped](https://cloud.githubusercontent.com/assets/23193240/22211415/387bd6e6-e18d-11e6-90b1-6df428e675a3.jpg) bird's eye perspective

## finding lane line pixels










As there are many parameters to choose (X/Y/direction of the gradient, Colorspace, Layer within colorspace, kernel size, upper and lower thresholds), I created a program that provided sliding bars for each parameter. This allowed me to research many combinations and finally to come up with a set of valid 'pixel selectors'. The strategy I followed was to come up with many different layers and narrow each down to only select lane line pixels
