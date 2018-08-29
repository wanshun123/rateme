- /r/rateme
- scraper to view all submissions and scrape ONE image only - preferrably directly off page - then use face detection to only use submissions with exactly one face detected (plenty of data)
- in scraper, scrape all ratings (in a form like "n/10") and take the average (of course disregard scrapes with no number ratings) - could even do text sentiment analysis? (later)

https://github.com/dmarx/psaw

---

from psaw import PushshiftAPI
api = PushshiftAPI()

submissions = list(api.search_submissions(subreddit='rateme',
                            filter=['url','id', 'title'],
                            limit=10))
submissions = [v[1:4] for v in submissions]

import re
p = re.compile("[0-9]+\/? ?[MmFf]|[MmFf]\/? ?[0-9]+")
p.findall(submissions[1][1])[0]
                            
comments = list(api.search_comments(subreddit='rateme', filter=['body', 'link_id'], limit=10))
comments = [v[::2] for v in comments]
comments = [v[0:2] for v in comments]

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

