from django.db import models
from asci_art import show_message
from log import log

def boolean_is_image(image_url):
    image_url = image_url.lower()

    if image_url.endswith('.jpg') or image_url.endswith('.png'):
        return True
    else:
        return False


def boolean_element_exists(browser, selector):
    try:
        if selector.startswith('//'):
            browser.find_element_by_xpath(selector)
        else:
            browser.find_element_by_class_name(selector)
        return True
    except:
        return False


def save_instagram_photos(browser):
    import time
    from dateutil.parser import parse
    from datetime import datetime

    log('save_instagram_photos(browser)')

    photos_processed=0

    # save photo
    while photos_processed==0 or boolean_element_exists(browser, 'HBoOv.coreSpriteRightPaginationArrow'):
        time.sleep(3)

        image_urls = browser.find_elements_by_class_name(
            'KL4Bh')[-1].find_elements_by_css_selector("*")[0].get_attribute('srcset').split(',')

        url_image = image_urls[-1].split(' ')[0]

        if Photo.objects.filter(url_image=url_image).exists() == False:
            try:
                text_post = browser.find_elements_by_class_name(
                    'C4VMK')[0].find_elements_by_css_selector("*")[2].text
            except:
                text_post = None
            Photo(
                text_description_en_US=text_post,
                url_image=url_image,
                url_post=browser.current_url,
                str_source='Instagram',
                int_UNIXtime_created=round(datetime.timestamp(parse(browser.find_elements_by_class_name(
                    '_1o9PC.Nzb55')[0].get_attribute("datetime"))))
            ).save()
            log('--> New photo saved')
        else:
            # end script, since photos aren't new
            log('--> Photo exists. Skipped...')

        photos_processed+=1

        if boolean_element_exists(browser, 'HBoOv.coreSpriteRightPaginationArrow'):
            # go to next photo
            browser.find_element_by_class_name(
                'HBoOv.coreSpriteRightPaginationArrow').click()


def save_twitter_photos(browser):
    import time
    log('save_twitter_photos(browser)')

    # get all image blocks
    images_boxes = browser.find_elements_by_css_selector(
        'div.AdaptiveMedia-photoContainer.js-adaptive-photo')

    no_images_found_counter = 0

    while len(images_boxes) > 0 and no_images_found_counter < 5:
        # if only one tweet remaining, load more via scroll loading
        while (len(images_boxes) == 1 or len(images_boxes) == 0) and no_images_found_counter < 5:
            browser.execute_script(
                "window.scrollTo(0, 0);")
            browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            images_boxes = browser.find_elements_by_css_selector(
                'div.AdaptiveMedia-photoContainer.js-adaptive-photo')

            if len(images_boxes) == 1 or len(images_boxes) == 0:
                no_images_found_counter += 1

        # get all children (images)
        children = images_boxes[0].find_elements_by_css_selector("*")
        try:
            int_UNIXtime = int(browser.find_elements_by_class_name(
                '_timestamp.js-short-timestamp')[0].get_attribute("data-time"))
        except:
            int_UNIXtime = None

        try:
            url_post = browser.find_elements_by_class_name(
                'tweet-timestamp.js-permalink.js-nav.js-tooltip')[0].get_attribute("href")
        except:
            url_post = None

        try:
            text_tweet = images_boxes[0].find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_class_name(
                'js-tweet-text-container').text
        except:
            text_tweet = None
        for child in children:
            url_image = child.get_attribute("src")

            if Photo.objects.filter(url_image=url_image).exists() == False:
                Photo(
                    text_description_en_US=text_tweet,
                    url_image=url_image,
                    url_post=url_post,
                    str_source='Twitter',
                    int_UNIXtime_created=int_UNIXtime,
                ).save()
                log('--> New photo saved')
            else:
                log('--> Photo exist. Skipped...')

        # delete tweet from timeline html
        browser.execute_script("""
        document.getElementsByClassName(
            'js-stream-item stream-item stream-item')[0].outerHTML=''
        """)

        images_boxes = browser.find_elements_by_css_selector(
            'div.AdaptiveMedia-photoContainer.js-adaptive-photo')

    log('--> Finished!!')


def save_wiki_photo(photo):
    from _database.models.meetingnotes import startChrome
    from dateutil.parser import parse
    from datetime import datetime
    from config import Config

    if not Config('BASICS.WIKI.API_URL').value:
        log('--> BASICS.WIKI.API_URL not found in config.json -> BASICS - Please add your WIKI_API_URL first.')
        return

    if boolean_is_image(photo['url']) == True:
        # open url in selenium, test if image is on blocked list, else save low resolution image url
        browser = startChrome(True, photo['descriptionurl'])
        save_image = True
        try:
            pages_with_image = browser.find_element_by_id(
                'mw-imagepage-section-linkstoimage').text.split('\n', 1)[1]
            for blocked_page in Config('BASICS.WIKI.PHOTOS_IGNORE_PAGES').value:
                if blocked_page in pages_with_image:
                    save_image = False
                    break
        except:
            print(
                'LOG: --> mw-imagepage-section-linkstoimage not found - coudlnt check if image url is blocked')

        if save_image == False:
            log('--> Skipped photo. URL on WIKI.PHOTOS_IGNORE_PAGES list')

        elif Photo.objects.filter(url_post=photo['descriptionurl']).exists() == True:
            log('--> Skipped photo. Already exists.')
            browser.close()
            return 'Skipped'

        else:
            try:
                url_image = browser.find_element_by_class_name(
                    'mw-thumbnail-link').get_attribute('href')
            except:
                url_image = photo['url']

            Photo(
                text_description_en_US=photo['canonicaltitle'] if 'canonicaltitle' in photo else None,
                url_image=url_image,
                url_post=photo['descriptionurl'],
                str_source='Wiki',
                int_UNIXtime_created=round(
                    datetime.timestamp(parse(photo['timestamp']))),
            ).save()
            log('--> New photo saved')
            browser.close()

            return 'Saved'

        


class PhotoSet(models.QuerySet):
    def count_overview(self):
        return {
            'total': self.count(),
            'Wiki': self.filter(str_source='Wiki').count(),
            'Twitter': self.filter(str_source='Twitter').count(),
            'Instagram': self.filter(str_source='Instagram').count(),
            'Flickr': self.filter(str_source='Flickr').count(),
        }

    def random(self, num_results=30):
        import random
        # get random numbers to show random results
        random_set = []
        maximum = self.count()
        while len(random_set) < num_results:
            random_number = random.randint(0, maximum)
            while random_number in random_set:
                random_number = random.randint(0, maximum)
            random_set.append(random_number)

        random_results = []
        for number in random_set:
            random_results.append(self.all()[number])

        return random_results

    def latest(self):
        return self.order_by('-int_UNIXtime_created')

    def oldest(self):
        return self.order_by('int_UNIXtime_created')

    def import_from_google_photos(self):
        log('import_from_google_photos()')
        GooglePhotos().import_photos()

    def import_from_twitter(self):
        log('import_from_twitter()')
        from _database.models.meetingnotes import startChrome
        import time
        import requests
        from config import Config

        # check if twitter is saved in social channels
        for entry in Config('SOCIAL.SOCIAL_NETWORKS').value:
            if 'twitter.com/' in entry['url']:
                show_message(
                    '✅ Found Twitter in SOCIAL.SOCIAL_NETWORKS - Start importing photos from your Twitter page ...')
                time.sleep(2)
                if requests.get(entry['url']).status_code == 200:
                    browser = startChrome(True, entry['url']+'/media')
                else:
                    show_message(
                        'WARNING: I can\'t access your Twitter page. Is the URL correct? Will skip importing photos from Twitter for now.')
                    time.sleep(4)
                    return
                break
        else:
            show_message(
                'WARNING: Can\'t find Twitter in SOCIAL.SOCIAL_NETWORKS in your config.json. Will skip importing photos from Twitter for now.')
            time.sleep(4)
            return

        save_twitter_photos(browser)

    def import_from_twitter_hashtag(self):
        log('import_from_twitter_hashtag()')
        from _database.models.meetingnotes import startChrome
        import time
        import requests
        from config import Config

        # check if hastag exists
        HASHTAG = Config('SOCIAL.HASHTAG').value

        # check if instagram tag is saved in settings
        if HASHTAG:
            show_message(
                '✅ Found SOCIAL.HASHTAG - Start importing photos from Twitter with your hashtag ...')
            time.sleep(2)
            if requests.get('https://twitter.com/hashtag/{}?f=image'.format(HASHTAG.split('#')[1])).status_code == 200:
                browser = startChrome(
                    True, 'https://twitter.com/hashtag/{}?f=image'.format(HASHTAG.split('#')[1]))
            else:
                show_message(
                    'WARNING: I can\'t access your SOCIAL.HASHTAG on Twitter. Is the hashtag correct? Will skip importing photos from Twitter with your hashtag for now.')
                time.sleep(4)
                return
        else:
            show_message(
                'WARNING: Can\'t find SOCIAL.HASHTAG in your config.json. Will skip importing photos from Twitter with your hashtag for now.')
            time.sleep(4)
            return

        save_twitter_photos(browser)

    def import_from_wiki(self):
        # API documentation: https://www.mediawiki.org/wiki/API:Allimages
        log('import_from_wiki()')
        from config import Config
        import requests
        import time

        WIKI_API_URL = Config('BASICS.WIKI.API_URL').value

        if WIKI_API_URL:
            show_message(
                '✅ Found BASICS.WIKI.API_URL - Start importing photos from your Wiki ...')
            time.sleep(2)
            if requests.get(WIKI_API_URL).status_code != 200:
                show_message(
                    'WARNING: I can\'t access your Wiki. Is the API_URL correct? Will skip importing photos from your Wiki for now.')
                time.sleep(4)
                return
        else:
            show_message(
                'WARNING: Can\'t find BASICS.WIKI.API_URL in your config.json. Will skip importing photos from your Wiki for now.')
            time.sleep(4)
            return

        parameter = {
            'action': 'query',
            'format': 'json',
            'list': 'allimages',
            'list': 'allimages',
            'aisort': 'timestamp',
            'aidir': 'descending',
            'ailimit': '500',
            'aiminsize': '50000',  # minimum 50kb size, to filter out small logos/icons
            'aiprop': 'timestamp|canonicaltitle|url|user'
        }
        response_json = requests.get(WIKI_API_URL, params=parameter).json()

        skipped_photos_counter=0

        # for every photo...
        for photo in response_json['query']['allimages']:
            if skipped_photos_counter<5:
                status = save_wiki_photo(photo)
                if status=='Skipped':
                    skipped_photos_counter+=1

        while 'continue' in response_json and 'aicontinue' in response_json['continue'] and skipped_photos_counter < 5:
            response_json = requests.get(
                WIKI_API_URL, params={**parameter, **{'aicontinue': response_json['continue']['aicontinue']}}).json()

            for photo in response_json['query']['allimages']:
                status = save_wiki_photo(photo)
                if status=='Skipped':
                    skipped_photos_counter+=1

        if skipped_photos_counter>=5:
            log('No new photos it seems.')

        log('Complete! All photos processed! Now {} photos'.format(
            Photo.objects.count()))


    def import_from_flickr(self):
        log('import_from_flickr()')
        from _database.models.meetingnotes import startChrome
        import time
        from dateutil.parser import parse
        from datetime import datetime
        from config import Config
        import requests

        FLICKR_URL = Config('SOCIAL.FLICKR_URL').value

        # check if instagram tag is saved in settings
        if FLICKR_URL:
            show_message(
                '✅ Found SOCIAL.FLICKR_URL - Start importing photos from Flickr ...')
            time.sleep(2)

            if requests.get(FLICKR_URL).status_code == 200:
                browser = startChrome(True, FLICKR_URL)
            else:
                show_message(
                    'WARNING: I can\'t access your FLICKR_URL. Is the URL correct? Will skip importing photos from Flickr for now.')
                time.sleep(4)
                return
        else:
            show_message(
                'WARNING: Can\'t find SOCIAL.FLICKR_URL in your config.json. Will skip importing photos from Flickr for now.')
            time.sleep(4)
            return

        processed_images = 0

        time.sleep(5)
        no_images_found_counter = 0

        while boolean_element_exists(browser, 'view.photo-list-photo-view.awake') == True or no_images_found_counter < 5:
            # if no photo found... click "load more" button if exists, else scroll down and wait
            if boolean_element_exists(browser, 'view.photo-list-photo-view.awake') == False:
                while boolean_element_exists(browser, 'view.photo-list-photo-view.awake') == False:
                    # see if load more button exists
                    if boolean_element_exists(browser, 'infinite-scroll-load-more') == True:
                        browser.find_element_by_class_name(
                            'infinite-scroll-load-more').click()
                    else:
                        # else scroll down
                        browser.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);")

                    time.sleep(5)

                    no_images_found_counter += 1
                    if no_images_found_counter == 5:
                        log('--> No more images left. Exit code.')
                        exit()

            # get the first image
            photo = browser.find_elements_by_class_name(
                'view.photo-list-photo-view.awake')[0]

            # get image url, name and post url
            url_image = 'https://' + \
                photo.get_attribute("style").split('url("//')[1].split('"')[0]
            str_titel = photo.find_elements_by_css_selector("*")[0].find_elements_by_css_selector(
                "*")[0].find_elements_by_css_selector("*")[0].get_attribute('aria-label')
            url_post = photo.find_elements_by_css_selector("*")[0].find_elements_by_css_selector(
                "*")[0].find_elements_by_css_selector("*")[0].get_attribute('href')

            if Photo.objects.filter(url_post=url_post).exists() == False:
                # open photo in new tab, switch to new tab, get created date, close tab & switch to previous tab
                new_window = startChrome(True, url_post)
                int_UNIXtime = round(datetime.timestamp(parse(new_window.find_element_by_class_name(
                    'date-taken-label').text.split('on ')[1])))
                new_window.close()

                # save photo
                Photo(
                    text_description_en_US=url_post,
                    url_image=url_image,
                    url_post=url_post,
                    str_source='Flickr',
                    int_UNIXtime_created=int_UNIXtime,
                ).save()
                log('--> New photo saved')
            else:
                log('--> Photo exist. Skipped...')

            # delete image from feed and go to next one
            browser.execute_script("""
            document.getElementsByClassName(
                'view photo-list-photo-view awake')[0].outerHTML=''
            """)

            processed_images += 1
            log('-> processed_images: '+str(processed_images))


class Photo(models.Model):
    objects = PhotoSet.as_manager()
    text_description_en_US = models.TextField(
        blank=True, null=True, verbose_name='Description en-US')
    text_description_he_IL = models.TextField(
        blank=True, null=True, verbose_name='Description he-IL')
    url_image = models.URLField(
        max_length=250, blank=True, null=True, verbose_name='Image URL')
    url_post = models.URLField(
        max_length=250, blank=True, null=True, verbose_name='Post URL')
    str_source = models.CharField(
        max_length=250, blank=True, null=True, verbose_name='Source')
    int_UNIXtime_created = models.IntegerField(blank=True, null=True)
    int_UNIXtime_updated = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.url_image

    @property
    def str_relative_time(self):
        log('photo.str_relative_time')
        import time
        from datetime import datetime

        timestamp = self.int_UNIXtime_created

        # in last 60 minutes
        if timestamp >= time.time()-(60*60):
            minutes_in_past = int((time.time()-timestamp)/60)
            log('--> return STR')
            return str(minutes_in_past)+' minute'+('s' if minutes_in_past > 1 else '')+' ago'

        # in last 24 hours
        elif timestamp >= time.time()-(60*60*24):
            hours_in_past = int(((time.time()-timestamp)/60)/60)
            log('--> return STR')
            return str(hours_in_past)+' hour'+('s' if hours_in_past > 1 else '')+' ago'

        # else if in last 6 days, return number of days ago
        elif timestamp >= time.time()-(60*60*24*6):
            days_in_past = int((((time.time()-timestamp)/60)/60)/24)
            log('--> return STR')
            return str(days_in_past)+' day'+('s' if days_in_past > 1 else '')+' ago'

        # else date string
        else:
            log('--> return STR')
            return datetime.utcfromtimestamp(timestamp).strftime('%b %d, %Y')
