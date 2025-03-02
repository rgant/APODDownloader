#!/usr/bin/env python
"""
Downloads the Astronomy Picture of the Day (http://apod.nasa.gov/apod), storing
it into a particular path using a sortable YYYYMMDD date string. Also removes
any pictures downloaded from a day more than 100 days ago.
"""
import datetime
import logging
import os
import re
import urllib.parse
import urllib.request


TODAY = datetime.date.today()
CHNG_DELTA = datetime.timedelta(days=1)
FILE_BASE = '/Users/rgant/Pictures/APOD'


def cleanup_old_files() -> datetime.date:
    """Clean up the older files, find the newest file."""

    # Get a list of the currently downloaded APODs
    file_list = os.listdir(FILE_BASE)

    cutoff_date = TODAY - CHNG_DELTA * 100
    cutoff_str = cutoff_date.strftime('%Y%m%d')

    # date string of the most recently downloaded file
    most_recent = ''

    for filename in file_list:
        # strip off the beginning date portion of the file name
        f_date = filename.partition('-')[0]

        # if this file is older than the cut off date, delete it
        # integer comparison works for sortable YYYYMMDD date strings.
        if f_date < cutoff_str:
            os.remove(os.path.join(FILE_BASE, filename))

        # find the most recent APOD date
        if f_date > most_recent and f_date > cutoff_str:
            most_recent = f_date

    # Convert the most recent APOD file date to a `datetime` object
    if most_recent:
        curr_date = datetime.date(
            int(most_recent[0:4]), int(most_recent[4:6]), int(most_recent[6:8])
        )
    else:
        curr_date = cutoff_date

    return curr_date


def get_latest_images(curr_date: datetime.date) -> None:
    """Download the APOD image for each day."""
    logger = logging.getLogger(__name__)
    url_base = 'http://apod.nasa.gov/apod'
    img_regex = re.compile(r'<a href="(image/[^"]+)', re.IGNORECASE | re.MULTILINE)

    # Starting from the day after the most recently downloaded APOD file until
    # today download the new APOD images.
    while curr_date < TODAY:
        # Step to next date
        curr_date += CHNG_DELTA

        # Formatted dates used for the APOD URL & when saving APOD file
        url_date_str = curr_date.strftime('%y%m%d')
        file_date_str = curr_date.strftime('%Y%m%d')

        # URL for the APOD page
        html_url = f'{url_base}/ap{url_date_str}.html'
        # Download the page into a string
        with urllib.request.urlopen(html_url) as response:
            html_pg = response.read().decode()

        # Search for the anchor tag to the big image
        match = img_regex.search(html_pg)
        if not match:
            continue  # Image URL not found, so skip this date

        img_url = urllib.parse.quote(match.group(1))
        img_file_nm = os.path.basename(img_url)
        request_url = f'{url_base}/{img_url}'
        out_path = f'{FILE_BASE}/{file_date_str}-{img_file_nm}'
        logger.info('REQUEST: %r', request_url)
        logger.info('OUTPUT: %r', out_path)
        urllib.request.urlretrieve(request_url, out_path)


def main() -> None:
    """
    First, cleanup old files in the FILE_BASE directory. Then download any new images from APOD
    website.
    """
    curr_date = cleanup_old_files()
    get_latest_images(curr_date)


if __name__ == '__main__':
    logging.basicConfig()#level=logging.INFO)
    main()
