#!/usr/bin/env python3

#sox,imagemagick,ffmpeg
import os
from twython import Twython
from twython import TwythonError
import time
import random
import subprocess
import html
import re
import json
import unicodedata

def translate2cw(msg):
	CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
     	'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',
        
        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.',
		'À': '--.-',
		'Å': '--.-',
		'Ä': '.-.-',
		'È': '.-..-',
		'É': '..-..',
		'Ö': '---.',
		'Ü': '..--',
		'ß': '...--..',
		'Ñ': '--.--',
		'.': '.-.-.-',
		',': '--..--',
		':': '---...',
		';': '-.-.-.',
		'?': '..--..',
		'-': '-....-',
		'_': '..--.-',
		'(': '-.--.',
		')': '-.--.-',
		'=': '-...-',
		'+': '.-.-.',
		'/': '-..-.',
		'@': '.--.-.',
		' ': '/'

        }
	tr_msg=""
	for char in msg:
		CHAR=char.upper()
		if CHAR in CODE:
			tr_msg=tr_msg+CODE[CHAR]+" "
	
	
	return tr_msg

def video(msg):	
	
	tr_msg=translate2cw(msg)
		
	os.system('bash create_audio.sh '+tr_msg)
	os.system('bash create_images.sh '+tr_msg)
	
	outff = subprocess.check_output('ffmpeg -hide_banner -loglevel panic -f gif -i ./img/total.gif -i ./audio/total.wav  -pix_fmt yuv420p -r 20 ./video/video.mp4', shell=True)
	
	vid = open('./video/video.mp4', 'rb')
	
	os.system('bash tidy.sh')
	
	return vid

	
def write_file(file,content):
	f = open(file, "w")
	f.write(str(content))
	f.close

def read_file(file):
	f = open(file, "r")
	content=f.read()
	f.close
	
	return content

	
def main():
	import config as c
	api = Twython(c.APP_KEY, c.APP_SECRET,c.OAUTH_TOKEN, c.OAUTH_TOKEN_SECRET)
	
	lastid_folder='./lastids/'
	search_file='search.txt'
	filter_file='filter.txt'
	refresh_time=10
	vid_pause_time=10
	search_pause_time=30
	
	os.system('bash tidy.sh')
	
	while True:
	
		if not os.path.isfile('alreadytweeted.json'):
			write_file('alreadytweeted.json','{"1":1}')
		alreadytweeted=json.loads(read_file('alreadytweeted.json'))
		
		tweetcount=0
		
		with open(search_file) as f:
			for search in f.readlines():
				search=search.strip()
				print(' >>> '+search)
				lastid_file=lastid_folder+search

				if not os.path.isfile(lastid_file):
					write_file(lastid_file,'1')
					firstrun=1
				else:
					firstrun=0
					
				lastid=read_file(lastid_file)
				try:
					if search.find("#",0,1) != -1:
						search_tweets=api.search(q=search,since_id=lastid)
						rev_search_tweets=reversed(search_tweets['statuses'])
					elif search.find("@",0,1) != -1:
						rev_search_tweets=reversed(api.get_user_timeline(screen_name=search[1:],since_id=lastid))
					elif search.find("§",0,1) != -1:
						search_tweets=api.search(q='@'+search[1:],since_id=lastid)
						rev_search_tweets=reversed(search_tweets['statuses'])
					
					for tweet in rev_search_tweets:
												
						tid=str(tweet['id'])
						msg=html.unescape(tweet['text'])
						msg=msg.replace('ß','ss')
						msg=unicodedata.normalize('NFKD',msg).encode('ASCII','ignore').decode('utf-8')
						
						filtered=0
						
						# do not respond to own tweets
						if search.find("§",0,1) != -1 and search[1:] == tweet['user']['screen_name']:
							filtered=1
						
						# work the filter file
						with open(filter_file) as ff:
							for filter in ff.readlines():
								filter=filter.strip()
								if filter.find('@',0,1) != -1:
									if '@'+tweet['user']['screen_name'] == filter:
										filtered=1
								else:
									if msg.find(filter) != -1:
										filtered=1
						
						# eliminate double tweets
						if tid in alreadytweeted.keys():
							filtered=1
						
						# no retweets
						if msg.find("RT ",0,3) != -1:
							filtered=1
						
						# no conversations, execpt with self
						if msg.find("@",0,1) != -1:
							if search.find('§',0,1) != -1 and msg.find('@'+search[1:]) == 0:
								#no action
								filtered=filtered
							else:
								filtered=1
						
						if filtered == 0 and firstrun == 0:
							msg = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', msg, flags=re.MULTILINE)				
							print('- '+tweet['user']['screen_name']+': '+msg)						
						
							vid=video(msg)
	
							try:
								response=api.upload_video(media=vid, media_type='video/mp4', media_category='tweet_video', check_progress=True)
								response=api.update_status(status='@'+tweet['user']['screen_name']+' '+str(tid), media_ids=[response['media_id']], in_reply_to_status_id=tid)								
								api.retweet(id=response['id'])
								alreadytweeted[tid]=1
								write_file('alreadytweeted.json',json.dumps(alreadytweeted))
								write_file(lastid_file,tid)
								tweetcount+=1
								time.sleep(vid_pause_time)
							except TwythonError as e:
								print("TweepyError: update_status: "+str(e))								
						
				except TwythonError as e:
					print("TwythonError: Timeline"+str(e))
				
				time.sleep(search_pause_time)
		
		if tweetcount == 0:
			write_file('alreadytweeted.json','{"1":1}')
		
		print(".",end="",flush=True)
		time.sleep(refresh_time)
	
if __name__ == "__main__":
	main()