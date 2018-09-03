'''

# /r/rateme
# scraper to view all submissions and scrape ONE image only - preferrably directly off page - then use face detection to only use submissions with exactly one face detected (plenty of data)
# in scraper, scrape all ratings (in a form like "n/10") and take the average (of course disregard scrapes with no number ratings) - could even do text sentiment analysis? (later)

https://github.com/dmarx/psaw

'''

from psaw import PushshiftAPI
api = PushshiftAPI()
import re

# pull submissions

submissions = list(api.search_submissions(subreddit='rateme',filter=['url','id', 'title']))
submissions = [v[1:4] for v in submissions]

age = []
sex = []

p = re.compile("[0-9]+\/? ?[MmFf]|[MmFf]\/? ?[0-9]+")

# make an age and sex array - this information may be interesting (get counts, averages etc)

for i in submissions:
    if len(p.findall(i[1])) > 0:
        # there is a regex match for something like 22M, so append the gender and age to those arrays
        # p.findall(i[1])[0]) is item at index 0 (ie. first match) for finding the complicated regex string above in the title (which is i[1]), and we're appending the first match of [0-9]+ and [MmFf] for those
        age.append(re.search("[0-9]+", p.findall(i[1])[0])[0])
        sex.append(re.search("[MmFf]", p.findall(i[1])[0])[0])
    else:
        age.append('NA')
        sex.append('NA')

# also add age and sex to each entry in the submissions list
        
count = 0
for i in submissions:
    submissions[count] = i + (age[count],sex[count],)
    count += 1

# get rid of submissions that don't link direct to imgur or i.redd.it
        
count = 0
submissionsDirect = []

for i in submissions:
    if ("i.redd.it" in i[2]) or ("imgur" in i[2]):
        submissionsDirect.append(i)
    count += 1

# get count of entries in submissions that link to a certain URL, eg. url = "i.redd.it" or url = "imgur"

def urlcount(url):
    count = 0
    for i in submissions:
        if url in i[2]:
            count += 1
    return count

# pull comments
    
comments = list(api.search_comments(subreddit='rateme', filter=['body', 'link_id']))
comments = [v[::2] for v in comments]
comments = [v[0:2] for v in comments]

'''
with open("sc6.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(sc6)
    
with open('comments.csv', 'r') as f:
    reader = csv.reader(f)
    comments = list(reader)
   
'''

p = re.compile("[0-9]\.?[0-9]+?\/10")

ratings = []

# Make a ratings array with the rating, link_id  and comment it pertains to. Also add the rating included in a comment to each comment in the comments list (if there's a rating)

count = 0
for i in comments:
    if len(p.findall(i[0])) > 0:
        rating = re.search("[0-9]\.?[0-9]?", p.findall(i[0])[0])[0]
        ratings.append([rating, i[1], i[0]])
        #comments[count] = i + (rating,)
    count += 1

# get rid of the t3_ in ratings[]

for i in ratings:
    i[1] = i[1][3:]

# check ratings and comments for a given link_id
# good example is returnRatings("9b31zo")

# returnRatings("95fcs0")
   
def returnRatings(link_id):   
    ratingsArray = []
    for i in ratings:
        if i[1] == link_id:
            print(i[0] + ' ~ ' + i[2])
            ratingsArray.append(i[0])
    if len(ratingsArray) > 0:
        ratingsArray = [float(i) for i in ratingsArray]
        print('average of ' + str(sum(ratingsArray)/len(ratingsArray)))
    else:
        print('no ratings yet')

# loop through all submissions (only those in submissionsDirect that are direct image links), check if the link_id at submissionsDirect[0] (which is i[0] here) matches each rating entry at j[1], make a ratings array for each submission, then get the average of ratings and add that to the submissionsDirect list under its relevant submission

# this takes some time, so best to save the submissionsDR list after it's done

submissionsDR = []

count = 0
totalAdditions = 0
for i in submissionsDirect:
    ratingsArray = []
    for j in ratings:
        if i[0] == j[1]:
            ratingsArray.append(j[0])
    if len(ratingsArray) > 0:
        ratingsArray = [float(i) for i in ratingsArray]
        average = sum(ratingsArray)/len(ratingsArray)
        #SubmissionsDR[totalAdditions] = i + (average,)
        #submissionsDR.append(i + (average,))
        submissionsDR.append([i[0], i[1], i[2], i[3], i[4], average])
        totalAdditions += 1
        print('rating added: ' + str(count) + ' ~ ' + str(totalAdditions))
    count += 1

#print('rating added to submissionsDR for submission from submissionsDirect at index ' + str(count) + ' ~ ' + str(totalAdditions))
    
# to download images

import urllib.request, urllib.error
#urllib.request.urlretrieve("https://i.redd.it/0u4qa4luh3j11.jpg", "1.jpg")

# get gallery ID for images posted to imgur - should be 7 characters at end of URL
# can also make another submissions array containing only submissions with a valid link

submissionsClean = []



import time

#count = 21419
#index = 26599
count = 0
index = 0
for i in submissionsDR[index:len(submissionsDR)]:
    if index % 100 == 0:
        #sleep for a bit
        print('taking a nap...')
        time.sleep(5)
    url = i[2]
    #print(str(index) + ': ' + str(i) + ' starting...')
    if (".jpg" in url) or (".jpeg" in url) or (".png" in url) or (".gif" in url):
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print(str(index) + ': HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print(str(index) + ': URLError: {}'.format(e.reason))
        else:
            fullfilename = os.path.join('Pictures/', str(count) + '.jpg')
            urllib.request.urlretrieve(url, fullfilename)
            #print('downloaded image ' + str(url))
            print(str(index) + ': Successful')
            submissionsClean.append(i)
            count += 1
    else:
        # imgur album
        time.sleep(0.1)
        galleryID = url[-7:]
        #print('quering gallery ID ' + str(galleryID) + '...')
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print('HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print('URLError: {}'.format(e.reason))
        else:
            fp = urllib.request.urlopen(url)
            mybytes = fp.read()
            try:
                mystr = mybytes.decode("utf8")
                fp.close()
                indexStart = mystr.find("<link rel=\"image_src\"            href=\"")
                if indexStart > 0:
                    image = mystr[indexStart + 39:indexStart + 39 + 31]
                    if image[len(image) - 1:] != ' ':
                        #print('downloading gallery image ' + str(image) + '...')
                        fullfilename = os.path.join('Pictures/', str(count) + '.jpg')
                        urllib.request.urlretrieve(image, fullfilename)
                        print(str(index) + ': Successful')
                        submissionsClean.append(i)
                        count += 1
                    else:
                        print(str(index) + ': Gallery was loaded, but no images inside')
                else:
                    print(str(index) + ': No images in this gallery')
            except:
                print(str(index) + ': Bytes decode issue - issue with loading webpage')
    index += 1

'''
for i in submissionsClean[10005:10006]:
    if index % 100 == 0:
        #sleep for a bit
        print('taking a nap...')
        time.sleep(5)
    url = i[2]
    #print(str(index) + ': ' + str(i) + ' starting...')
    if (".jpg" in url) or (".jpeg" in url) or (".png" in url) or (".gif" in url):
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print(str(index) + ': HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print(str(index) + ': URLError: {}'.format(e.reason))
        else:
            fullfilename = os.path.join('Pictures/', str(10005) + '.jpg')
            urllib.request.urlretrieve(url, fullfilename)
            #print('downloaded image ' + str(url))
            print(str(index) + ': Successful')
            #submissionsClean.append(i)
            count += 1
    else:
        # imgur album
        time.sleep(0.1)
        galleryID = url[-7:]
        #print('quering gallery ID ' + str(galleryID) + '...')
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print('HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print('URLError: {}'.format(e.reason))
        else:
            fp = urllib.request.urlopen(url)
            mybytes = fp.read()
            try:
                mystr = mybytes.decode("utf8")
                fp.close()
                indexStart = mystr.find("<link rel=\"image_src\"            href=\"")
                if indexStart > 0:
                    image = mystr[indexStart + 39:indexStart + 39 + 31]
                    if image[len(image) - 1:] != ' ':
                        #print('downloading gallery image ' + str(image) + '...')
                        fullfilename = os.path.join('Pictures/', str(10005) + '.jpg')
                        urllib.request.urlretrieve(image, fullfilename)
                        print(str(index) + ': Successful')
                        #submissionsClean.append(i)
                        count += 1
                    else:
                        print(str(index) + ': Gallery was loaded, but no images inside')
                else:
                    print(str(index) + ': No images in this gallery')
            except:
                print(str(index) + ': Bytes decode issue - issue with loading webpage')
    index += 1
'''
    
    
    
sc1 = []
sc2 = []
sc3 = []
sc4 = []
sc5 = []
sc6 = []
    
for i in submissionsClean:
    sc1.append(i[0])
    sc2.append(i[1])
    sc3.append(i[2])
    sc4.append(i[3])
    sc5.append(i[4])
    sc6.append(i[5])
    
    
'''
0
1
10
100
1000
10001
10002
10003
10004
10005
'''
    
# find faces in images

from PIL import Image
import face_recognition
import os
import glob

facesOnly = []
picturesPath = os.path.expanduser('~/Pictures')
files = glob.glob(picturesPath + '/*.jpg')
count = 0
for myFile in sorted(files):
    if count < 5:
        fileName = myFile[26:]
        index = int(fileName[0:len(fileName) -4])
        #print(index)
        image = face_recognition.load_image_file(myFile)
        #face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
        face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0)
        if len(face_locations) == 1:
            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_image = image[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save('/home/paperspace/faces/' + fileName, 'JPEG')
                print('face saved for ' + fileName + ' ~ ' + str(count))
                facesOnly.append(submissionsClean[index])
        else:
            print(len(face_locations) + ' faces found for ' + fileName + ' - not saving' + ' ~ ' + str(count))
        count += 1

'''
        
# make an even cleaner submissions list by only including those with an age and sex
                
sc = []

for i in submissionsClean:
    if i[3] != 'NA':
        sc.append(i)
        
# pure ratings

pr = []

for i in submissionsClean:
    pr.append(i[5])
    
'''
    
# start analysis
# run a face detection script and save only THOSE images - won't work if images are all different aspect ratios - face detection script will make square images containing just the face

import cv2
import glob

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

count = 0
files = glob.glob ("images/*.jpg")
for myFile in files:
    print(myFile)
    image = cv2.imread(myFile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        )
    print("Found {0} faces!".format(len(faces)))
    for (x, y, w, h) in faces:
        #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        print('width of',w)
        print('height of',h)
        print('x location',x)
        print('y location',y)
    roi = image[y:y+h, x:x+w]
    cv2.imwrite(str(count) + '.jpg', roi)
    count += 1
        #
        #cv2.imshow("Faces found", image)
        #cv2.waitKey(1000)
        #cv2.destroyAllWindows()


import face_recognition
image = face_recognition.load_image_file("1.jpg")
face_locations = face_recognition.face_locations(image)




local_download_path = os.path.expanduser('images')

import glob
import cv2

images = []
files = glob.glob(local_download_path + '/*.jpg')
for myFile in sorted(files):
    image = cv2.imread(myFile)
    images.append(image)

height = []
width = []
for i in images:
    height.append(i.shape[0])
    width.append(i.shape[1])

avgHeight = round(sum(height)/len(height))
avgWidth = round(sum(width)/len(width))

count = 0
for i in images:
    images[count] = cv2.resize(i, (avgWidth, avgHeight))
    count += 1
    
from sklearn.model_selection import train_test_split
    
images_train, images_test, labels_train, labels_test = train_test_split(images, pr, test_size=0.2)

images_train = np.array(images_train)
labels_train = np.array(labels_train)
images_test = np.array(images_test)
labels_test = np.array(labels_test)











###

'''

3 different models: predict attractiveness, age and gender
gender: Binary classification sigmoid binary_crossentropy (pg 114)
age: Multiclass, single-label classification softmax categorical_crossentropy

Choosing the right last-layer activation and loss function for your model
Problem type Last-layer activation Loss function
Binary classification sigmoid binary_crossentropy
Multiclass, single-label classification softmax categorical_crossentropy
Multiclass, multilabel classification sigmoid binary_crossentropy
Regression to arbitrary values None mse
Regression to values between 0 and 1 sigmoid mse or binary_crossentropy


'''

# predicting gender pg 134, pg 145








from keras import layers
from keras import models
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator

model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu',
input_shape=(150, 150, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Flatten())
model.add(layers.Dropout(0.5))
model.add(layers.Dense(512, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy',
optimizer=optimizers.RMSprop(lr=1e-4),
metrics=['acc'])

train_datagen = ImageDataGenerator(
rescale=1./255,
rotation_range=40,
width_shift_range=0.2,
height_shift_range=0.2,
shear_range=0.2,
zoom_range=0.2,
horizontal_flip=True,)

test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
train_dir,
target_size=(150, 150),
batch_size=32,
class_mode='binary')

validation_generator = test_datagen.flow_from_directory(
validation_dir,
target_size=(150, 150),
batch_size=32,
class_mode='binary')

history = model.fit_generator(
train_generator,
steps_per_epoch=100,
epochs=100,
validation_data=validation_generator,
validation_steps=50)
