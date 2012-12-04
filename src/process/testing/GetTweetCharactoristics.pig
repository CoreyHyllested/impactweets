register tutorial.jar

--------------------------------------------------------------------------------------------------------------------------
-- Read and Process raw data.  Get some general stats on ALL the data.
-- Total Tweets, Sum Topics, Mean Topic/tweet, Sum Links, Mean Link/tweet, mean RT over total tweets.
--------------------------------------------------------------------------------------------------------------------------
raw = LOAD 'signal.out' using PigStorage('\t') as (tweetID:int, usr:bytearray, rtcount:int, topics:bytearray, links:bytearray, mentions:bytearray, datweet:bytearray);
distweets = FOREACH raw GENERATE topics, links, (topics is null ? 0 : COUNT(TOKENIZE(topics))) as tpt, (links is null ? 0 : COUNT(TOKENIZE(links))) as lpt, rtcount, usr, datweet;
grptweets = GROUP distweets ALL;
allstats  = FOREACH grptweets GENERATE COUNT_STAR(distweets.tpt) as nr, SUM(distweets.tpt) as st, AVG(distweets.tpt) as atpt, SUM(distweets.lpt) as sl, AVG(distweets.lpt), AVG(distweets.rtcount);
STORE allstats into 'p2_allstats' USING PigStorage('\t');

--------------------------------------------------------------------------------------------------------------------------
-- Collect Data based on tpt, lpt.  Not flattened :. 'datweet' would be duplicated N times in all tweets with N topics. -- 
-- Stores the number tweets as a function of the number of topics and links in the tweet.  Use in Chi-square?
--------------------------------------------------------------------------------------------------------------------------
distGroup = GROUP distweets by (tpt, lpt);
-- distPrint = FOREACH distGroup GENERATE group.tpt as tpt, group.lpt as lpt, COUNT(distweets) as nr, SUM(distweets.rtcount) as rtcount, distweets.datweet as datweet;

distPrint = FOREACH distGroup GENERATE group.tpt as tpt, group.lpt as lpt, COUNT(distweets.rtcount) as nr, SUM(distweets.rtcount) as rtcount;
store distPrint into 'p2_tweetNR_by_topic_and_link' using PigStorage('\t');

--t0l1 = FILTER distPrint BY tpt == 0 and lpt == 1;
--t1l1 = FILTER distPrint BY tpt == 1 and lpt == 1;
--t2l1 = FILTER distPrint BY tpt == 2 and lpt == 1;
--t3l1 = FILTER distPrint BY tpt == 3 and lpt == 1;
--tml1 = FILTER distPrint BY tpt >= 4 and lpt == 1;


--------------------------------------------------------------------------------------------------------------------------
-- flatten #topics and http://links.  Only maintain a list with all both.
-- Generate a list of TOPICS and every link that may be associated with topic
-- FUTURE work.  Determine how many destint tweets/(users) have link/topic.
--------------------------------------------------------------------------------------------------------------------------
flatweets = FOREACH distweets GENERATE FLATTEN(TOKENIZE(topics)) as topic, FLATTEN(TOKENIZE(links)) as link, rtcount, tpt, lpt, usr, datweet;
flatweets = DISTINCT flatweets;

rawNoNull = FILTER  flatweets BY topic IS NOT NULL;
rawNoNull = FILTER  rawNoNull BY link  IS NOT NULL;
topicGroup = GROUP  rawNoNull by topic;
-- topicLinks = FOREACH topicGroup GENERATE $0 as topic, COUNT(rawNoNull.link) as link_count, rawNoNull.link as link, rawNoNull.rtcount as rtcounts, rawNoNull.datweet as datweets;
topicLinks = FOREACH topicGroup {
	linkCntnt = FOREACH rawNoNull GENERATE link, rtcount;
	linkOrder = ORDER linkCntnt BY rtcount DESC;
	GENERATE group, COUNT(linkOrder) as links, linkOrder;
}
STORE topicLinks into 'p2_topicLinks2' using PigStorage('\t');


linkGroup  = GROUP  rawNoNull by link;
linkTopics = FOREACH linkGroup {
	topicCntnt = FOREACH rawNoNull GENERATE topic, rtcount;
	topicOrder = ORDER topicCntnt BY rtcount DESC;
	GENERATE group, SUM(topicOrder.rtcount) as rt, topicOrder;
}
STORE linkTopics into 'p2_linkTopics' using PigStorage('\t');



--------------------------------------------------------------------------------------------------------------------------
-- Find unique mentions of topics. -- 
-- find by
--------------------------------------------------------------------------------------------------------------------------
topictwt = FOREACH flatweets GENERATE topic, rtcount, usr, datweet;
topicgrp = GROUP topictwt by topic;
topicsts = FOREACH topicgrp {
	usr =  COUNT(topictwt.usr);
	rt   = SUM(topictwt.rtcount);
	GENERATE group, rt, usr;
}
topicsts = FILTER topicsts BY group == '';
STORE topicsts into 'p2_topic2' using PigStorage('\t');


usrGroup  = GROUP  distweets by usr;
usrStats  = FOREACH usrGroup  {
	GENERATE group as usr, SUM(distweets.rtcount) as totalRT, AVG(distweets.tpt) as avg_topic, AVG(distweets.lpt) as avg_link;
}
