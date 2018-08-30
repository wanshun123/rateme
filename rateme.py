# /r/rateme
# scraper to view all submissions and scrape ONE image only - preferrably directly off page - then use face detection to only use submissions with exactly one face detected (plenty of data)
# in scraper, scrape all ratings (in a form like "n/10") and take the average (of course disregard scrapes with no number ratings) - could even do text sentiment analysis? (later)

https://github.com/dmarx/psaw

---

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

p = re.compile("[0-9]\.?[0-9]?\/10")

ratings = []

# Make a ratings array with the rating, link_id  and comment it pertains to. Also add the rating included in a comment to each comment in the comments list (if there's a rating)

count = 0
for i in comments:
    if len(p.findall(i[0])) > 0:
        rating = re.search("[0-9]\.?[0-9]?", p.findall(i[0])[0])[0]
        ratings.append([rating, i[1], i[0]])
        comments[count] = i + (rating,)
    count += 1

# get rid of the t3_ in ratings[]

for i in ratings:
    i[1] = i[1][3:]

# check ratings and comments for a given link_id
# good example is returnRatings("9b31zo")
   
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
        submissionsDR.append(i + (average,))
        totalAdditions += 1
        print('rating added to submissionsDR for submission from submissionsDirect at index ' + str(count) + ' ~ ' + str(totalAdditions))
    count += 1

import os
os.getcwd()
    
import io
with io.open('submissionsDR.txt', 'w', encoding="utf-8") as filehandle:
    for i in submissionsDR:
        filehandle.write(str(i))
        
# https://github.com/Imgur/imgurpython
# download the first image of each submission
        
from imgurpython import ImgurClient
client_id = '640932c9d26a059'
client_secret = '16fb29a6a4c454940097d570e88d68dac04c3004'
client = ImgurClient(client_id, client_secret)

# to download images

import urllib.request, urllib.error
#urllib.request.urlretrieve("https://i.redd.it/0u4qa4luh3j11.jpg", "1.jpg")

# get gallery ID for images posted to imgur - should be 7 characters at end of URL
# can also make another submissions array containing only submissions with a valid link

submissionsClean = []

count = 0
for i in submissionsDR[0:50]:
    url = i[2]
    if "i.redd.it" in url:
        print('downloading single image ' + str(url) + '...')
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print('HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print('URLError: {}'.format(e.reason))
        else:
            urllib.request.urlretrieve(url, str(count) + '.jpg')
            print('downloaded image ' + str(url))
            submissionsClean.append(i)
    else:
        # imgur album
        galleryID = url[-7:]
        print('quering gallery ID ' + str(galleryID) + '...')
        try:
            conn = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            print('HTTPError: {}'.format(e.code))
        except urllib.error.URLError as e:
            print('URLError: {}'.format(e.reason))
        else:
            galleryPhotos = client.get_album_images(galleryID)
            if len(galleryPhotos) > 0:
                image = galleryPhotos[0].link
                print('downloading gallery image ' + str(image) + '...')
                urllib.request.urlretrieve(image, str(count) + '.jpg')
                print('gallery image downloaded')
                submissionsClean.append(i)
            else:
                print('no images in this gallery')
    count += 1

    
from bs4 import BeautifulSoup
data = urllib.request.urlopen('https://imgur.com/gallery/wCHERzZ').read()
soup = BeautifulSoup(data)
soup = BeautifulSoup(data, 'html.parser')
# a = soup.find(rel="image_src")
# url = a[11:32]

for link in soup.find_all('link'):
    print(link.get('href'))

for link in soup.find_all('link'):
    print(link.get('rel'))

for link in soup.find_all('rel'):
    print(link.get('href'))
    
    
<link rel="image_src"            href="https://i.imgur.com/UIWp1Rk.jpg"

###

fp = urllib.request.urlopen("https://imgur.com/gallery/wCHERzZ")
mybytes = fp.read()
mystr = mybytes.decode("utf8")
fp.close()

indexStart = mystr.find("<link rel=\"image_src\"            href=\"")
url = mystr[indexStart + 39:indexStart + 39 + 31]

###
    
items = client.get_album_images('EzdTo6E')
for item in items:
    print(item.link)
    
    
firstImage = items[0].link


