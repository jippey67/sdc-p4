import math, cv2
import numpy as np
from cam_cal import undistort
# finds lane lines in a single frame, and calculates the coordinates of a trapezoid to be warped on a rectangle
# saves the matrices and road info (length of dashed lane, width of lane, camera position relative to the car)

def region_of_interest(img, vertices):
    # defining a blank mask to start with
    mask = np.zeros_like(img)

    # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255

    # filling pixels inside the polygon defined by "vertices" with the fill color
    cv2.fillPoly(mask, vertices, ignore_mask_color)

    # returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def get_lane_coeffs(img,x1,x2,y1,y2):
    points=[]
    for x in range(x1,x2):
        for y in range(y1, y2):
            if img[y,x] == 255:
                points.append((x,y))
    coeffs = np.polyfit(np.array(points)[:,0],np.array(points)[:,1], deg=1)
    return coeffs

def find_rectangle(c1, c2, offset):
    x_vanish = (c2[1] - c1[1]) / (c1[0]-c2[0])
    points = []
    points.append([(719-c1[1])/c1[0],719])
    points.append([x_vanish - offset,(x_vanish - offset) * c1[0] + c1[1]])
    points.append([x_vanish + offset,(x_vanish + offset) * c2[0] + c2[1]])
    points.append([(719-c2[1])/c2[0],719])
    #print(points)
    return points


base_img = undistort(cv2.imread('test_images/test1.jpg'))
img = cv2.cvtColor(base_img,cv2.COLOR_BGR2HLS)
img = img[:,:,2]
sobel_img = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=25)
abs_sobel = np.absolute(sobel_img)
scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
sobel_binary = np.zeros_like(scaled_sobel)
sobel_binary [(scaled_sobel>=55)&(scaled_sobel<=140)] = 255

vertices = np.array([[(215,720),(560, 436), (750,436), (1194,720)]], dtype=np.int32) #for image1
img = region_of_interest(sobel_binary,vertices)

ll_coeffs = get_lane_coeffs(img,0,650,436,720)
rl_coeffs = get_lane_coeffs(img,650,1280,436,720)

src = find_rectangle(ll_coeffs,rl_coeffs,120)
rect = np.array(src)
center_of_car = img.shape[1]/2

line_image = np.copy(img)*0
cv2.line(line_image, (int(rect[0,0]), int(rect[0,1]) ), (int(rect[1,0]), int(rect[1,1])),(255,0,0),10)
cv2.line(line_image, (int(rect[3,0]), int(rect[3,1]) ), (int(rect[2,0]), int(rect[2,1])),(255,0,0),10)
combImg = np.dstack((np.zeros_like(img),line_image,img))

cor_fac = 0.1
src=np.float32(src)
dst=np.float32([[src[0,0],src[0,1]],[src[0,0]+cor_fac*(src[1,0]-src[0,0]),src[1,1]],[src[3,0]-cor_fac*(src[3,0]-src[2,0]),src[2,1]],[src[3,0],src[3,1]]])

M = cv2.getPerspectiveTransform(src,dst)
Minv = cv2.getPerspectiveTransform(dst,src)

warped = cv2.warpPerspective(base_img,M,(1280,720),flags=cv2.INTER_LINEAR)
unwarped = cv2.warpPerspective(warped,Minv,(1280,720),flags=cv2.INTER_LINEAR)

road_details = []
lane_line_piece = np.zeros_like(img)
lane_line_piece = cv2.warpPerspective(img,M,(1280,720),flags=cv2.INTER_LINEAR)
lane_line_piece_isolated = np.zeros_like(img)
lane_line_piece_isolated[400:550,700:1200]=lane_line_piece[400:550,700:1200]

indices_of_lane_piece = np.where(lane_line_piece_isolated == 255)
lane_piece_length = np.max(indices_of_lane_piece[0]) - np.min(indices_of_lane_piece[0])
print('lane_piece in pixels: ',lane_piece_length)
lane_width = rect[3,0] - rect[0,0]
print('lane_width in pixels: ',lane_width)
center_of_car = img.shape[1]/2
print('center of car: ',center_of_car)
road_details.append(['lane_line_piece',lane_piece_length])
road_details.append(['lane_width',lane_width])
road_details.append(['car center',center_of_car])
road_details = np.array(road_details)

np.save('road_details', road_details)
np.save('warper',M)
np.save('unwarper',Minv )

cv2.imshow('lane_piece', lane_line_piece_isolated)
cv2.imshow('autofind perspective', img)
cv2.imshow('autofind lines', combImg)
cv2.imshow('warped', warped)
cv2.imshow('original', base_img)
cv2.imshow('unwarped', unwarped)
cv2.waitKey(0)