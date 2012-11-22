register tutorial.jar
raw = LOAD 'signal.out' using PigStorage('\t') as (tweetID, usr, rtcount, topics, links, mentions, created, replyto, datweet);

-- Done Get an ordered idea of topics by pure count.
-- Get a topic count per individual user. (e.g.  10 topic mentions from 10 users; alternately 10 mentions from 3 users).
-- Get a topic count per tweet.  (e.g. 10 topic mentions in 10 tweets, 10 mentions in 7 tweets).
topicFiltr = FILTER raw BY topics IS NOT NULL;
topicTweet = FOREACH topicFiltr GENERATE usr, rtcount, FLATTEN(TOKENIZE(topics)) as topic, links, mentions, datweet;
topicGrp   = GROUP topicTweet BY topic;
topicCnt   = FOREACH topicGrp GENERATE $0 as topic, COUNT_STAR(topicTweet) as topicCount, topicTweet; 
topicOrd   = ORDER topicCnt by topicCount;


-- How many topic in a single tweet before we suspect SPAM?  2 , 3, 4, ANY?
topicCount = FOREACH topicFiltr GENERATE COUNT_STAR(TOKENIZE(topics)) as tpt, topics, datweet;
tpt3       = FILTER topicCount BY tpt > 2


-- Done:: Get an ordered idea of links by pure count.
-- Get a topic count per individual user. (e.g.  10 topic mentions from 10 users; alternately 10 mentions from 3 users).
-- Get a topic count per tweet.  (e.g. 10 topic mentions in 10 tweets, 10 mentions in 7 tweets).
linkFiltr = FILTER raw BY links IS NOT NULL;
linkCount = FOREACH linkFiltr GENERATE usr, rtcount, topics, COUNT_STAR(TOKENIZE(links)) as lpt, TOKENIZE(links) as links, mentions, datweet;
linkTweet = FOREACH linkCount GENERATE usr, rtcount, topics, lpt, FLATTEN(links) as link, mentions, datweet;
linkGrp   = GROUP linkTweet BY link;
linkCnt   = FOREACH linkGrp GENERATE $0 as link, COUNT_STAR(linkTweet) as linkCount, linkTweet; 
linkOrd   = ORDER linkCnt by linkCount;

--include group of users, not tweets
--linkCnt   = FOREACH linkGrp GENERATE $0.link as link, $0.usr as usr, COUNT_STAR(linkTweet) as linkCount, linkTweet; 


--What are the 3+ links/tweet
link3lpt  = FILTER linkTweet BY lpt > 2;
linkGrp   = GROUP linkTweet BY (link, usr);



-- Begins to create a graph of topics.
topicLinks = FILTER  raw        BY topics IS NOT NULL;
topicLinks = FILTER  topicLinks BY links  IS NOT NULL;
topicLinks = FOREACH topicLinks GENERATE FLATTEN(TOKENIZE(topics)) as topic, links
theTopicLinks = GROUP   topicLinks by topic;
theTopicLinks = FOREACH theTopicLinks GENERATE $0 as topic, COUNT(topicLinks) as count, topicLinks.links;

linkTopics = FILTER  raw        BY topics IS NOT NULL;
linkTopics = FILTER  linkTopics BY links  IS NOT NULL;
linkTopics = FOREACH linkTopics GENERATE links, FLATTEN(TOKENIZE(topics)) as topic;
theLinkTopics = GROUP linkTopics by links;
theLinkTopics = FOREACH thelinkTopics GENERATE $0 as links, COUNT(linkTopics) as count, linkTopics.topic;



-- get better stopword list
--stopWords = LOAD 'stopwords' using PigStorage('\t') as word;
--cln1 = FOREACH raw GENERATE FLATTEN(org.apache.pig.tutorial.NGramGenerator(text)) as ngram, text;  
--tokenGrp = GROUP cln1 BY ngram;
--tokenCnt = FOREACH tokenGrp GENERATE $0 as ngram, COUNT_STAR($1) as count; 
--tokenJnd = JOIN stopWords BY word RIGHT OUTER, tokenGrp BY $0;
--tokenFlt = FILTER tokenJnd BY $0 IS NULL;
--tokenAll = GROUP tokenFlt ALL;
--tweets = FOREACH tokenAll GENERATE COUNT_STAR(tokenFlt);
--tokenCount = FOREACH tokenFlt GENERATE tokenGrp::group as ngram, COUNT(tokenGrp::cln1) as count, ((float) COUNT(tokenGrp::cln1) / tweets.$0) AS freq;
--tokenFiltr = FILTER tokenCount BY freq > .004;
--tokenOrder = ORDER tokenFiltr BY freq desc;
--STORE tokenFiltr INTO '/tmp/Expectations7' USING PigStorage(); -- SAVE tokenRatio, unfiltered, because those terms may be useful.. or maybe not, assume 0
