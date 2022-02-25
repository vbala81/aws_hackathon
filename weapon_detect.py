from picamera import PiCamera
import cv2 as cv
import argparse
import boto3
import time
import os
import sys
import json

def recognizeFace(client, image):
    face_matched = False
    response = ''
    with open(image, 'rb') as file:
        response = client.detect_labels(Image={'Bytes': file.read()}, MaxLabels=10, MinConfidence=40)
    labels = response['Labels']
    for label in labels:
        label_name = label['Name']
        print("Detected Object -->  " + label_name)
        if (label_name.endswith('Gun')):
            print ('Alert ------>>>>>> Weapon Detected')
            message = 'Alert! Your School camera has detected a weapon.'
            # sns_client = boto3.client('sns')
            # response = sns_client.publish(
            #     TargetArn='arn:aws:sns:us-east-1:680445953140:hackathon-gun-detection-stack-AlertSNSTopic-MOK0S0RXFCHD',
            #     Message=json.dumps(message)
            # )            
            s3_client = boto3.client('s3')
            S3_KEY = 'detected_images/'
            with open(image, 'rb') as data:
                upload_status = s3_client.upload_fileobj(data, 'aabg-hackathon-q2-2022-gun-detection', S3_KEY + image)
            lambda_client = boto3.client('lambda')
            alert_response = lambda_client.invoke(FunctionName='hackathon-gun-detection-stack-GunAlertFunction-6hCq0xhamGy1',
                                                  Payload = bytes(json.dumps({'FileName': S3_KEY + image}), encoding='utf8'))
            print (alert_response)
    os.remove(image)
    return response

def storeImage(frame):	
    timestr = time.strftime("%Y%m%d-%H%M%S")
    image = '{0}/image_{1}.png'.format(directory, timestr)
    cv.imwrite(image,frame)
    # print ('Your image was saved to %s' %image)
    return image

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
        image = storeImage(frame)
        if image is not None:
            response = recognizeFace(client, image)

        if cv.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cam.release()
    cv.destroyAllWindows()

dirname = os.path.dirname(__file__)
directory = os.path.join(dirname, 'faces')
main()
