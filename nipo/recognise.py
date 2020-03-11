from nipo import get_configs
import face_recognition
import cv2

config = get_configs()

#Commented out because it brings a seemingly simple problem that we are currently unable to fix
faces_folder = config['Faces directory']


#TODO: Submit pull request in face_recognition module so that the comparison functions are not so sensitive about the input data type and type check to give useful warnings. Also just update docs to include the types of expected inputs e.g the functions compare_faces and face_encodings

class Face:
	#A class that carries functions which are the different things we can do once we have an image of a face
	def __init__(self,face_pixels):
		self.face_pixels = face_pixels
		self.studentid = None
		self.face_encoding = None

	def get_encoding(self):
		if self.face_encoding is None:
			self.face_encoding = face_recognition.face_encodings(self.face_pixels)[0]

		return self.face_encoding
		

	def isSameFaceAs(self, encoding, threshold  = 0.6):
		#Check the current face_pixels(which necessarily has a face), get the encoding for this face and check whether it matches any of the students we currently have. If it does, set student ID to that student's ID, otherwise, set studentID to "Unknown". Also, store the file frame being recognised into the folder of the student's name (including unknown) so that that image can be used later in training.

		#Note that encoding can be a list
		enc= []
		enc.append(self.get_encoding())

		match = face_recognition.compare_faces(enc, encoding)
		return match

	def encode(self):
		if self.face_encoding is None:
			self.face_encoding =  face_recognition.face_encodings(self. face_pixels)

	#TODO: Set functionallity in this class to compare 2 face objects. This should be done by comparing student ID if it exists or comparing encodings if at least 1 studentID is missing

class Frame:
	#This class Deals with a single frame. It does any preprocessing such as getting the locations of the face(s), keeping track of the number of faces inside it, resizing (it will retain a copy of pre-sized high res frame)

	def __init__(self,frame):
		self.frame = frame 		#Should be an rgb frame
		self.small_frame = self.compress_frame(self.frame)
		#Consider keeping only one of either face_locations or faces in the frame
		self.face_locations = []
		self.face = []
		self.total_faces = None

	def get_size(self):
		#A function that returns the size of self.frame. Not important at the moment
		pass

	def get_faces(self):
		'''Return a list of all face objects within this Frame.'''
		if self.total_faces is None:
			self.detect_faces()
		return self.face

	def detect_faces(self, compressed_frame = True):
		'''Check self.small_frame and detect human faces. Store all face locations in self.face_locations. This function is meant to be used internally by the object'''
		faces_found = -1
		if compressed_frame == True:
			frame = self.small_frame
		else:
			frame = self.frame

		self.face_locations = face_recognition.face_locations(frame)
		if len(self.face_locations) > 0:
			faces_found = len(self.face_locations)
			for location in self.face_locations:
				left, bottom, right, top= location
				print('top: {}\tleft: {}\t bottom: {}\tright {}'.format(top,left,bottom, right))
				face_pixels = frame[top:bottom, left:right]
				self.face.append(Face(face_pixels))

		self.total_faces = faces_found
		return faces_found



	def compress_frame(self, frame):
		#Resize the frame of video to 1/4 size for faster processing later
		smaller_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		return smaller_frame

class Stream:
	'''A class for checking a stream of video (A few successive frames) and reporting whether the stream is blurred or not. We intend to make the first version simply an implementation of https://github.com/AntiAegis/Face-Attendance-System'''

	pass


