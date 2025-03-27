import numpy as np
import cv2 as cv
import glob
import pickle
from os import getcwd
from os.path import join

PARAMETERS_FILENAME = "camera_params.pkl"
IMAGES_PATTERN = join(getcwd(), "tools/captures/*.jpg")

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob(IMAGES_PATTERN)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (7,4), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (9,6), corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(500)

cv.destroyAllWindows()
print("All patterns identified, carrying out callibration")

# calibrate
ret, camera_matrix, distortion_coefs, _, _ = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera calibrated")
print(f"RMS: {ret}")

# save the parameters
print(f"Saving parameters to {PARAMETERS_FILENAME}")
pickle.dump({
    "camera_matrix": camera_matrix,
    "distortion_coefs": distortion_coefs,
}, open(PARAMETERS_FILENAME, 'w'))

print("Done")