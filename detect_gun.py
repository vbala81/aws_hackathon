from picamera import PiCamera
import cv2 as cv
import argparse
import boto3
import time
import os

def recognizeFace(client, image, collection):
    face_matched = False
    response = ''
    with open(image, 'rb') as file:
        response = client.detect_labels(Image={'Bytes': file.read()}, MaxLabels=10)
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()
    return response

def main():	

    #get args
    parser = argparse.ArgumentParser(description='Facial recognition')
    parser.add_argument('--camera', help='Camera device number.', type=int, default=0)
    args = parser.parse_args()

    #intialize opencv face detection
    face_cascade_name = args.face_cascade
    face_cascade = cv.CascadeClassifier()

    camera_device = args.camera

    #Read the video stream
    cam = cv.VideoCapture(camera_device)
    #setting the buffer size and frames per second, to reduce frames in buffer
    cam.set(cv.CAP_PROP_BUFFERSIZE, 1)
    cam.set(cv.CAP_PROP_FPS, 2);

    if not cam.isOpened:
        print('--(!)Error opening video capture')
        exit(0)

    #initialize reckognition sdk
    client = boto3.client('rekognition')

    while True:
        frame = {}
        #calling read() twice as a workaround to clear the buffer.
        cam.read()
        cam.read()
        ret, frame = cam.read()		
        if frame is None:
            print('--(!) No captured frame -- Break!')
            break
            response = recognizeFace(client, image , args.collection)

        if cv.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cam.release()
    cv.destroyAllWindows()

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()

