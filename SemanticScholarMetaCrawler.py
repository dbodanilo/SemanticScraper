from json import loads
from locale import LC_ALL,setlocale,format_string
from re import sub
from typing import List, Set
from requests import get

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import Gerenciador

from Artigo import Artigo
from Autor import Autor
# import Autor
# import Artigo
import os
import platform
import ExcelExporter
import sys
import Timer


class Crawler:
    def __init__(self, root_directory):
        # increase the recursion limit to handle very large searches
        sys.setrecursionlimit(5000)

        # options handler for Google Chrome
        self.options = Options()

        # saves current directory in a string
        self.root_directory = root_directory

        # saves current platform in a string
        self.current_platform = platform.system()

        self.directory_chromedriver = ''
        if self.current_platform == 'Darwin':
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverMac')
        elif self.current_platform == 'Windows':
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverWin.exe')
        else:
            self.directory_chromedriver = os.path.join(self.root_directory, 'ChromeDriver', 'ChromeDriverLin')

        # sets Chrome to run Headless (without showing the navigator window while running)
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--start-maximized")
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')

        #self.options.binary_location = "C:\\Path\\To\\Chrome"

        self.start_time = Timer.timeNow()
        self.end_time = Timer.timeNow()

        self.manager = None
        self.list_authors: List[Autor] = []
        self.list_articles: List[Artigo] = []

        self.input_search = ''
        self.input_pages = 0

        self.gui = None

        self.index_progress_bar = 1

    def update_search_parameters(self, input_search, input_pages):
        self.input_search = input_search
        self.input_pages = input_pages

    # extract the type of the article from the BibText cite text and returns it as a single word string
    def return_type_cite(self, string_cite):
        list_cite = string_cite.split('{')
        type_cite = list_cite[0][1:]
        return type_cite

    def start_search(self):
        self.start_time = Timer.timeNow()

        setlocale(LC_ALL, "pt_BR")

        # loads files for the inputted search if they exist, otherwise, the files are created
        self.manager = Gerenciador.Gerenciador(self.input_search, self.root_directory)
        self.list_authors = self.manager.loadAutores()
        self.list_articles = self.manager.loadArtigos()

        # creates a webdriver instance
        # driver = webdriver.Chrome(self.directory_chromedriver, chrome_options=self.options)

        # runs the following code 3 times, one for each type os search
        # for k in range(0, 2):
        # label gui
        self.gui.app.queueFunction(self.gui.app.setLabel, 'progress_bar_label', 'Crawling with '
                                    + str(1) + '/1 parameter...')
                                    # + str(k+1) + '/3 parameter...')
        self.gui.app.queueFunction(self.gui.app.setMeter, 'progress_bar', 0)


        # access switched to api calls,
        # no need to access main page
        # get('http://api.semanticscholar.org/')
        # access Semantic Scholar main page
        # driver.get('https://www.semanticscholar.org/')

        # waits for the page to load, searching for the Field of Study filter to be enabled
        # try:
        #     waitelement = WebDriverWait(driver, 20). \
        #         until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Search text']")))
        # except TimeoutError:
        #     print("~~~~ PAGE DID NOT LOAD! ~~~~")

        # dismiss the popup that asks to allow cookies, if it shows up
        # try:
        #     driver.find_element_by_xpath(
        #         "//div[@class='copyright-banner__dismiss-btn button button--secondary']").click()
        # except:
        #     pass

        # input now sent directly via request url,
        # with extra whitespace striped
        _search_query = sub(r"\s+", " ", self.input_search.strip())
        _article_count = self.input_pages
        _articles_query_params = {
            "query": _search_query,
            "fields": "abstract,authors,citationCount,citationStyles,title,url,venue,year",
            "offset": 0,
            "limit": _article_count
        }

        # TODO: model expected JSON object types
        # e.g., search :: String -> [Paper] 
        # Paper :: { title: String, Author: Author, ...}
        _articles_endpoint = 'https://api.semanticscholar.org/graph/v1/paper/search'
        _articles_res = get(_articles_endpoint, params=_articles_query_params).json()

        # input the desired search phrase in the input box and hits ENTER
        # driver.find_element_by_name('q').send_keys(self.input_search)
        # driver.find_element_by_name('q').send_keys(Keys.ENTER)

        # waits for the page to load. It happens when the number of results is shown
        # try:
        #     waitelement = WebDriverWait(driver, 20). \
        #         until(EC.presence_of_element_located(
        #         (By.XPATH, "//div[@class='dropdown-filters__result-count']")))
        # except TimeoutError:
        #     print("~~~~ PAGE DID NOT LOAD! ~~~~")

        # Check all the filters in menu
        # filters = driver.find_elements_by_xpath("//button[@class='cl-button cl-button--no-arrow-divider cl-button--not-icon-only cl-button--no-icon cl-button--has-label cl-button--font-size- cl-button--icon-pos-left cl-button--shape-rectangle cl-button--size-default cl-button--type-default cl-button--density-default cl-dropdown-button']")
        # date_filter = None
        # type_filter = None
        # for f in filters:
        #     if f.text == "Date Range":
        #         date_filter = f
        #     elif f.text == "Publication Type":
        #         type_filter = f

        # search for now happens only once
        # TODO: mimic the old behavior,
        # i.e., searching with different filters applied

        # tests which type of search has been done and sets the correct one
        # if k == 1:  # results from the last five years
            # date_filter.click()
            # element = driver.find_element_by_xpath(
            #     "//button[@data-selenium-selector='last-five-years-filter-button']")
            # driver.execute_script('arguments[0].click()', element)
            # driver.find_element_by_xpath(
            #     "//div[@class='flex-container flex-row-vcenter dropdown-filters__outer-flex-container']").click()
        # elif k == 2:  # results with Reviews marked
            # type_filter.click()
            # driver.find_element_by_xpath("//*[contains(text(), 'Review (')]").click()
            # driver.find_element_by_xpath(
            #     "//div[@class='flex-container flex-row-vcenter dropdown-filters__outer-flex-container']").click()
        # else:
        #     pass

        # runs the code for the amount of pages desired
        self.index_progress_bar = 1
        self.list_articles = set(self.list_articles)

        # no need for pagination yet,
        # as number of articles is explicitly set,
        # in API request.
        # for pag in range(0, self.input_pages):
            # progress bar
            # self.gui.app.queueFunction(self.gui.app.setMeter, 'progress_bar',
            #                             (100 * self.index_progress_bar)/self.input_pages)

            # self.index_progress_bar += 1

            # # waits for the page to load
            # while True:
            #     try:
            #         element = driver.find_element_by_xpath("//div[@class='result-page is-filtering']")
            #     except:
            #         break

            # searches for the articles in the page and saves them in a list
            # list_articles_in_page = driver.find_elements_by_xpath("//div[@class='cl-paper-row serp-papers__paper-row paper-row-normal']")

        # now iterates over articles from API response
        for item in _articles_res["data"]:
        # iterates over each article in the articles list
        # for item in list_articles_in_page:

            # now takes it directly from JSON
            # saves the article title as a string
            title = item["title"]
            # title = item.find_element_by_xpath(".//a[@data-selenium-selector='title-link']").text

            # now authors field is present in API response
            _paper_authors = item["authors"]
            # saves all authors with a html link to their pages in a list
            # list_authors_html_link = item.find_elements_by_xpath(
                # ".//a[@class='cl-paper-authors__author-link']")

            # saves all authors without a html link to their pages in a list
            # list_authors_without_html_link = None
            # try:
            #     list_authors_without_html_link = item.find_elements_by_xpath(
            #         ".//span[@class='author-list__author-name']")
            # except:
            #     pass

            # creates a set list of the authors for the article
            list_authors_in_article: Set[Autor] = set()

            self.list_authors = set(self.list_authors)

            # iterates over each author in the list.
            for temp in _paper_authors:
            # iterates over each author in the list with html link
            # for temp in list_authors_html_link:

                # author name now comes in "name" field
                name = temp["name"]
                # saves the author name as a string
                # author = temp.text

                # no link comes with author from Papers API
                # TODO: fetch their link somehow.
                link = None
                # saves the author page html link as a string
                # link = temp.get_attribute('href')

                # creates temporary author
                author = Autor(name, link)

                # adds new authors to the set lists
                self.list_authors.add(author)
                list_authors_in_article.add(author)

            # no more distinction between:
            # authors with and without link.
            # iterates over each author in the list without html link, if the list is not empty
            # if list_authors_without_html_link is not None:
            #     for temp in list_authors_without_html_link:
            #         # saves the author name as a string
            #         author = temp.text

            #         # creates temporary author
            #         temp = Autor.Autor(author, None)

            #         # adds new authors to the set lists
            #         self.list_authors.add(temp)
            #         list_authors_in_article.add(temp)

            self.list_authors = list(self.list_authors)
            self.list_authors.sort()
            list_authors_in_article: List[Autor] = list(list_authors_in_article)
            list_authors_in_article.sort()

            # origin comes as "venue" in API response.
            origin = item["venue"]
            # saves the article origin as a string
            # origin = '-'
            # try:
            #     origin = item.find_element_by_xpath(".//span[@data-selenium-selector='venue-metadata']").text
            # except:
            #     pass

            # date comes as "year" in API response.
            _year = item["year"]
            # TODO: log when field comes empty,
            # print paper id, field name and its value.
            date = str(_year) if _year else "0"
            # saves the article date as a string
            # date = '0'
            # try:
            #     full_date = item.find_element_by_xpath(".//span[@class='cl-paper-pubdates']").text
            #     date = full_date.split()[-1]
            # except:
            #     pass

            # citationCount comes as a number in API response.
            _citationCount = item["citationCount"]
            citationCount = format_string("%d", int(_citationCount), grouping=True) if _citationCount else "0"
            # saves the article total citations as a string
            # citations = '0'
            # try:
            #     citations = item.find_element_by_xpath(
            #         ".//div[@data-selenium-selector='total-citations-stat']").text
            #     citations = citations.replace(',', '')
            #     citations = citations.replace('.', '')
            # except:
            #     pass

            # link comes as "url" in API response.
            link = item["url"]
            # saves the article html link as a string
            # link = '-'
            # try:
            #     link = item.find_element_by_xpath(".//a[@class='flex-row cl-paper-view-paper']")\
            #         .get_attribute('href')
            # except:
            #     pass

            # currently no type comes in API response.
            _citationStyles = item["citationStyles"]
            bibtex = _citationStyles["bibtex"] if _citationStyles else "-"
            cite = self.return_type_cite(bibtex)
            # saves the article type as a string
            # bibtex = '-'
            # cite = '-'
            # try:
            #     item.find_element_by_xpath(".//button[@data-selenium-selector='cite-link']").click()
            #     try:
            #         waitelement = WebDriverWait(driver, 20). \
            #             until(EC.presence_of_element_located(
            #             (By.XPATH, "//cite[@class='formatted-citation formatted-citation--style-bibtex']")))
            #     except TimeoutError:
            #         print("~~~~ PAGE DID NOT LOAD! ~~~~")

            #     cite = driver.find_element_by_xpath(
            #         "//cite[@class='formatted-citation formatted-citation--style-bibtex']").get_attribute('textContent')
            #     driver.find_element_by_xpath(
            #         "//cite[@class='formatted-citation formatted-citation--style-bibtex']").send_keys(
            #         Keys.ESCAPE)
            #     bibtex = cite
            #     cite = self.return_type_cite(cite)
            # except:
            #     pass

            # synopsis comes as "abstract" in API response.
            synopsis = item["abstract"]
            # saves the article synopsis as a string
            # synopsis = 'No synopsis'
            # try:
            #     element = item.find_element_by_xpath(".//div[@class='tldr-abstract-replacement text-truncator']")
            #     synopsis = element.text.replace(" Expand", "")
            #     synopsis = synopsis.replace("TLDR\n", "")
            # except:
            #     pass

            # creates a new instance of a Article object
            new_article = Artigo(title, list_authors_in_article, origin, date,
                                        citationCount, link, cite, bibtex, synopsis)

            # adds new article to set list (set list does not allow duplicates)
            before = len(self.list_articles)
            self.list_articles.add(new_article)
            after = len(self.list_articles)

            # add article to the author's article list if the article is not repeated
            if before is not after:
                for autorTemp in list_authors_in_article:
                    autorTemp.addArtigo(new_article)

            # no need to switch pages when using API.
            # TODO: add pagination to API calls.
            # tries to go to the next page, if exists
            # try:
            #     element = driver.find_element_by_xpath("//button[@data-selenium-selector='next-page']")
            #     driver.execute_script('arguments[0].click()', element)
            # except:
            #     print("SUBJECT HAS NO MORE SEARCH PAGES!")
            #     break

        self.end_time = Timer.timeNow()

        # converts set to list, to be able to sort it after
        self.list_articles = list(self.list_articles)

        # closes the Google Chrome
        # driver.quit()

        # saves the list of articles and authors as .pkl files
        self.manager.saveArtigos(self.list_articles)
        self.manager.saveAutores(self.list_authors)

        self.gui.show_search_done_alert(Timer.totalTime(self.start_time, self.end_time), str(len(self.list_articles)))

    def saves_excel(self, parameter):
        # creates the excel file
        os.chdir(self.root_directory)
        excelExporter = ExcelExporter.ExcelExporter(self.input_search, self.gui.single_or_merge, self.root_directory)
        excelExporter.gui = self.gui
        excelExporter.order_type(parameter)
