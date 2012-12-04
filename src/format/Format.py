import json
import glob
import math
import re
import urllib2
import traceback
import httplib
import networkx as nx

VERSION = 0.52
debug = False;

def trace(string):
	if (debug): print string 

print "Process Twitter TimeLines, v" + str(VERSION);

signal = open('signal.out', 'w+')
strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")


dg = nx.DiGraph();
allFiles = glob.glob("/home/corey.hyllested/impactweets/data/*.json");

rtweets = 0;
mtweets = 0;
htweets = 0;
ltweets = 0;
retweets = 0;
lametweets = 0;
totalTweets = 0;
importweets = 0;
topics = {}

for fileName in allFiles:
	trace (fileName)

	try:
		fd = open(fileName, 'r')
		trace ("opening " + fileName);
		txt = fd.read()
		trace ("reading " + fileName);
		j = json.loads(txt)
		fd.close()

		urlcount = 0
		for idx in j:
			other = []
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

				if (len(hashtag) == 0 and len(urllink) == 0 and retweet >= 250):  
					print idx['text']
					#other.append(idx['text'])


				tweetTags = []
				for tag in hashtag:
					topicInstance = strip_unicode.sub('', tag['text'].lower().encode('utf-8'))  
					taglist = taglist + topicInstance + " " 

					tweetTags.append(topicInstance);

					if topics.has_key(topicInstance):
						topics[topicInstance] = topics[topicInstance] + 1;
					else:
						topics[topicInstance] = 1;


				size = len(hashtag);
				if size >= 2:
					
					for sidx in range(size):
						if tweetTags[sidx] == '': continue;
						leftag = tweetTags[sidx]
						for widx in range(sidx + 1, size):
							if tweetTags[widx] == '': continue;
							rightag = tweetTags[widx]
							nweight = float(retweet);

							if (size == 2): nweight = nweight + float(0.5);
							if (size > 2):  
								dnom = float(math.factorial(size)/(math.factorial(size-2) * 2)  )
								nweight = float(nweight) + float(1/dnom); 
								#print "nweight(" + str(nweight) + ") = RT(" + str(retweet) + ") + " +  str(float(1/dnom)) + " for " + str(size) + " topics"; 

							if dg.has_edge(leftag,rightag):
								nweight = float(nweight) + float(dg[leftag][rightag]['weight']);
								#print (leftag + "-" + rightag + "=" + str(nweight) + "\twas " + str(dg[leftag][rightag]['weight']) + " rt:" + str(retweet));
							dg.add_edge(tweetTags[sidx], tweetTags[widx], weight=nweight) 



				for url in urllink:
					urllist = urllist + url['url'].encode('utf-8') + " " 
					#print str(urlcount) + "/" + str((totalTweets)) + " :\t" + url['url'];
					urlcount = urlcount + 1

					#try:
					#	realresrc = urllib2.urlopen(url['url'].encode('utf-8'), timeout=20).geturl() + " " 
					#	urllist = urllist +  realresrc
					#	print realresrc
					#except urllib2.HTTPError, e:
					#	traceback.print_exc();
					#	print "HTTPError"
					#except urllib2.URLError, e:
					#	traceback.print_exc();
					#	print "URLERR"
					#except ValueError:
					#	print "Lol, wut, ValueError?"
					#	traceback.print_exc();
					#except httplib.HTTPException, e:
					#	traceback.print_exc();
					#	print "HTTPExcption "
					#except Exception:
					#	traceback.print_exc();
					#	print "generic Excption "
					#except:
					#	traceback.print_exc();
					#	print "caught other error"


				for usr in mention:
					#add this to conversation "group" , is conversation bi-directional?
					usrlist = usrlist + usr['screen_name'].encode('utf-8') + " " 

				datweet = strip_unicode.sub('.', idx['text'])
				datweet = datweet.replace('\n', ' ')
				datweet = datweet.replace('\t', ' ')
				try:
					signal.write(tweetid + "\t" + usrname + "\t" + str(retweet) + "\t" + str(taglist) + "\t" + str(urllist) + "\t" + usrlist + "\t" + replyto + "\t" +  datweet + "\n") 
				except UnicodeDecodeError:
					print "caught decode error " + str(tweetid);

			else:
				lametweets = lametweets + 1;

				
		print "The rate for importweets is " + str(importweets) + "/" +  str(totalTweets)
		print "The rate for lametweets is " + str(lametweets) + "/" +  str(totalTweets) + " = " + str(float(lametweets)/float(totalTweets));
		print "The rate for retweets is " + str(rtweets) + "/" +  str(totalTweets) + " = " + str(float(rtweets)/float(totalTweets))
		print "The rate for hashtags is " + str(htweets) + "/" +  str(totalTweets) + " = " + str(float(htweets)/float(totalTweets)) 
		print "The rate for mentions is " + str(mtweets) + "/" +  str(totalTweets) + " = " + str(float(mtweets)/float(totalTweets))
		print "The rate for urllinks is " + str(ltweets) + "/" +  str(totalTweets) + " = " + str(float(ltweets)/float(totalTweets)) 
		print "retweets = " + str(retweets);

		topicSort = open('topic.relationship', 'w+');
		topicFile = open('topic.digraph', 'w+');
		topicFile.write("digraph g {\n")
		for edge in dg.edges(data=True):
			n1, n2, data = edge;
			penwidth = data['weight'];
			if (penwidth > 5): penwidth = 5;
			topicFile.write("\"#" + n1 + "\"\t->\t\"#" + n2 + "\"\t" + "\t[penwidth=" + str(penwidth) +", weight="+ str(data['weight']) +"]\n")
			topicSort.write("#"   + n1 + "\t#"         + n2 + "\t"   +                                              str(data['weight']) + "\n")
		topicFile.write("}\n")
		topicFile.close()
		topicSort.close()

		topicFile = open('topic.topics', 'w+');
		for tag in topics.keys():
			topicFile.write(tag + "\t" + str(topics[tag]) + "\n");
		topicFile.close()


	except ValueError:
		traceback.print_exc();
		print "oops " + fileName
