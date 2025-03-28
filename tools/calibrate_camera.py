import numpy as np
import cv2 as cv
import glob
import pickle

PARAMETERS_FILENAME = "camera_params.pkl"
IMAGES_PATTERN = "captures/*.jpg"

PATTERN_H = 5
PATTERN_W = 8

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((PATTERN_H*PATTERN_W,3), np.float32)
objp[:,:2] = np.mgrid[0:PATTERN_W, 0:PATTERN_H].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob(IMAGES_PATTERN)

for fname in images:
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (PATTERN_W,PATTERN_H), None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, (PATTERN_W,PATTERN_H), corners2, ret)

    cv.imshow('img', img)
    cv.waitKey(0)

cv.destroyAllWindows()
print("All patterns identified, carrying out callibration")

# calibrate
ret, camera_matrix, distortion_coefs, _, _ = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print("Camera calibrated")
print(f"RMS: {ret}")
print("Camera matrix:")
print(camera_matrix)
print("Distortion coefs:")
print(distortion_coefs)

# save the parameters
print(f"Saving parameters to {PARAMETERS_FILENAME}")
pickle.dump({
    "camera_matrix": camera_matrix,
    "distortion_coefs": distortion_coefs,
}, open(PARAMETERS_FILENAME, 'bw'))

print("Done")