import pytest
from nipo import recognise
from face_recognition import load_image_file


TEST_IMG = recognise.faces_folder
TEST_IMG += '/test/0.jpg'
TEST_IMG = load_image_file(TEST_IMG)

@pytest.fixture
def test_frame():
	return recognise.Frame(TEST_IMG)

@pytest.fixture
def test_face():
	return recognise.Frame(TEST_IMG)

class TestFace:

	def test_encode(self):
		pass

	def test_isSameFaceAs(Self):
		pass

class TestFrame():

	def test_init(self,test_frame):
		'''Check that when passed a frame, the size of small frame in this frame is actually a quarter the size of the original frame. Also check types of the other variables'''
		pass

	def test_detect_faces(self):
		pass

	class TestStream:
		pass

