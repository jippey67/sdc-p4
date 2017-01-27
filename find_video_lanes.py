import lane_finder_utils as lfu
import numpy as np
import cv2
from moviepy.editor import VideoFileClip

itf = lfu.image_transformer() # object for transforming images
lf = lfu.lane_finder(num_frames=10) # object for finding lanes

def process_image(image):
    undist = itf.undistort(image) # corrects for camera distortion
    stapel = lfu.stack(undist) # finds lane line pixels in current frame
    warped = itf.warp(stapel) # transforms found pixels to bird eyes view
    coeffs, radius , offset = lf.add_frame(warped) # finds lanes, road radius and relative car position

    # create a polygon for drawing the found lane onto the camera image
    poly = []
    for j in range(2):
        for i in range(720):
            if j == 0:
                x_val = int(coeffs[j][0] * i * i + coeffs[j][1] * i + coeffs[j][2])
                poly.append([x_val, i])
            else:
                x_val = int(coeffs[j][0] * (719-i) * (719-i) + coeffs[j][1] * (719-i) + coeffs[j][2])
                poly.append([x_val, (791-i)])
    filled_poly = cv2.fillPoly(np.zeros_like(stapel), np.int32([poly]), 255)

    unwarped_poly = itf.unwarp(filled_poly) # transform the drawn lane line from birds eye view to camera view
    unwarped_lane = np.dstack((np.zeros_like(unwarped_poly), unwarped_poly, np.zeros_like(unwarped_poly))) #green layer
    image_with_lane_lines = cv2.addWeighted(unwarped_lane, 0.5, image, 1, 0) #combine found lane and original image

    # add textual info to image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image_with_lane_lines, 'road radius (meters): ' + str(radius), (20, 60), font, 1, (255, 255, 255), 2)
    cv2.putText(image_with_lane_lines, 'position car relative to lane center (meters): ' + "{0:.2f}".format(round(offset,2)), (20, 120), font, 1, (255, 255, 255), 2)

    return image_with_lane_lines


clip = VideoFileClip("project_video.mp4")
augmented_clip = clip.fl_image(process_image)
augmented_clip.write_videofile('augmented_video.mp4', audio=False)
