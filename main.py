import os

import cvzone
import cv2
from cvzone.PoseModule import PoseDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set the width of the capture to 1280 pixels
cap.set(4, 720)   # Set the height of the capture to 720 pixels


detector = PoseDetector()

shirtFolderPath = "Resources/Shirts"
listShirts = os.listdir(shirtFolderPath)
# print(listShirts)
fixedRatio = 262 / 190  # widthOfShirt/widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440
imageNumber = 0
imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_UNCHANGED)
imgButtonLeft = cv2.flip(imgButtonRight, 1)
counterRight = 0
counterLeft = 0
selectionSpeed = 20

while True:
    success, img = cap.read() #reads a frame from the webcam
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList: # for calculating the dimensions of the shirt that will be overlaid on the person
        lm11 = lmList[11][1:3]
        lm12 = lmList[12][1:3]
        imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[imageNumber]), cv2.IMREAD_UNCHANGED)

        widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)

        L_cm = (widthOfShirt * 2.54) / 0.0875
        imgShirtWidth = widthOfShirt
        imgShirtHeight = int(imgShirtWidth * shirtRatioHeightWidth)

        # Determine t-shirt size
        if imgShirtWidth <= 250 and imgShirtHeight <= 325:
            shirtSize = "small"
        elif 251 <= imgShirtWidth <= 275 and 326 <= imgShirtHeight <= 350:
            shirtSize = "medium"
        elif imgShirtWidth > 276 and imgShirtHeight > 350:
            shirtSize = "large"
        else:
            shirtSize = "unknown"

        print(f"T-shirt size: {shirtSize}")

        # Calculate shirt size based on width
        ''' if L_cm < 38:
            shirtSize = "S"
        elif L_cm < 41:
            shirtSize = "M"
        else:
            shirtSize = "L" '''

        imgShirtWidth = int(widthOfShirt)
        imgShirtHeight = int(widthOfShirt * shirtRatioHeightWidth)
        print("width : ",imgShirtWidth)
        print("height : ", imgShirtHeight)


        if imgShirtWidth > 0 and imgShirtHeight > 0:
            #if imgShirt is not None:
            imgShirt = cv2.resize(imgShirt, (imgShirtWidth, imgShirtHeight))
            currentScale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * currentScale), int(48 * currentScale)

            try:
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except:
                pass

            img = cvzone.overlayPNG(img, imgButtonRight, (1074, 293))
            img = cvzone.overlayPNG(img, imgButtonLeft, (72, 293))
            '''
            # Display shirt size overlay on image
            cv2.putText(img,"Size : "+shirtSize, (int(lm12[0] - offset[0]), int(lm12[1] - offset[1]) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                        '''
            text = f"Size: {shirtSize}"
            text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, thickness=3)

            # Calculate the position for the text overlay
            text_x = int((img.shape[1] - text_size[0]) / 2)  # Centered horizontally
            text_y = img.shape[0] - 20  # Positioned at the bottom with a margin of 20 pixels

            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)


            #else:
              #  print("Failed to load the image.")

        if lmList[16][1] < 300:
            counterRight += 1
            cv2.ellipse(img, (139, 360), (66, 66), 0, 0,
                        counterRight * selectionSpeed, (0, 255, 0), 20)
            if counterRight * selectionSpeed > 360:
                counterRight = 0
                if imageNumber < 2:
                    print('true')
                    imageNumber += 1
                    
        elif lmList[15][1] > 900:
            counterLeft += 1
            cv2.ellipse(img, (1138, 360), (66, 66), 0, 0,
                        counterLeft * selectionSpeed, (0, 255, 0), 20)
            if counterLeft * selectionSpeed > 360:
                counterLeft = 0
                if imageNumber > 0:
                    imageNumber -= 1

        else:
            counterRight = 0
            counterLeft = 0

    cv2.imshow("Image", img)
    cv2.waitKey(1)