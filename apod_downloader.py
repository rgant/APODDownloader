#!/usr/bin/python3
"""
Downloads the Astronomy Picture of the Day (https://apod.nasa.gov/apod), storing
it into a particular path using a sortable YYYYMMDD date string. Also removes
any pictures downloaded from a day more than 100 days ago.
"""
import codecs
import datetime
import http.client
import logging
import os
import re
import urllib.parse
import urllib.request
import urllib.error


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

    # APOD files are named `YYYYMMDD-...`; anything else in the directory (e.g. a
    # macOS .DS_Store) is ignored so it is never deleted or misread as a date.
    name_regex = re.compile(r'^(\d{8})-')

    for filename in file_list:
        name_match = name_regex.match(filename)
        if not name_match:
            continue
        f_date = name_match.group(1)

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


def _decode_html(raw: bytes) -> str:
    """
    Decode an APOD page to text, detecting the encoding from the bytes rather
    than the HTTP headers. The server reports ``charset=UTF-8`` even for pages
    saved as UTF-16, so the response content is the only trustworthy signal.

    APOD pages carry no ``<meta charset>``; they are UTF-8, or occasionally
    UTF-16 flagged by a byte-order mark. A leading BOM selects the encoding,
    otherwise the page is UTF-8.
    """
    if raw.startswith(codecs.BOM_UTF8):
        return raw.decode('utf-8-sig')
    if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        # ``utf-16`` reads the BOM to pick the endianness and strips it.
        return raw.decode('utf-16')

    # `errors='replace'` keeps one unexpected page from aborting the whole run;
    # the image link extracted downstream is pure ASCII and survives intact.
    return raw.decode('utf-8', errors='replace')


def get_latest_images(curr_date: datetime.date) -> None:
    """Download the APOD image for each day."""
    logger = logging.getLogger(__name__)
    url_base = 'https://apod.nasa.gov/apod'
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
        logger.info('PAGE: %r', html_url)
        # Download the page into a string
        response: http.client.HTTPResponse
        try:
            with urllib.request.urlopen(html_url) as response:
                html_pg = _decode_html(response.read())
        except urllib.error.URLError as e:
            # A page may be missing (e.g. today's is not posted yet) or the
            # network may hiccup; skip this date rather than abort the run.
            logger.warning('Page retrieval failed: %r', e)
            continue

        # Search for the anchor tag to the big image
        match = img_regex.search(html_pg)
        if not match:
            continue  # Image URL not found, so skip this date

        img_url = urllib.parse.quote(match.group(1))
        img_file_nm = os.path.basename(img_url)
        logger.info('REQUEST: %r', f'{url_base}/{img_url}')
        logger.info('OUTPUT: %r', f'{FILE_BASE}/{file_date_str}-{img_file_nm}')
        try:
            _ = urllib.request.urlretrieve(
                f'{url_base}/{img_url}',
                f'{FILE_BASE}/{file_date_str}-{img_file_nm}',
            )
        except urllib.error.HTTPError as e:
            logger.exception('Image retrieval failed: %r', e)


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
