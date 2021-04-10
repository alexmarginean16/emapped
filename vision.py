import io
import os
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "emapped-8fe0781bbd63.json"

def getImage(image_name):
	client = vision.ImageAnnotatorClient()
	file_name = os.path.abspath(image_name)

	with io.open(file_name, 'rb') as image_file:
	    content = image_file.read()

	image = vision.Image(content=content)
	return client, image

# Performs label detection on the image file
def getLables(client, image):
	response = client.label_detection(image=image)
	labels = response.label_annotations

	tags = []
	for label in labels:
	    tags.append(str(label.description))

	return tags


# Performs face detection on the image file
def getMoods(client, image):
	response = client.face_detection(image=image)
	faces = response.face_annotations

	likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')

	moods = []

	for face in faces:
		mood = []
		mood.append('Joy')
		mood.append(likelihood_name.index(likelihood_name[face.joy_likelihood]))
		moods.append(mood)

		mood = []
		mood.append('Sorrow')
		mood.append(likelihood_name.index(likelihood_name[face.sorrow_likelihood]))
		moods.append(mood)

		mood = []
		mood.append('Anger')
		mood.append(likelihood_name.index(likelihood_name[face.anger_likelihood]))
		moods.append(mood)

		mood = []
		mood.append('Surprise')
		mood.append(likelihood_name.index(likelihood_name[face.surprise_likelihood]))
		moods.append(mood)

	return moods

def getDominantColors(client, image):
	response = client.image_properties(image=image)
	colors = response.image_properties_annotation.dominant_colors.colors

	dominant_color = colors[0].color
	red = int(dominant_color.red)
	green = int(dominant_color.green)
	blue = int(dominant_color.blue)

	dominant_colors = []
	dominant_colors.append(red)
	dominant_colors.append(green)
	dominant_colors.append(blue)

	return dominant_colors

client, image = getImage('image.png')
lables = getLables(client, image)
moods = getMoods(client, image)
colors = getDominantColors(client, image);
print(colors)