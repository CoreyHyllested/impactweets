Data Collection
src/collect/getAllFollowers.py is a script that utilizes twitter4j binaries to not hit the ratelimits.  This makes collection of data take a while.  It dumps all data, individual timelines, into a directory structure.  Variables exist to modify where the timelines are to be saved, ego-networks's user, etc.

The protectedAccounts is a file of names.  This list is twitter protected accounts and will be skipped because Twitter will timeout or fail to collect them.  For both, protectedAccounts and deleted (some people have follow bots which are removed)... they need to be removed prior to Data Formating.  I know.

grep "Showing @" * | cut -f 1  -d ':'  >> protectedAccounts
grep "Showing @" * | cut -f 1  -d ':' | xargs rm

grep "^Failed to get timeline" | cut -f 1 -d ':'   # >> protectedAccounts and xargs rm... def do this if you're repeating this process.


Data Formating.
Ah grasshopper.  The JSON isn't an array.  It requires manually massaging.

The following steps create a single JSON array.
For each file, add a ',' to the last line.   Use
$ sed -e 's/^  }$/^  },/'

Concatenate all files together into an array, basically add "[" and "]".  But be sure to remove the very last comma.

Now you have a giant JSON array of tweets.


Process.
The pig script will require the tutorial.jar and data.json to be in specific locations.
Be sure it has access.  For the least amount of work, cd to src/process/testing.
$ pig -x local GetTweetCharactoristics.pig
it will create a set of output in src/process/testing/out



Topic-Grams.
The process output will create a digraph file for graphviz.
$ sfdp -Gbgcolor=black -Ncolor=white -Ecolor=white -Nwidth=0.02 -Nheight=0.02 -Goverlap=false -Nfontcolor=white  -Earrowsize=0.4 -Gratio=fill -Tpng 

