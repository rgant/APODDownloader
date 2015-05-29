#!/usr/bin/python

import datetime, os, re, urllib

today = datetime.date.today()
chng_delta = datetime.timedelta(days=1)	# Step value for change in dates (one day)

# Get a list of the currently downloaded APODs
file_base = '/Users/rgant/Pictures/APOD'
file_list = os.listdir(file_base)

# Clean up the older files, find the newest file
cutoff_date= today - chng_delta * 100;	# 100 Days in the past. It would be better to do something like strtotime('100 days ago')
cutoff_str = cutoff_date.strftime('%Y%m%d')
# date string of the most recently downloaded file
most_recent = 0
for f in file_list:
	# strip off the beginning date portion of the file name
	f_date = f.partition('-')[0]

	# if this file is older than the cut off date, delete it
	if f_date < cutoff_str:	# integer comparison works for sortable YYYYMMDD date strings.
		os.remove( os.path.join(file_base, f) )

	# find the most recent APOD date
	if f_date > most_recent and f_date > cutoff_str:
		most_recent = f_date

# Convert the most recent APOD file date to a datetime object
if most_recent:
	curr_date = datetime.date( int(most_recent[0:4]), int(most_recent[4:6]), int(most_recent[6:8]) )
else:
	curr_date = cutoff_date

url_base = 'http://apod.nasa.gov/apod'
img_regex = re.compile('<a href="(image/[^"]+)', re.IGNORECASE | re.MULTILINE)

# Starting from the day after the most recently downloaded APOD file til today
# download the new APOD images.
while curr_date < today:
	# Step to next date
	curr_date += chng_delta

	# Formated dates used for the APOD URL & when saving APOD file
	url_date_str = curr_date.strftime('%y%m%d')
	file_date_str = curr_date.strftime('%Y%m%d')

	# URL for the APOD page
	html_url = url_base+'/ap'+url_date_str+'.html'
	# Download the page into a string
	html_pg = urllib.urlopen(html_url).read()

	# Search for the anchor tag to the big image
	m = img_regex.search(html_pg)
	if not m:
		continue	# Image URL not found, so skip this date

	img_url = m.group(1)
	img_file_nm = os.path.basename(img_url)
	urllib.urlretrieve(url_base+'/'+img_url, file_base+'/'+file_date_str+'-'+img_file_nm)
