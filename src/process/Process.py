import json
import glob
import math
import re
import urllib2
import traceback
import networkx as nx

other = []
VERSION = 0.42
debug = False;

def trace(string):
	if (debug): print string 

print "Process Twitter TimeLines, v" + str(VERSION);

signal = open('signal.out', 'w+')
strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")


dg = nx.MultiDiGraph();
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
	topics = {}

	try:
		fd = open(fileName, 'r')
		trace ("opening " + fileName);
		txt = fd.read()
		trace ("reading " + fileName);
		j = json.loads(txt)
		fd.close()

		urlcount = 0
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
				#thedate = idx['created_at'].encode('utf-8')
				replyto = idx['in_reply_to_status_id_str'] or "";
				
				taglist = ""
				urllist = ""
				usrlist = ""

				if (retweet != 0): rtweets = rtweets + 1;
				if (len(hashtag) != 0): htweets = htweets + 1;
				if (len(urllink) != 0): ltweets = ltweets + 1;
				if (len(mention) != 0): mtweets = mtweets + 1;


				tweetTags = []
				for tag in hashtag:
					topicInstance = strip_unicode.sub('', tag['text'].lower().encode('utf-8'))  
					tweetTags.append(topicInstance);

					if topics.has_key(topicInstance):
						topics[topicInstance] = topics[topicInstance] + 1;
					else:
						topics[topicInstance] = 1;


				size = len(hashtag);
				if size >= 2:
					weight = 1;
					dnom = 0;
					multiplier = retweet or 1
					if (size == 2): dnom= 2;
					if (size > 2):  dnom = math.factorial(size) / (math.factorial(size-2) * 2)
					weight = str(float(1)/float(dnom))
					
					for sidx in range(size):
						for widx in range(sidx + 1, size):
							dg.add_edge(tweetTags[sidx], tweetTags[widx], key=tweetid, weight=weight*multiplier) 


				for url in urllink:
					urllist = urllist + url['url'].encode('utf-8') + " " 

					print str(urlcount) + "/" + str((totalTweets)) + " :\t" + url['url'];
					urlcount = urlcount + 1
					try:
						realresrc = urllib2.urlopen(url['url'].encode('utf-8')).geturl() + " " 
						urllist = urllist +  realresrc
						print realresrc
					except urllib2.HTTPError, e:
						print "HTTPError"
					except urllib2.URLError, e:
						print "URLERR"
					except httplib.HTTPException, e:
						print "HTTPExcption "
					except Exception:
						print "generic Excption "


				for usr in mention:
					#add this to conversation "group" , is conversation bi-directional?
					usrlist = usrlist + usr['screen_name'].encode('utf-8') + " " 

				datweet = strip_unicode.sub('.', idx['text'])
				datweet = datweet.replace('\n', ' ')
				datweet = datweet.replace('\t', ' ')
				signal.write(tweetid + "\t" + usrname + "\t" + str(retweet) + "\t" + taglist + "\t" + urllist + "\t" + usrlist + "\t" + replyto + "\t" +  datweet + "\n") 

			else:
				other.append(idx['text'])
				
#		print "\n\nLame Tweets"
#		for i in other:
#			print i
 
		print "The rate for importweets is " + str(importweets) + "/" +  str(totalTweets)
		print "The rate for retweets is " + str(rtweets) + "/" +  str(totalTweets) + " = " + str(float(rtweets)/float(totalTweets))
		print "The rate for hashtags is " + str(htweets) + "/" +  str(totalTweets) + " = " + str(float(htweets)/float(totalTweets)) 
		print "The rate for mentions is " + str(mtweets) + "/" +  str(totalTweets) + " = " + str(float(mtweets)/float(totalTweets))
		print "The rate for urllinks is " + str(ltweets) + "/" +  str(totalTweets) + " = " + str(float(ltweets)/float(totalTweets)) 
		print "retweets = " + str(retweets);

		#topicFile = open('out.topicRelationship', 'w+');
		#topicFile.write("digraph g {\n")
		#for edge in dg.edges(keys=True, data=True):
		#	n1, n2, k, data = edge;
		#	topicFile.write("\"#" + n1 + "\"\t->\t\"#" + n2 + "\"\t" + "\n") #+  "\t[weight=" + data['weight'] +"]" 
		#topicFile.write("}\n")
		#topicFile.close()


		#topicFile = open('out.topics', 'w+');
		#for tag in topics.keys():
		#	topicFile.write(tag + "\t" + str(topics[tag]) + "\n");
		#topicFile.close()


	except ValueError:
		print "oops " + fileName
