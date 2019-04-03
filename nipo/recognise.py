from nipo import get_configs
import face_recognition
import cv2

config = get_configs

faces_folder = 	config['faces directory']

class Face:
	#A class that carries functions which are the different things we can do once we have an image of a face
	def __init__(self,frame=None):
		self.frame=frame
		self.studentid=None
		pass

	def recognise(self):
		#Check the current frame(which necessarily has a face), get the encoding for this face and check whether it matches any of the students we currently have. If it does, set student ID to that student's ID, otherwise, set studentID to "Unknown". Also, store the file frame being recognised into the folder of the student's name (including unknown) so that that image can be used later in training.

	def encode(self):
		#Go go to faces_folder,  

	def set_frame(self,frame):
		self.frame = frame
		#Do something here to change the student id so that even if the new frame is someone else, the old student ID doesnt remain in the instance


class Frame:
	#This class Deals with a single frame. It does any preprocessing such as getting the locations of the face(s), keeping track of the number of faces inside it, resizing (it will retain a copy of pre-sized high res frame)

	def __init__(self,frame):
		self.frame = frame
		self.small_frame = self.compress(self.frame)
		self.face_locations = []

	def get_size(self):
		#A function that returns the size of self.frame. Not important at the moment
		pass

	def detect_faces(self,frame=self.small_frame):
		#Check self.small_frame and detect human faces. Store all face locations in self.face_locations

	def compress_frame(self, frame):
		#Resize the frame of video to 1/4 size for faster processing later
		smaller_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		return small_frame





class Stream:
	#A class for checking a stream of video (A few successive frames and reporting whether) the stream is blurred or not. I intend to make the first version simply an implementation of https://github.com/AntiAegis/Face-Attendance-System

	pass