import json
import glob
import re

other = []
VERSION = 0.38
debug = True;

def trace(string):
	if (debug): print string 

print "Process Twitter TimeLines, v" + str(VERSION);

signal = open('signal.out', 'w+')
strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")


allFiles = glob.glob("/home/corey.hyllested/impactweets/data/*.json");
for fileName in allFiles:
	trace (fileName)
	totalTweets = 0;
	importweets = 0;
	rtweets = 0;
	mtweets = 0;
	htweets = 0;
	ltweets = 0;
	retweets = 0;

	try:
		fd = open(fileName, 'r')
		trace ("opening " + fileName);
		txt = fd.read()
		trace ("reading " + fileName);
		j = json.loads(txt)
		trace ("loading json of " + fileName);
		for idx in j:
			usrname = idx['user']['screen_name'].lower()
			retweet = idx['retweet_count'] 

			hashtag = idx['entities']['hashtags']
			urllink = idx['entities']['urls']
			mention = idx['entities']['user_mentions']

			totalTweets = totalTweets + 1;
			if (idx.has_key('retweeted_status') or not idx.has_key('text')):
				retweets = retweets + 1;
				continue;

			
			if (retweet != 0 or len(hashtag) != 0 or len(urllink) != 0 or len(mention) != 0):
				importweets = importweets + 1

				tweetid = idx['id_str']
				thedate = idx['created_at'].encode('utf-8')
				replyto = idx['in_reply_to_status_id_str'] or "";
				
				taglist = ""	#taglist = "\ttags (" + str(len(hashtag)) + ") :  "
				urllist = ""	#urllist = "\turls (" + str(len(urllink)) + ") :  "
				usrlist = ""	#usrlist = "\tusrs (" + str(len(mention)) + ") :  "

				if (retweet != 0): rtweets = rtweets + 1;
				if (len(hashtag) != 0): htweets = htweets + 1;
				if (len(urllink) != 0): ltweets = ltweets + 1;
				if (len(mention) != 0): mtweets = mtweets + 1;

				for tag in hashtag:
					taglist = taglist + strip_unicode.sub('', tag['text'].lower().encode('utf-8')) + " " 

				for url in urllink:
					urllist = urllist + url['url'].encode('utf-8') + " " 

				for usr in mention:
					#add this to conversation "group" , is conversation bi-directional?
					usrlist = usrlist + usr['screen_name'].encode('utf-8') + " " 

				datweet = strip_unicode.sub('.', idx['text'])
				datweet = datweet.replace('\n', ' ')
				datweet = datweet.replace('\t', ' ')
				signal.write(tweetid + "\t" + usrname + "\t" + str(retweet) + "\t" + taglist + "\t" + urllist + "\t" + usrlist + "\t" + thedate + "\t" + replyto + "\t" +  datweet + "\n") 

			else:
				other.append(idx['text'])
				

#		print "\n\nLame Tweets"
#		for i in other:
#			print i
 
		print "The rate for importweets is " + str(importweets) + "/" +  str(totalTweets)
		print "The rate for retweets is " + str(rtweets) + "/" +  str(totalTweets)
		print "The rate for hashtags is " + str(htweets) + "/" +  str(totalTweets) 
		print "The rate for mentions is " + str(mtweets) + "/" +  str(totalTweets)
		print "The rate for urllinks is " + str(ltweets) + "/" +  str(totalTweets) 
		print "retweets = " + str(retweets);

		fd.close()

	except ValueError:
		print "oops " + fileName
