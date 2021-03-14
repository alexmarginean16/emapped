import io
import os
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "emapped-8b4be6305e9a.json"

client = vision.ImageAnnotatorClient()
file_name = os.path.abspath('IMG_5385.jpg')

with io.open(file_name, 'rb') as image_file:
    content = image_file.read()



image = vision.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

tags = []
for label in labels:
    tags.append(str(label.description))

print(tags)

# Performs face detection on the image file
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

print(moods)

