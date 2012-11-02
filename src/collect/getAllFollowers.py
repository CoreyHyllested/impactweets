import tweepy
import os
import subprocess as ps
from subprocess import call
import datetime as dt
import errno
import re

debugOn = False;
user    = "CoreyHyllested"
getFriendsBin = "/home/corey.hyllested/twitter/t4j/bin/friendsandfollowers/getFriendsIDs.sh " + user;

def debug (x):
	global debugOn
	if (debugOn == True): print x


def login():
	consumer_key="xp7VAWmCnVq1dviT0YO9pw"
	consumer_secret="IpVnz8xpqFJOxidYGOclUA9G2tDw4e7eTgUcKpJ0bg" 
	access_token="15669956-8fCVRqpf3XGnaDvC4yxLbSKWWCWvZRYscDPXaAVS5"
	access_token_secret="Tp67vtcXhMhFZyvCGqyBuBgsXPe4j3WbQxNhuq9OMPc"

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	return tweepy.API(auth)


def userDirectory(u):
	dir = "/home/corey.hyllested/twitter/data/project/" + u + "/"
	mkdir(dir);
	return dir;

def userRawDir(u):
	today = dt.datetime.today()
	dir = "/home/corey.hyllested/twitter/data/project/" + u + "/raw/" + str(today.month) + "/" + str(today.day) + "/"
	mkdir(dir);
	return dir;

def userFollowList(u):
	return "/home/corey.hyllested/twitter/data/project/" + u + "/" + u + ".friends"

def userFoFList(u):
	return "/home/corey.hyllested/twitter/data/project/" + u + "/" + u + ".FoF"

def getFriendsExec(u):
	return "/home/corey.hyllested/twitter/t4j/bin/friendsandfollowers/getFriendsIDs.sh " + u;



#create a new file, append .#NR 
def nextFileVersion(fileName):
	ver = 0;
	path = fileName + "." + str(ver);
	while (os.path.lexists(fileName + "." + str(ver)) == True):
		ver = ver + 1;
	return path; 


def fileExists(fileName):
	rc = os.path.lexists(fileName);
	#print "does " + path + " exist? " + str(rc);
	return rc;

	
def getTimelineForUser(u):
	timelineExec = "/home/corey.hyllested/twitter/t4j/bin/timeline/getUserTimeline.sh " + u;
	
	#newFileVer = nextFileVersion(userRawDir(user) + u);
	#debug ("getTimelineForUser("+u+"): " + newFileVer)
	if (not fileExists(userRawDir(user) + u)):
		print ("downloading timeline for '" + u + "'")
		os.system(timelineExec + " | sed -e '/^\\[./d' -e '/\/usr\//d' -e '/^$/d' -e '/^\\]$/,$d' > " + userRawDir(user) + u)
		
#	if (newFileVer[:len(newFileVer)-1]) == str(0):
#		debug (newFileVer + " output already exists!")
#	else:
#		print ("downloading timeline for '" + u + "'")
#		os.system(timelineExec + " | sed -e '/^\\[./d' -e '/\/usr\//d' -e '/^$/d' -e '/^\\]$/,$d' > " + newFileVer)
	

def createFriendList(u):
	getFriendsCmd = "/home/corey.hyllested/twitter/t4j/bin/friendsandfollowers/getFriendsIDs.sh " + user;
	os.system(getFriendsCmd + " | sed -e '/^\\[/d' -e '/^$/d' -e '/java/d' -e '/Listing/d' > " + userFollowList(user))
	f = open(userFollowList(user), 'r');
	friendString = f.read();
	userFriends = re.split("\n", friendString);


def createFoFList(u):
	#print u;
	os.system(getFriendsExec(u) + " | sed -e '/^\\[/d' -e '/^$/d' -e '/java/d' -e '/Listing/d' >> " + userFoFList(user))


def mkdir(path):
	try:
		os.makedirs(path)
	except OSError as e:
		if e.errno == errno.EEXIST:
			pass
		else:
			raise


def processLists(u):
	friends = userFollowList(u);
	fof = userFoFList(u);
	combined = userDirectory(u) + "/followed.uniq";
	os.system("cat " + friends + " " + fof + " | sort | uniq > " + combined); 
	return combined;
	
def readProtectedList():
	protectedMap = {}
	f = open('/home/corey.hyllested/twitter/data/project/protectedAccounts', 'r');
	skiplist = re.split("\n", f.read());
	for i in skiplist:
		protectedMap[i] = i;
	return protectedMap;

api = login();
uDir = userDirectory(user)
protected = readProtectedList(); 


os.system(getFriendsBin + " | sed -e '/^\\[/d' -e '/^$/d' -e '/java/d' -e '/Listing/d' > " + userFollowList(user))
f = open(userFollowList(user), 'r'); friendString = f.read();
userFriends = re.split("\n", friendString);

for idx in userFriends:
	if idx != '':
		u = api.get_user(idx);
		createFoFList(u.screen_name)

		
pFileName = processLists(user);

pFile = open(pFileName, 'r');
followed = re.split("\n", pFile.read());

counter = 0;
suspended = [] 
for idx in followed:
	counter = counter + 1
	if (counter % 125 == 0):
		print "thus far-> " + str(counter)

	if idx != '':
		try:
			u = api.get_user(idx);
			if (protected.has_key(u.screen_name)) or protected.has_key(u.screen_name.lower()):
				debug ("PROTECTED\t" + u.screen_name )
				continue
			debug ("getTimelineForUser(" + u.screen_name + ")")
			getTimelineForUser(u.screen_name)
		except tweepy.TweepError:
			#print "SUSPENDED\t" + idx
			suspended.append(idx)


suspendedFile = open('/home/corey.hyllested/twitter/data/project/suspendedAccounts', 'a');
suspendedFile.seek(0, 2);
for acct in suspended:
	suspendedFile.write(str(acct) + "\n")

suspendedFile.close();
