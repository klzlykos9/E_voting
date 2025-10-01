# USAGE
# python encode.py --dataset dataset --encodings encodings.pickle

# import the necessary packages
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
from regex import R

from sympy import EX
from django.conf import settings

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--dataset", required=False, default="../dataset/",
# 	help="path to input directory of faces + images")
# ap.add_argument("-e", "--encodings", required=False, default="encodings.pickle",
# 	help="path to serialized db of facial encodings")
# ap.add_argument("-d", "--detection-method", type=str, default="hog",
# 	help="face detection model to use: either `hog` or `cnn`")
# args = vars(ap.parse_args())
import os
def encode():
	# grab the paths to the input images in our dataset
	print("[INFO] quantifying faces...")
	user_face_folder = os.path.join(settings.BASE_DIR, 'user_faces')
	print(user_face_folder)

	imagePaths = list(paths.list_images(user_face_folder))

	# initialize the list of known encodings and known names
	knownEncodings = []
	knownNames = []

	# loop over the image paths
	for (i, imagePath) in enumerate(imagePaths):
		# extract the person name from the image path
		print("[INFO] processing image {}/{} - {}".format(i + 1,
			len(imagePaths),
			imagePath))

		try:
			name = os.path.basename(os.path.dirname(imagePath))

			# load the input image and convert it from RGB (OpenCV ordering)
			# to dlib ordering (RGB)
			image = cv2.imread(imagePath)
			rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

			# detect the (x, y)-coordinates of the bounding boxes
			# corresponding to each face in the input image
			boxes = face_recognition.face_locations(rgb,
				model='hog')

			# compute the facial embedding for the face
			encodings = face_recognition.face_encodings(rgb, boxes)

			# loop over the encodings
			for encoding in encodings:
				# add each encoding + name to our set of known names and
				# encodings
				knownEncodings.append(encoding)
				knownNames.append(name)
		except Exception as e:
			print("Error Occur "+str(e))

	# dump the facial encodings + names to disk
	print("[INFO] serializing encodings...")
	data = {"encodings": knownEncodings, "names": knownNames}
	user_face_folder = os.path.join(settings.BASE_DIR, 'model')
	f = open(user_face_folder+'/encodings.pickle', "wb")
	f.write(pickle.dumps(data))
	f.close()
