# advanced lane line finding using various techniques

This repository contains the work I did for the advanced lane line project in the Udacity Self-Driving Car Nanodegree program.

The objective of the project is to find the lane lines on the road, lay them over the road image and show in the image the curvature of the road and the distance of the car from the center of the lane.
There are a couple of steps in the process:
          
1.  correcting the distortion of the camera lens
2.  finding pixels that are part of a lane line
3.  transforming the image to obtain a bird's view
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

Below are two sets of chessboards, left the distorted image with found corners and right the undistorted version

<img src="https://cloud.githubusercontent.com/assets/23193240/22209623/7544a81a-e187-11e6-8a8e-23e0c38fc248.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22209777/074825c0-e188-11e6-8eb4-1bb4e94d5f4f.jpg" width="356" height="200" />

<img src="https://cloud.githubusercontent.com/assets/23193240/22209845/12d339d4-e188-11e6-9da9-5dca1add29c9.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22209639/82526f60-e187-11e6-9405-a707655ef5da.jpg" width="356" height="200" />

The calculation of the camera matrices was doen with the program cam_cal.py, included in the repository

## finding lane line pixels

The strategy that I employed here is to find various layers that had <u>only</u> lane line pixels in them and subsequently stack them on top of eachother by a binary OR function. This required tuning the various operators at hand to filter out pixels that don't belong to lane lines. I created a tool for doing that, included in this repository (directory Sobel-tools), with slide bars for various parameters that change the behavior of the sobel operator and color masks. With the tool I could obtain a good inside look into how the various parameters interact. The Sobel tool has six sliders, making available changes in: 
* Colorspace
* Layer within the Colorspace
* Method (Sobel-x, Sobel-y, Sobel size of gradient, Sobel direction of gradient)
* Size of the Sobel kernel
* lower threshold
* upper threshold

I ended up finding six layers (Sobel or colormasked) that seemed to be worthwile to include in the final process. However in practice those layers together found an unacceptably large number of pixels not belonging to lane lines, leading to a badly performing pipeline on the video stream. Another reason to include a smaller number of layers is the processing time it took to handle those layers. Experimentally peeling of layers resulted in a leaner pipeline, in which the following to layers are used to find lane line pixels:
* Sobel gradient in x direction on L channel in HLS space with thresholds of 170 and 255
* Color threshold on the S channel in HLS space with thresholds of 20 and 100
Those layers are then combined by adding them up, essentially performing a binary OR

Below are examples of the sobel gradient in x direction and color mask layers

<img src="https://cloud.githubusercontent.com/assets/23193240/22370292/017dc53a-e491-11e6-9b6f-23bf20b4b26e.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22370291/01677258-e491-11e6-9854-4b05dcaf7f6a.jpg" width="356" height="200" /> 

The original image and the combined layer:

<img src="https://cloud.githubusercontent.com/assets/23193240/22370336/3563fca2-e491-11e6-89a1-3b0122ae155f.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22370293/01862702-e491-11e6-9093-c85180ea3c74.jpg" width="356" height="200" /> 

As is clear from the stacked image, a lot of unwanted details are still in the picture. By searching only the most likely neighborhood of the image, only the relevant pixels are found. This is described in the paragraph 4. Also many details will disappear after the bird eyes transform which we will turn to now.

## transforming the image to a bird's view

OpenCV provides the warpPerspective function that can will do a perspectiv transform. Alongside the image to be warped, it needs a matrix as input. This matrix is calculated by another OpenCV function: getPerspectiveTransform. This function needs two sets of points: 
1.        points that form a rectangle on the image when seen from a bird's perspective
2.        the points of a rectangle for the image to be warped on
To be able to later on calculate the road curvature and the position of the car with respect to the center of the lane, I need to make a couple of assumptions here:
1.        The camera is at the center of the car, and aligned with the car.
2.        The car is aligned with the road
3.        The road segment used for calculating is straight and the dashed line is 3 meters long
Based on the assumptions I had the perspective transform matrix automatically calculated. The road and car details like lane width in pixels, dashed line length in pixels, and the center of the car with respect to the camera, were saved for later use.

Below are the warped versions of the color camera image and the stacked layer

<img src="https://cloud.githubusercontent.com/assets/23193240/22370857/f3d39a60-e493-11e6-9066-ddceb8c11b6a.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22370852/eed1683a-e493-11e6-99f8-8e2f53df382a.jpg" width="356" height="200" /> 












As there are many parameters to choose (X/Y/direction of the gradient, Colorspace, Layer within colorspace, kernel size, upper and lower thresholds), I created a program that provided sliding bars for each parameter. This allowed me to research many combinations and finally to come up with a set of valid 'pixel selectors'. The strategy I followed was to come up with many different layers and narrow each down to only select lane line pixels
