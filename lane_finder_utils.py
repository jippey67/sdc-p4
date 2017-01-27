import numpy as np
import cv2

class image_transformer:
    # loads precalculated transformation matrices
    # provides methods for various transformations
    def __init__(self):
        self._mtx = np.load('cam_mtx.npy')
        self._dist = np.load('cam_dist.npy')
        self._M = np.load('warper.npy')
        self._Minv = np.load('unwarper.npy')

    def undistort(self, img):
        return cv2.undistort(img, self._mtx, self._dist, None, self._mtx)

    def warp(self, img):
        return cv2.warpPerspective(img, self._M, (1280, 720), flags=cv2.INTER_LINEAR)

    def unwarp(self, img):
        return cv2.warpPerspective(img, self._Minv, (1280, 720), flags=cv2.INTER_LINEAR)

def stack(image, s_thresh=(170, 255), sx_thresh=(20, 100)):
    # finds lane pixels in various layers and stacks them onto one layer
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HLS).astype(np.float)
    l_channel = hsv[:, :, 1]
    s_channel = hsv[:, :, 2]

    # Sobel x
    sobelx = cv2.Sobel(l_channel, cv2.CV_64F, 1, 0)  # Take the derivative in x
    abs_sobelx = np.absolute(sobelx)  # Absolute x derivative to accentuate lines away from horizontal
    scaled_sobel = np.uint8(255 * abs_sobelx / np.max(abs_sobelx))

    # Threshold x gradient
    sxbinary = np.zeros_like(scaled_sobel, dtype=int)
    sxbinary[(scaled_sobel >= sx_thresh[0]) & (scaled_sobel <= sx_thresh[1])] = 255
    sxbinary = np.uint8(sxbinary)

    # Threshold color channel
    s_binary = np.zeros_like(s_channel, dtype=int)
    s_binary[(s_channel >= s_thresh[0]) & (s_channel <= s_thresh[1])] = 255
    s_binary = np.uint8(s_binary)

    stacked_img = sxbinary+s_binary
    return stacked_img

def first_find(lane_pixel_img):
    # finds the approximate location of the lanes based on sum of pixels in vertical direction
    histogram = np.sum(lane_pixel_img[int(lane_pixel_img.shape[0]/2):,:], axis=0)
    left_max_loc = (np.where(histogram[:int(lane_pixel_img.shape[1]/2)] == histogram[:int(lane_pixel_img.shape[1]/2)].max()))[0][0]
    right_max_loc = np.where(histogram[int(lane_pixel_img.shape[1]/2):] == histogram[int(lane_pixel_img.shape[1]/2):].max())[0][0]+int(lane_pixel_img.shape[1]/2)
    return (left_max_loc,right_max_loc)

def find_lanes(stacked_img, base_points=(303,1028),first_frame=False):
    # finds the lanes by moving a box over the image and adding found points to the collection
    # does a fit of a quadratic function to obtain the lane line equations

    if first_frame:
        base_points = first_find(stacked_img)

    box_width = 200
    box_height = 50
    maxlevel = 10
    coeffs = np.zeros((2,3),dtype=float)

    for j in range(2):
        lane = []
        average_x = base_points[j]
        for x in range(max(average_x-(int(box_width/2)),0),min(average_x+(int(box_width/2)),1280)):
            for y in range(719,719-box_height,-1):
                #print(j, stacked_img.shape)
                if stacked_img[y,x] > 0:
                    lane.append([x,y])
        if lane:
            average_x = int(np.average(np.array(lane)[:,0])) # only change average_x if pixels are found

        for level in range(1,maxlevel):
            lane_piece=[]
            for x in range(max(average_x - (int(box_width / 2)),0), min(average_x + (int(box_width / 2)),1280)):
                for y in range(719 - level * box_height, 719 - (level + 1) * box_height, -1):
                    if stacked_img[y, x] > 0:
                        lane_piece.append([x, y])
            if lane_piece:
                average_x = int(np.average(np.array(lane_piece)[:, 0]))
                lane.extend(lane_piece)

        coeffs[j] = np.polyfit(np.array(lane)[:, 1], np.array(lane)[:, 0], deg=2)

    return coeffs

class lane_finder:
    # initiates lane finding, keeps history of found lane coefficients
    # averages weighted coefficients over 'num_frames' frames
    # calculates road radius and distance of car from lane center
    def __init__(self,num_frames=10):
        self._first_frame = True
        self._num_frames = num_frames
        self._params = []
        self._params_keep = []
        self._weighted_params = np.zeros((2,3),dtype=float)
        self._road_details = np.load('road_details.npy')
        line_in_px = np.float(self._road_details[0,1])
        width_in_px = np.float(self._road_details[1,1])
        self._car_center = np.float(self._road_details[2,1])
        line_in_m = 3
        width_in_m = 3.7
        self._y_px_per_m = line_in_px / line_in_m
        self._x_px_per_m = width_in_px / width_in_m

    def add_frame(self, img):
        if self._first_frame:
            coeffs = find_lanes(stacked_img=img,first_frame=True)
            self._first_frame=False
            self._params.append(coeffs)
            self._params_keep.append([1,1])
        else:
            index = len(self._params) - 1
            loc1 = int(self._params[index][0,0]*719*719+self._params[index][0,1]*719+self._params[index][0,2])
            loc2 = int(self._params[index][1,0]*719*719+self._params[index][1,1]*719+self._params[index][1,2])
            coeffs = find_lanes(stacked_img=img, base_points=(loc1,loc2), first_frame=False)
            self._params.append(coeffs)
            if len(self._params)>self._num_frames:
                del self._params[0]
                del self._params_keep[0]
            if len(self._params)<self._num_frames:
                self._params_keep.append([1, 1])
            else:
                threshold = 0.1
                confidence = [1,1]
                for n in range(2):
                    if abs(coeffs[n,0]/self._weighted_params[n,0]-1)>threshold or abs(coeffs[n,1]/self._weighted_params[n,1]-1)>threshold or abs(coeffs[n,2]/self._weighted_params[n,2]-1)>threshold:
                        confidence[n] = 0
                self._params_keep.append(confidence)
        numpy_params = np.array(self._params)

        weighted_params = np.zeros_like(numpy_params[0],dtype=float)
        weigh_factor = 0
        for i in range(len(numpy_params)):
            weighted_params += numpy_params[i]*(i+1)
            weigh_factor += (i+1)
        weighted_params /= weigh_factor
        self._weighted_params = weighted_params
        averaged_lane_coeffs = np.average(weighted_params, axis=0)

        A = ( averaged_lane_coeffs[0] * self._y_px_per_m**2 / self._x_px_per_m )
        B = ( averaged_lane_coeffs[1] * self._y_px_per_m / self._x_px_per_m )
        r_curve = (1+(2*A*719+B)**2)**1.5 / np.abs(2*A)

        loc_left = int(self._weighted_params[0, 0] * 719 * 719 + self._weighted_params[0, 1] * 719 + self._weighted_params[0, 2])
        loc_right = int(self._weighted_params[1, 0] * 719 * 719 + self._weighted_params[1, 1] * 719 + self._weighted_params[1, 2])
        road_center_in_px = (loc_left+loc_right)/2
        dist_from_center_in_px = float(self._road_details[2,1])-road_center_in_px
        dist_from_center_in_m = dist_from_center_in_px/self._x_px_per_m

        return weighted_params, int(r_curve), dist_from_center_in_m



