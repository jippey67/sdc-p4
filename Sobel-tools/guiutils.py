import cv2, numpy as np


class EdgeFinder:
    def __init__(self, image, filter_size=1, threshold1=0, threshold2=0):
        self.image = image
        self._filter_size = filter_size
        self._threshold1 = threshold1
        self._threshold2 = threshold2

        def onchangeThreshold1(pos):
            self._threshold1 = pos
            self._render()

        def onchangeThreshold2(pos):
            self._threshold2 = pos
            self._render()

        def onchangeFilterSize(pos):
            self._filter_size = pos
            self._filter_size += (self._filter_size + 1) % 2
            self._render()

        cv2.namedWindow('edges')

        cv2.createTrackbar('threshold1', 'edges', self._threshold1, 255, onchangeThreshold1)
        cv2.createTrackbar('threshold2', 'edges', self._threshold2, 255, onchangeThreshold2)
        cv2.createTrackbar('filter_size', 'edges', self._filter_size, 20, onchangeFilterSize)

        self._render()

        print ("Adjust the parameters as desired.  Hit any key to close.")

        cv2.waitKey(0)

        cv2.destroyWindow('edges')
        cv2.destroyWindow('smoothed')

    def threshold1(self):
        return self._threshold1

    def threshold2(self):
        return self._threshold2

    def filterSize(self):
        return self._filter_size

    def edgeImage(self):
        return self._edge_img

    def smoothedImage(self):
        return self._smoothed_img

    def _render(self):
        self._smoothed_img = cv2.GaussianBlur(self.image, (self._filter_size, self._filter_size), sigmaX=0, sigmaY=0)
        self._edge_img = cv2.Canny(self._smoothed_img, self._threshold1, self._threshold2)
        cv2.imshow('smoothed', self._smoothed_img)
        cv2.imshow('edges', self._edge_img)

class Sobel:
    def __init__(self, image, filter_size=1, threshold1=0, threshold2=0, colorspace=0, layer=0, method=0):
        self.image = image
        self._filter_size = filter_size
        self._threshold1 = threshold1
        self._threshold2 = threshold2
        self._colorspace = colorspace
        self._layer = layer
        self._method = method

        self._colorspaces = ['BGR','YUV','HLS','HSV','gray']
        self._layers = 3
        self._methods = ['Sobel_grad_x','Sobel_grad_y','Sobel_mag_dir','Sobel_grad_dir']

        def onchangeThreshold1(pos):
            self._threshold1 = pos
            self._render()

        def onchangeThreshold2(pos):
            self._threshold2 = pos
            self._render()

        def onchangeFilterSize(pos):
            self._filter_size = pos*2+1
            self._render()

        def onchangeColorspace(pos):
            self._colorspace = pos
            self._render()

        def onchangeLayer(pos):
            self._layer = pos
            self._render()

        def onchangeMethod(pos):
            self._method = pos
            self._render()

        cv2.namedWindow('edges')

        cv2.createTrackbar('method', 'edges', self._method, len(self._methods) - 1, onchangeMethod)
        cv2.createTrackbar('colorspace', 'edges', self._colorspace, len(self._colorspaces) - 1, onchangeColorspace)
        cv2.createTrackbar('layer', 'edges', self._layer, (self._layers - 1), onchangeLayer)
        cv2.createTrackbar('filter_size', 'edges', self._filter_size, 15, onchangeFilterSize)
        cv2.createTrackbar('threshold1', 'edges', self._threshold1, 255, onchangeThreshold1)
        cv2.createTrackbar('threshold2', 'edges', self._threshold2, 255, onchangeThreshold2)

        self._render()

        print ("Adjust the parameters as desired.  Hit any key to close.")

        cv2.waitKey(0)

        cv2.destroyWindow('edges')


    def threshold1(self):
        return self._threshold1

    def threshold2(self):
        return self._threshold2

    def filterSize(self):
        return self._filter_size

    def method(self):
        return self._methods[self._method]

    def colorspace(self):
        return self._colorspaces[self._colorspace]

    def layer(self):
        return self._colorspaces[self._colorspace][self._layer]

    def edgeImage(self):
        return self._edge_img

    def _render(self):
        if self._colorspace == 0:
            img = self.image
            img = img[:, :, self._layer]
        elif self._colorspace == 1:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2YUV)
            img = img[:, :, self._layer]
        elif  self._colorspace == 2:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HLS)
            img = img[:, :, self._layer]
        elif self._colorspace == 3:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            img = img[:, :, self._layer]
        else:
            img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self._layer = 0

        if self._method == 0:
            sobel_img = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=self._filter_size)
            abs_sobel = np.absolute(sobel_img)
            scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
            sobel_binary = np.zeros_like(scaled_sobel)
            sobel_binary[(scaled_sobel >= self._threshold1) & (scaled_sobel <= self._threshold2)] = 255
        elif self._method == 1:
            sobel_img = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=self._filter_size)
            abs_sobel = np.absolute(sobel_img)
            scaled_sobel = np.uint8(255 * abs_sobel / np.max(abs_sobel))
            sobel_binary = np.zeros_like(scaled_sobel)
            sobel_binary[(scaled_sobel >= self._threshold1) & (scaled_sobel <= self._threshold2)] = 255
        elif self._method == 2:
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=self._filter_size)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=self._filter_size)
            # Calculate the gradient magnitude
            gradmag = np.sqrt(sobelx ** 2 + sobely ** 2)
            # Rescale to 8 bit
            gradmag = np.uint8(255 * gradmag / np.max(gradmag))
            # Create a binary image of ones where threshold is met, zeros otherwise
            sobel_binary = np.zeros_like(gradmag)
            sobel_binary    [(gradmag >= self._threshold1) & (gradmag <= self._threshold2)] = 255
        else:
            sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=self._filter_size)
            sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=self._filter_size)
            with np.errstate(divide='ignore', invalid='ignore'):
                abs_graddir = np.absolute(np.arctan(sobely / sobelx))
                #print(scaled_sobel)
            sobel_binary = np.zeros_like(abs_graddir)
            sobel_binary[(abs_graddir >= (np.pi/510)*self._threshold1) & (abs_graddir <= (np.pi/510)*self._threshold2)] = 255



        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(sobel_binary, 'Method = '+self._methods[self._method], (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(sobel_binary, 'Colorspace = '+self._colorspaces[self._colorspace], (10, 60), font, 1, (255, 255, 255), 2)
        cv2.putText(sobel_binary, 'Layer = '+self._colorspaces[self._colorspace][self._layer], (10, 90), font, 1, (255, 255, 255), 2)
        cv2.putText(sobel_binary, 'kernel size: '+str(self._filter_size), (10, 120), font, 1, (255, 255, 255), 2)
        if self._method == 3:
            cv2.putText(sobel_binary, 'threshold1: ' + str(int(90/255*self._threshold1)) + ' deg', (10, 150), font, 1, (255, 255, 255), 2)
            cv2.putText(sobel_binary, 'threshold2: ' + str(int(90/255*self._threshold2)) + ' deg', (10, 180), font, 1, (255, 255, 255), 2)
        else:
            cv2.putText(sobel_binary, 'threshold1: '+str(self._threshold1), (10, 150), font, 1, (255, 255, 255), 2)
            cv2.putText(sobel_binary, 'threshold2: '+str(self._threshold2), (10, 180), font, 1, (255, 255, 255), 2)

        self._edge_img = sobel_binary

        cv2.imshow('edges', self._edge_img)
        cv2.moveWindow('edges', 1280, 0)
        cv2.imshow('layer', img)
        cv2.moveWindow('layer', 0, -200)
        cv2.imshow('RGB', self.image)
        cv2.moveWindow('RGB', 0, 700)


class HSV:
    def __init__(self, image, threshold1=0, threshold2=255, layer=0):
        self.image = img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        self._threshold1 = threshold1
        self._threshold2 = threshold2
        self._layer = layer

        def onchangeThreshold1(pos):
            self._threshold1 = pos
            self._render()

        def onchangeThreshold2(pos):
            self._threshold2 = pos
            self._render()

        def onchangeLayer(pos):
            self._layer = pos
            self._render()

        cv2.namedWindow('pixels')
        cv2.createTrackbar('layer', 'pixels', self._layer, 2, onchangeLayer)
        cv2.createTrackbar('threshold1', 'pixels', self._threshold1, 255, onchangeThreshold1)
        cv2.createTrackbar('threshold2', 'pixels', self._threshold2, 255, onchangeThreshold2)

        self._render()

        print ("Adjust the parameters as desired.  Hit any key to close.")

        cv2.waitKey(0)

        cv2.destroyWindow('pixels')
        cv2.destroyWindow('RGB')


    def threshold1(self):
        return self._threshold1

    def threshold2(self):
        return self._threshold2

    def layer(self):
        return self._layer

    def _render(self):
        image = self.image[:,:,self._layer]
        pix_img = np.zeros_like(image)
        pix_img [(image>=self._threshold1)&(image<=self._threshold2)] = 255
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(pix_img, 'Layer = '+str(self._layer), (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(pix_img, 'threshold1: '+str(self._threshold1), (10, 60), font, 1, (255, 255, 255), 2)
        cv2.putText(pix_img, 'threshold2: '+str(self._threshold2), (10, 90), font, 1, (255, 255, 255), 2)
        cv2.imshow('pixels', pix_img)
        cv2.moveWindow('pixels', 1280, 0)
        cv2.imshow('RGB', cv2.cvtColor(self.image, cv2.COLOR_HSV2BGR))

class HLS:
    def __init__(self, image, threshold1=0, threshold2=255, layer=0):
        self.image = img = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
        self._threshold1 = threshold1
        self._threshold2 = threshold2
        self._layer = layer

        def onchangeThreshold1(pos):
            self._threshold1 = pos
            self._render()

        def onchangeThreshold2(pos):
            self._threshold2 = pos
            self._render()

        def onchangeLayer(pos):
            self._layer = pos
            self._render()

        cv2.namedWindow('pixels')
        cv2.createTrackbar('layer', 'pixels', self._layer, 2, onchangeLayer)
        cv2.createTrackbar('threshold1', 'pixels', self._threshold1, 255, onchangeThreshold1)
        cv2.createTrackbar('threshold2', 'pixels', self._threshold2, 255, onchangeThreshold2)

        self._render()

        print ("Adjust the parameters as desired.  Hit any key to close.")

        cv2.waitKey(0)

        cv2.destroyWindow('pixels')
        cv2.destroyWindow('RGB')


    def threshold1(self):
        return self._threshold1

    def threshold2(self):
        return self._threshold2

    def layer(self):
        return self._layer

    def _render(self):
        image = self.image[:,:,self._layer]
        pix_img = np.zeros_like(image)
        pix_img [(image>=self._threshold1)&(image<=self._threshold2)] = 255
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(pix_img, 'Layer = '+str(self._layer), (10, 30), font, 1, (255, 255, 255), 2)
        cv2.putText(pix_img, 'threshold1: '+str(self._threshold1), (10, 60), font, 1, (255, 255, 255), 2)
        cv2.putText(pix_img, 'threshold2: '+str(self._threshold2), (10, 90), font, 1, (255, 255, 255), 2)
        cv2.imshow('pixels', pix_img)
        cv2.moveWindow('pixels', 1280, 0)
        cv2.imshow('RGB', cv2.cvtColor(self.image, cv2.COLOR_HSV2BGR))

