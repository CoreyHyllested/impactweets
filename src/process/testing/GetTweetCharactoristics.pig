register tutorial.jar

--------------------------------------------------------------------------------------------------------------------------
-- Read and Process raw data.  Get some general stats on ALL the data.
-- Total Tweets, Sum Topics, Mean Topic/tweet, Sum Links, Mean Link/tweet, mean RT over total tweets.
--------------------------------------------------------------------------------------------------------------------------
raw = LOAD 'data/signal.out' using PigStorage('\t') as (tweetID:int, usr:bytearray, rtcount:int, topics:bytearray, links:bytearray, mentions:bytearray, reply:bytearray, datweet:chararray);
distweets = FOREACH raw GENERATE topics, links, (topics is null ? 0 : COUNT(TOKENIZE(topics))) as tpt, (links is null ? 0 : COUNT(TOKENIZE(links))) as lpt, rtcount, usr, datweet;
grptweets = GROUP distweets ALL;
allstats  = FOREACH grptweets GENERATE COUNT_STAR(distweets.tpt) as nr, SUM(distweets.tpt) as st, AVG(distweets.tpt) as atpt, SUM(distweets.lpt) as sl, AVG(distweets.lpt), AVG(distweets.rtcount);
STORE allstats into 'out/allstats' USING PigStorage('\t');

--------------------------------------------------------------------------------------------------------------------------
-- Stores the top tweets, by retweet.  Show full tweets. --
--------------------------------------------------------------------------------------------------------------------------
toptweets = FOREACH distweets GENERATE rtcount, usr, datweet;
toptweets = ORDER toptweets BY rtcount DESC;
toptweets = LIMIT toptweets 100;
store toptweets into 'out/top100_retweets' using PigStorage('\t');


--------------------------------------------------------------------------------------------------------------------------
-- Collect Data based on tpt, lpt.  Not flattened :. 'datweet' would be duplicated N times in all tweets with N topics. -- 
-- Stores the number tweets as a function of the number of topics and links in the tweet.  Use in Chi-square?
--------------------------------------------------------------------------------------------------------------------------
distGroup = GROUP distweets by (tpt, lpt);
distPrint = FOREACH distGroup GENERATE group.tpt as tpt, group.lpt as lpt, COUNT(distweets.rtcount) as nr, SUM(distweets.rtcount) as rtcount;
store distPrint into 'out/TaRT_by_topic_link' using PigStorage('\t');

-t0l1 = FILTER distPrint BY tpt == 0 and lpt == 1;
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

--------------------------------------------------------------------------------------------------------------------------
-- topicscore: unique mentions of topics + RT count.
-- toptopics:  topicscore^^ with the utility topics (FF, FB, foursquare) removed
--------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------------------------
-- Generate simplistic topic score --  
-----------------------------------------------------------------------------------------------------------
topictwt = FOREACH flatweets GENERATE topic, rtcount, usr, datweet;
topicgrp = GROUP topictwt by topic;
topicsts = FOREACH topicgrp {
	score = COUNT(topictwt.usr) + SUM(topictwt.rtcount);
	GENERATE group, score as score;
}
topicscore = FILTER topicsts BY group is NOT NULL; 
topicscore = ORDER  topicscore BY score DESC;
topicscore = LIMIT  topicscore 1500;
STORE topicscore into 'out/topicscore' using PigStorage('\t');



-----------------------------------------------------------------------------------------------------------
-- Generate simplistic topic score --  
-----------------------------------------------------------------------------------------------------------
linktwt = FOREACH flatweets GENERATE link, rtcount, usr, datweet;
linkgrp = GROUP linktwt by link;
linksts = FOREACH linkgrp {
	score = COUNT(linktwt.usr) + SUM(linktwt.rtcount);
	GENERATE group as link, score as score;
}
linkscore = FILTER linksts BY link is NOT NULL; 
linkscore = ORDER  linkscore BY score DESC;
STORE linkscore into 'out/linkscore' using PigStorage('\t');

-----------------------------------------------------------------------------------------------------------
-- Remove utility topics --  
-- Creates list of non-utility topics, rated by their score.  Bind Links/topic to this list. 
-----------------------------------------------------------------------------------------------------------
util = LOAD 'data/topics.utility' using PigStorage('\t') as (utiltopic:chararray);
nonutil = JOIN util BY utiltopic RIGHT OUTER, topicscore BY group;
nonutil = FILTER nonutil BY utiltopic IS NULL;
toptopics = FOREACH nonutil GENERATE group as topic, score as score;


-----------------------------------------------------------------------------------------------------------
-- Remove tweets that are missing links and topics.  Necessary for finding topics describing links.  --  
-----------------------------------------------------------------------------------------------------------
rawNoNull = FILTER  flatweets BY topic IS NOT NULL;
rawNoNull = FILTER  rawNoNull BY link  IS NOT NULL;
topicGroup = GROUP  rawNoNull by topic;
topicLinks = FOREACH topicGroup {
	-- also available: datweet --
	linkCntnt = FOREACH rawNoNull GENERATE link, rtcount;
	linkOrder = ORDER linkCntnt BY rtcount DESC;
	linkOrder = LIMIT linkOrder 5;
	GENERATE group, linkOrder;
}


---- 500 NonUtil Topics with Associated Links (Max 5) -----------------------------------------------------
-- Creates list of non-utility topics, rated by their score.  Links/topic rated . 
-----------------------------------------------------------------------------------------------------------
tl_ordered = JOIN toptopics BY topic RIGHT OUTER, topicLinks BY group;
tl_ordered = FILTER  tl_ordered BY toptopics::topic IS NOT NULL;
tl_ordered = FOREACH tl_ordered GENERATE topic, score, linkOrder as links;
tl_ordered = ORDER   tl_ordered by score DESC;
tl_ordered = LIMIT   tl_ordered 500;
STORE tl_ordered into 'out/links_by_topic' using PigStorage('\t');



---- 250 (from toplinks) bound with topics describing link ------------------------------
-- Creates list of links, rated by their score.  Providing all describing topics. 
-----------------------------------------------------------------------------------------
toplinks   = LIMIT  linkscore 250;
linkGroup  = GROUP  rawNoNull by link;
linkTopics = FOREACH linkGroup {
	topicCntnt = FOREACH rawNoNull GENERATE topic, rtcount;
	topicOrder = ORDER topicCntnt BY rtcount DESC;
	GENERATE group, topicOrder as topics;
}
lt_ordered = JOIN toplinks BY link RIGHT OUTER, linkTopics BY group;
lt_ordered = FILTER  lt_ordered BY link IS NOT NULL;
lt_ordered = FOREACH lt_ordered GENERATE link, score, topics;
lt_ordered = ORDER   lt_ordered by score DESC;
STORE lt_ordered into 'out/link_description' using PigStorage('\t');




usrGroup  = GROUP  distweets by usr;
usrStats  = FOREACH usrGroup  {
	GENERATE group as usr, SUM(distweets.rtcount) as totalRT, AVG(distweets.tpt) as avg_topic, AVG(distweets.lpt) as avg_link;
}
STORE usrStats into 'out/userscore' using PigStorage('\t');
