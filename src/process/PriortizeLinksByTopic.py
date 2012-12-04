import glob
import re
import urllib2
import numpy
import math

other = []
VERSION = 0.12
debug = True;

def trace(string):
	if (debug): print string 

print "Prioritze Twitter Links by Topics, v" + str(VERSION);

strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)")


allFiles = glob.glob("./part-*");
for fileName in allFiles:
	trace (fileName)
	totalTweets = 0;
	rtweets = 0;
	retweets = 0;

	try:
		fd = open(fileName, 'r')
		txt = fd.readlines()
		trace ("opened " + fileName);


		for tweet in txt:
			line = tweet.split('\t');
			topic = line[0];
			links = line[1];
			examples = line[2];
			newexample = re.sub('\\),\\(', ')\t(', examples);
			newexample = re.sub('[(){}\n]', '', newexample);

			for instance in newexample.split('\t'):
				details = instance.split(',');
				print details[1] + "\t" + str(details[2]);


			#trace (topic + "\t" + links + "\t" + exmpl) 
			#usrname = str(line[1]);
			#retweet = line[2];
			#urllink = link[4];
			#datweet = link[6];
			
			totalTweets = totalTweets + 1;
			continue;


				#signal.write(tweetid + "\t" + usrname + "\t" + str(retweet) + "\t" + taglist + "\t" + urllist + "\t" + usrlist + "\t" + replyto + "\t" +  datweet + "\n") 

				
		print "The rate for retweets is " + str(rtweets) + "/" +  str(totalTweets)
		print "retweets = " + str(retweets);

		fd.close()

	except ValueError:
		print "oops " + fileName
