import cv2
from os.path import join

SAVE_FOLDER = "captures"
FLIP = False

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

capture_count = 0
while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()

    if FLIP:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
    elif key > 0: # capture on space
        save_path = join(SAVE_FOLDER, f"{capture_count}.jpg")
        print(save_path)
        cv2.imwrite(save_path, frame)
        capture_count += 1

cv2.destroyWindow("preview")
vc.release()