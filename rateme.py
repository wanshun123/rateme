- /r/rateme
- scraper to view all submissions and scrape ONE image only - preferrably directly off page - then use face detection to only use submissions with exactly one face detected (plenty of data)
- in scraper, scrape all ratings (in a form like "n/10") and take the average (of course disregard scrapes with no number ratings) - could even do text sentiment analysis? (later)

https://github.com/dmarx/psaw

---

from psaw import PushshiftAPI
api = PushshiftAPI()
import re

submissions = list(api.search_submissions(subreddit='rateme',
                            filter=['url','id', 'title'],
                            limit=50))
submissions = [v[1:4] for v in submissions]

age = []
sex = []

p = re.compile("[0-9]+\/? ?[MmFf]|[MmFf]\/? ?[0-9]+")

for i in submissions:
    if len(p.findall(i[1])) > 0:
        # there is a regex match for something like 22M, so append the gender and age to those arrays
        # p.findall(i[1])[0]) is item at index 0 (ie. first match) for finding the complicated regex string above in the title (which is i[1]), and we're appending the first match of [0-9]+ and [MmFf] for those
        age.append(re.search("[0-9]+", p.findall(i[1])[0])[0])
        sex.append(re.search("[MmFf]", p.findall(i[1])[0])[0])
        #re.search("[0-9]+", p.findall(i[1])[0])[0]
        #re.search("[MmFf]", p.findall(i[1])[0])[0]
    else:
        age.append('NA')
        sex.append('NA')
    #i = i + (age[i],sex[i])
    
#submissions = [v[::2] for v in submissions]

count = 0
for i in submissions:
    submissions[count] = i + (age[count],sex[count],)
    count += 1
    
comments = list(api.search_comments(subreddit='rateme', filter=['body', 'link_id'], limit=10))
comments = [v[::2] for v in comments]
comments = [v[0:2] for v in comments]

p = re.compile("[0-10]\.?[0-9]?\/10")

ratings = []
ratingsList = []

# should get rid of all comments that don't have a rating

count = 0
for i in comments:
    if len(p.findall(i[0])) > 0:
        # rating out of 10 found (hopefully)
        #ratings.append(p.findall(i[0])[0])
        #ratingsList[count] = (p.findall(i[0])[0],i[1])
        ratings.append([re.search("[0-9]\.?[0-9]?", p.findall(i[0])[0])[0], i[1]])
        #ratings.append([p.findall(i[0])[0], i[1]])
        #print('rating found in --- ' + i[0] + ' ---. count = ' + str(count))
    else:
        print('deleting comment in --- ' + i[0] + ' --- since no rating. count = ' + str(count))
        #del comments[count]
    count += 1
    
for i in comments:
    i[1][3:]

'''
links = []
for i in result:
    links.append(i[1])
'''
        
# result[0][1] = link_id
# result[0][2] = title
# result[0][3] = imgur link
# test[0][0] = comment
# test[0][2][3:] = link_id

---

