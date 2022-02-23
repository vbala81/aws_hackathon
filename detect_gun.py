from picamera import PiCamera
import cv2 as cv
import argparse
import boto3
import time
import os
import sys

def recognizeFace(client, image):
    face_matched = False
    response = ''
    print ('in recognizeface')
    with open(image, 'rb') as file:
        response = client.detect_labels(Image={'Bytes': file.read()}, MaxLabels=10)
        print (response)
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

    camera_device = args.camera

    #Read the video stream
    cam = cv.VideoCapture(camera_device)
    #setting the buffer size and frames per second, to reduce frames in buffer
    cam.set(cv.CAP_PROP_BUFFERSIZE, 1)
    cam.set(cv.CAP_PROP_FPS, 2)
    # cam.set(cv.CAP_PROP_FRAME_WIDTH, width)
    # cam.set(cv.CAP_PROP_FRAME_HEIGHT, height)

    # # Visualization parameters
    # row_size = 20  # pixels
    # left_margin = 24  # pixels
    # text_color = (0, 0, 255)  # red
    # font_size = 1
    # font_thickness = 1
    # fps_avg_frame_count = 10

    # # Initialize the object detection model
    # options = ObjectDetectorOptions(
    #     num_threads=4,
    #     score_threshold=0.3,
    #     max_results=3,
    #     enable_edgetpu=False)
    # detector = ObjectDetector(model_path='efficientdet_lite0.tflite', options=options)


    if not cam.isOpened:
        print('--(!)Error opening video capture')
        exit(0)

    #initialize reckognition sdk
    client = boto3.client('rekognition')
    print (client)
    while True:
        frame = {}
        #calling read() twice as a workaround to clear the buffer.
        cam.read()
        cam.read()
        success, frame = cam.read()
        if not success:
            sys.exit(
                'ERROR: Unable to read from webcam. Please verify your webcam settings.'
            )        
        print (frame)
        if frame is not None:
            response = recognizeFace(client, frame)

        if cv.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cam.release()
    cv.destroyAllWindows()

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()
