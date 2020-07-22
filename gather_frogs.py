#!ve/bin/python3

# TODO update get_all_post_urls() FIRST_POST_ID var to the most recent post processed
# TODO make an exclusion list with non-name related posts
# TODO some names return as "You" or blank
# TODO posts with multiple names only return the first name
# TODO remove Time Posted? if not, change "None" values to blanks

from selenium import webdriver
import time
import requests
import lxml.html


def get_all_post_urls():
    PROFILE_URL = 'https://www.instagram.com/what_frog_you_are/'
    FIRST_POST_ID = '/p/CCaP08OJm2J/'
    CSS_SELECTOR__PHOTO_ROW = f'#react-root > section > main > div > div:nth-child(4) > article > div > div > div'
    CSS_SELECTOR__POST_URL = f'{CSS_SELECTOR__PHOTO_ROW} > div > a'
    CSS_SELECTOR__FIRST_POST = f'{CSS_SELECTOR__PHOTO_ROW}:last-child > div > a[href*="{FIRST_POST_ID}"]'

    driver = webdriver.Chrome()
    driver.get(PROFILE_URL)

    urls = []
    is_bottom = False

    while not is_bottom:
        posts = driver.find_elements_by_css_selector(CSS_SELECTOR__POST_URL)

        # TODO list comprehension
        for p in posts:
            urls.append(p.get_attribute('href'))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        try:
            driver.find_element_by_css_selector(CSS_SELECTOR__FIRST_POST)
            is_bottom = True
            driver.quit()
        except Exception as e:
            pass

    unique_urls = list(set(urls))
    return unique_urls


def get_fields_from_meta(response):
    tree = lxml.html.fromstring(response)
    meta_tags = tree.cssselect('meta')

    meta1 = meta_tags[7].values()[0]
    name = meta1.split('“')[1].split(' ')[0]

    meta2 = meta_tags[9].values()[1]
    dt = meta2.split(' • ')[1]
    date, timestamp = dt.split(' at ')

    return name, date, timestamp


def get_fields_from_response_text(response):
    tree = lxml.html.fromstring(response)

    name = tree.cssselect('title')[0].text_content()
    name = name.replace('You are a Frog on Instagram: “', '')
    name = name.split(' ')[0]

    date_start = response.find('accessibility_caption') + 51
    substr = response[date_start:]
    if substr.startswith('rog on '):
        substr = substr[7:]
        date_end = substr.find(' tagging')
    else:
        date_end = substr.find('.')
    date = substr[:date_end]

    return name, date, None


def get_media_id(response):
    s_id_term = 'GraphImage'
    e_id_term = '","shortcode'
    s_id = response.find(s_id_term) + 18
    e_id = response.find(e_id_term)
    return response[s_id:e_id]


def main():
    unique_urls = get_all_post_urls()

    # header row
    print('"Name (1st shown in post)"\t"Date Posted"\t"Time Posted (If Available)"\t"URL"\t"Instagram Media ID"')

    for i, u in enumerate(unique_urls):
        try:
            response = requests.get(u).text

            try:
                name, date, timestamp = get_fields_from_meta(response)
            except Exception as e:
                name, date, timestamp = get_fields_from_response_text(response)

            media_id = get_media_id(response)
            print(f'{name}\t{date}\t{timestamp}\t{u}\t{media_id}')

            if i != 0 and i % 15 == 0:
                time.sleep(10)

        except Exception as e:
            print(e)
            print(f'ERROR parsing {u}')
            return


if __name__ == '__main__':
    main()
