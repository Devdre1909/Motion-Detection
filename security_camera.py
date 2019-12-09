import numpy as numpy
import cv2
import time
from datetime import datetime
import pandas

'''
This function is called when you want to record from your camera.
Note that the video is saved when you record so you can go back to it for future references
'''
def recordAndSave(fileName, speed, fileRecords, capturedVideo):
    codec = cv2.VideoWriter_fourcc('M','J','P','G')
    windowWidth = int(capturedVideo.get(3))
    windowHeight = int(capturedVideo.get(4))
    windowSize = (windowWidth, windowHeight)
    savedVideo = cv2.VideoWriter(fileName, codec, speed, windowSize) #Saves the video file to your directory

    '''
    The following variables handle our motion and time recording
    recorded is used to keep a list of the recorded motion time
    recordedTime is used to set the dataframe which inserts the recorded time from the list into an excel sheet
    staticObjext refers to the the time there is no motion
    objectInMotion refers to the time when motion is detected
    '''
    recorded = [] 
    recordedTime = pandas.DataFrame(columns = ['Start Time, End Time'])
    staticObject = None
    objectInMotion = [None, None]


    if capturedVideo.isOpened() == False: #This code checks to see that your camera is opened successfully or unsuccessfully
        print('Oops... It seems there was an error connecting to your camera or there was an errror finding the file you selected!! Please check that your camera is turned on or allow this program to use your camera ')

    while capturedVideo.isOpened() == True:
        ret, frame = capturedVideo.read()

        if ret == True: #This handles writing frame for video and also remembering to save the video
            savedVideo.write(frame) #displays the  video recording in the created frame

    
        font =  cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(frame,str(datetime.now()),(10,30), font, 1,(255,255,255),2,cv2.LINE_AA) #This code adds the current TimeStamp to the video

        '''
        The following lines of code handle the motion detection properly
        First, the image is converted to grayscale, then it static mode is equated to its grayscale so a difference can be detected
        Next, the frames are compared to see if there are any changes, if there are, motion is detected and recorded in the recorded list
        A threshhold frame is used to set limits fr what the camera counts as motion so that tiny things like sound isn't counted as motion since sound is a vibration of air particles
        contours or change in area are then detected in the threshold frame and finally counted as detected motion and are appended in the objectInMotion list
        '''
        grayScale = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (25, 25), 0)

        if staticObject is None:
            staticObject = grayScale
            continue

        compareFrames = cv2.absdiff(staticObject, grayScale)

        thresholdFrame = cv2.dilate(cv2.threshold(compareFrames, 100, 200, cv2.THRESH_BINARY)[1], None, iterations = 2)

        contours, crest = cv2.findContours(thresholdFrame.copy(),
             cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        detectedMotion = 0
        for contour in contours:
            if cv2.contourArea(contour) < 7000:
                continue
            detectedMotion = detectedMotion + 1
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        objectInMotion.append(detectedMotion)  
        objectInMotion = objectInMotion[-2:]

        if objectInMotion[-1] == 1 and objectInMotion[-2] == 0:
            recorded.append(datetime.now())

        if objectInMotion[-1] == 0 and objectInMotion[-2] == 1:
            recorded.append(datetime.now())

        cv2.imshow('Video is recording..... Press esc key to stop recording', frame)


        #When the esc key is pressed, the program stops running and it appends recorded motion timeframe to the recorded time list
        if cv2.waitKey(1) == 27:
            if detectedMotion == 1:
                recorded.append(datetime.now())
            break

        '''
        Finally, the excel sheet is created and the motion times are appended
        '''
    for i in range(0, len(recorded), 2):
        recordedTime = recordedTime.append({'Start Time':recorded[i], 'End Time':recorded[i+1]}, ignore_index = True)

    recordedTime.to_csv(fileRecords)

    return recordedTime.to_csv(fileRecords), capturedVideo

'''
This function is called when you want to upload an already existing and check for motion in it.
Note that the video is not saved when you record. This function works like the previous function except that it doesn't contain the commands that write the recorded video into a frame and save that frame.
'''
def upload(fileName, fileRecords):
    capturedVideo = cv2.VideoCapture(fileName)
    recorded = []
    recordedTime = pandas.DataFrame(columns = ['Start Time, End Time'])
    staticObject = None
    objectInMotion = [None, None]


    if capturedVideo.isOpened() == False: 
        print('Oops... It seems there was an error connecting to your camera or there was an errror finding the file you selected!! Please check that your camera is turned on or allow this program to use your camera ')

    while capturedVideo.isOpened() == True:
        ret, frame = capturedVideo.read()

        font =  cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(frame,str(datetime.now()),(10,30), font, 1,(255,255,255),2,cv2.LINE_AA)

        grayScale = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (25, 25), 0)

        if staticObject is None:
            staticObject = grayScale
            continue

        compareFrames = cv2.absdiff(staticObject, grayScale)

        thresholdFrame = cv2.dilate(cv2.threshold(compareFrames, 100, 200, cv2.THRESH_BINARY)[1], None, iterations = 2)

        contours, crest = cv2.findContours(thresholdFrame.copy(),
             cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        detectedMotion = 0
        for contour in contours:
            if cv2.contourArea(contour) < 7000:
                continue
            detectedMotion = detectedMotion + 1
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        objectInMotion.append(detectedMotion)  
        objectInMotion = objectInMotion[-2:]

        if objectInMotion[-1] == 1 and objectInMotion[-2] == 0:
            recorded.append(datetime.now())

        if objectInMotion[-1] == 0 and objectInMotion[-2] == 1:
            recorded.append(datetime.now())

        cv2.imshow('Video is recording..... Press esc key to stop recording', frame)


        #Appends recorded motion timeframe to the recorded time list
        if cv2.waitKey(1) == 27:
            if detectedMotion == 1:
                recorded.append(datetime.now())
            break

        for i in range(0, len(recorded), 2):
            recordedTime = recordedTime.append({'Start Time':recorded[i], 'End Time':recorded[i+1]}, ignore_index = True)

    recordedTime.to_csv(fileRecords)

    return recordedTime.to_csv(fileRecords), capturedVideo


'''
This function gives the user the choice to create a custom name for the excel sheet 
It also gives the user the choice of either uploading a video or recording a new video to check for motion
It then calls the corresponding function to carryout the task
'''
def main():

    print('Do you want to Check a video for motion or Do you want to record a new video? ')
    video = input('Select 1 to record or select 2 to upload a video ')
    fileRecords = input('Choose a name for the file were you want to save the recorded Time Stamps ')

    if video == '1':
        fileName = input('Choose a name for your video file. Please remeber to include the .avi, .mov or .mp4 extensions ')
        speed = int(input('Choose a playback speed for your output video '))
        capturedVideo = cv2.VideoCapture(0)
        recordAndSave(fileName, speed, fileRecords, capturedVideo)


        
    elif video == '2':
        video = input('Select the video you want to upload... Remember to include the proper video format i.e .avi, .mov, .mp4 ')
        upload(video, fileRecords)

    else:
        print('Oops, I think you might have selected an invalid option')

    capturedVideo.release()
    cv2.destroyAllWindows()

main()

