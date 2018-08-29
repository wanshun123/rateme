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
    if "i.redd.it" in i[2]:
        submissionsDirect.append(i)
    count += 1

# get count of entries in submissions that link straight to i.redd.it if you want 
'''
count = 0
for i in submissions:
    if "i.redd.it" in i[2]:
        #print('found')
        count += 1
'''
        
# pull comments
    
comments = list(api.search_comments(subreddit='rateme', filter=['body', 'link_id'], limit = 1000))
comments = [v[::2] for v in comments]
comments = [v[0:2] for v in comments]

p = re.compile("[0-9]\.?[0-9]?\/10")

ratings = []

# Make a ratings array with the rating, link_id  and comment it pertains to. Also add the rating included in a comment to each comment in the comments list (if there's a rating)

count = 0
for i in comments:
    if len(p.findall(i[0])) > 0:
        rating = re.search("[0-9]\.?[0-9]?", p.findall(i[0])[0])[0]
        #print(rating)
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

# loop through all submissions (only those in submissionsDirect that are direct image links), check if the link_id at submissionsDirect[0] (which is i[0] here) matches each rating entry at j[1], make a ratings array for each submission, then get the average of ratings and add that to the submissionsDirect list under its relevant submission

count = 0
for i in submissionsDirect:
    ratingsArray = []
    for j in ratings:
        if i[0] == j[1]:
            ratingsArray.append(j[0])
    if len(ratingsArray) > 0:
        ratingsArray = [float(i) for i in ratingsArray]
        average = sum(ratingsArray)/len(ratingsArray)
        submissionsDirect[count] = i + (average,)
        print('rating added for submission at index ' + str(count))
    count += 1


