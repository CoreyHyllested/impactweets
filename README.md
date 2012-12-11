Data Collection
src/collect/getAllFollowers.py is a script that utilizes twitter4j binaries to not hit the ratelimits.  This makes collection of data take a while.  It dumps all data, individual timelines, into a directory structure.  Variables exist to modify where the timelines are to be saved, ego-networks's user, etc.

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

