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
7.  discussion

I will go over a these steps now, one by one.

## 1. correcting for camera distortion

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

## 2. finding lane line pixels

The strategy that I employed here is to find various layers that had <u>only</u> lane line pixels in them and subsequently stack them on top of eachother by a binary OR function. This required tuning the various operators at hand to filter out pixels that don't belong to lane lines. I created a tool, based on the code from a colleague student Maunesh, for doing that, The tool is included in this repository (directory Sobel-tools), with slide bars for various parameters that change the behavior of the sobel operator and color masks. With the tool I could obtain a good inside look into how the various parameters interact. The Sobel tool has six sliders, making available changes in: 
* Colorspace
* Layer within the Colorspace
* Method (Sobel-x, Sobel-y, Sobel size of gradient, Sobel direction of gradient)
* Size of the Sobel kernel
* lower threshold
* upper threshold

Below is a screenshot from the tool, showing the slide bars and the resulting output image.

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

## 3. transforming the image to a bird's view

OpenCV provides the warpPerspective function that can will do a perspectiv transform. Alongside the image to be warped, it needs a matrix as input. This matrix is calculated by another OpenCV function: getPerspectiveTransform. This function needs two sets of points: 
1.        points that form a rectangle on the image when seen from a bird's perspective
2.        the points of a rectangle for the image to be warped on
To be able to later on calculate the road curvature and the position of the car with respect to the center of the lane, I need to make a couple of assumptions here:
1.        The camera is at the center of the car, and aligned with the car.
2.        The car is aligned with the road
3.        The road segment used for calculating is straight and the dashed line is 3 meters long
Based on these assumptions I had the perspective transform matrix automatically calculated. The left and right lane provide a vanishing point where they intersect. Moving back a little towards the car on those lines provided a bird's eyes rectangle, that from the camera view was around 700 pixels wide near the car and 40 pixels wide at the far end. The road and car details like lane width in pixels, dashed line length in pixels, and the center of the car with respect to the camera, were saved for later use.

Below are the warped versions of the color camera image and the stacked layer

<img src="https://cloud.githubusercontent.com/assets/23193240/22370857/f3d39a60-e493-11e6-9066-ddceb8c11b6a.jpg" width="356" height="200" /> 
<img src="https://cloud.githubusercontent.com/assets/23193240/22370852/eed1683a-e493-11e6-99f8-8e2f53df382a.jpg" width="356" height="200" /> 

The calculation of the warp and unwarp matrices was done with the program auto_persp_transf.py, included in the repository

## 4. approximate a quadratic function for the lane lines

Based on the bird eyes view of the stacked layer the calculations of parameters of the left and right lane lines are done. To obtain approximate positions in x-direction of the lane lines, a histogram is taken of the sum of all found pixels in all columns. This results in peaks where many pixels are found. In the picture below theres is a clear peak for the left lane line. For the right lane, there are two peaks found, caused by the occurence of dashed lanes in the picture. The algortihm finds the right place to start, as the first of the right lane peaks is a little higher than the second one.

<img src="https://cloud.githubusercontent.com/assets/23193240/22371874/161c5642-e49a-11e6-8746-ac679475a688.png" width="356" height="200" /> 

The x-locations of those peaks are the starting point for finding all the assumed lane line pixels by moving a box upwards over the image, and adding all found pixels in the box to the list of assumed lane line pixels. Each box starts on the center of x-positions found on the layer beneath it, making it follow the lane line. A box size of 200 pixels wide and 50 pixels high provided good results. Only the lower 10 levels (of 50 pixels) are scanned, because in the upper part some scenery pixels are included. With the found lane pixels a quadratic fit is done to obtain the formula for the left and right lane line. Once the first image is handled each subsequent image is scanned from the x-positions found by providing the formulas for the left and righ lane lines with the bottom y-value (719).

This method of finding the lane lines provided reliable lanes, albeit quite jittery. I therefore introduced a smoothing mechanism by calculating a moving and weighted average of the function parameters. The last 10 frames are used where the most recent had a weight of 10. Each earlier frame had the weight decreased by 1. This provide a much smoother lane line, weheras the history was short enough (10 frames is less than half a second) to be relevant. 

## 5. calculate lane curvature and position of the car relative to the center of the lane

In the calculation of the image-to-birds eye transform, I calculated lane width, dashed lane line and position of the camera in the car (obtained from viewing many images: The hood seems to disappear on the same distances left and right from the center of the image). Those distances are all in pixel space and need to be converted to meter space before useful conclusion can be drawn. Based on the U.S. regulations for highways a assumed the lane width to be 3.7 meters, and the dashed lane lines to be 3 meters long. 

For the curvature of the road I took the average of the parameters of the left and right lane line, and calculated the curvature of the road at the level nearest to the car (y=719), and of course in bird eyes view. The position of the car relative to the road was calculated by averaging the x-values of the left and right lane line, also at the nearest position to the car. The distance in pixels from the center of the image was converted to meters, where a negative value means that the car is on the left side of the lane, and a positive value that the car is on the right side of the lane.

## 6. drawing the lane over the camera image

With the found lane lines in bird eyes view, a lane was plotted in this perspective. This plot was then unwarped, and stacked as a green layer on top of the original (but corrected for camera distortion) image. Lane radius and relative position of the car were added to the image as text. The resulting video can be downloaded [here:](https://github.com/jippey67/sdc-p4/blob/master/project_video.mp4)

The pipeline is run from the program find_video_lanes.py, while many functions and classes are included from lane_finder_utils.py. Both files are included in the repository

## 7. discussion

This project was quite demanding. It is not easy to discriminate lane line pixels from others. Playing with the various color spaces, Sobel filters and color masks provided me with an increasing insight in what might work and what absolutely didn't work. Averaging the lane lines over a couple of frames did the job for making the lane lines relatively smooth, but as can be seen from the video, the algorithm had difficulties to lock to the dashed lane line.

A subsequent step would be to isolate lane segments and identify whether they fit on a smootly curving line. I think that is what humans do when following a dashed line: follow the line as if it weren't dashed, and see if you encounter the next section. But it's time to go onto the next project, so I'll leave it as it is for the moment.
