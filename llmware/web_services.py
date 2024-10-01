
# Copyright 2023-2024 llmware

# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.


""" The web_services module implements classes to enable integrated access to popular web services within
LLMWare pipelines. """


import logging
import os
import shutil


from llmware.exceptions import LLMWareException
from llmware.configs import LLMWareConfig

logger = logging.getLogger(__name__)


class WikiKnowledgeBase:

    """ WikiKnowledgeBase implements Wikipedia API """

    def __init__(self):

        # importing here to suppress log warnings produced by urllib3
        import urllib3
        urllib3.disable_warnings()

        self.user_agent = "Examples/3.0"

        try:
            from wikipediaapi import Wikipedia, ExtractFormat
        except ImportError:
            raise LLMWareException(message="Exception: pip install `wikipediaapi` required.")

        self.wiki = Wikipedia(user_agent=self.user_agent, extract_format=ExtractFormat.WIKI, verify=False)
        self.wiki_search_api_url = 'http://en.wikipedia.org/w/api.php'

    def get_article(self, article_name):

        """ Retrieves a Wikipedia article by name. """

        article_response = {"title": "", "summary": "", "text": ""}

        try:
            page_py = self.wiki.page(article_name)

            if page_py.exists():

                logger.info(f"update: page_py - {page_py.title} - {page_py.summary}")
                logger.info(f"update: text - {page_py.text}")

                article_response = {"title": page_py.title, "summary": page_py.summary, "text": page_py.text}

            else:
                logger.info(f"update: connected with Wikipedia - selected article does not exist - "
                            f"{article_name}")

        except:
            logger.error(f"error: could not retrieve wikipedia article - please try again")

        return article_response

    def search_wikipedia(self, query, result_count=10, suggestion=False):

        """ Searches Wikipedia database API with a search 'topic' query. """

        # output result
        output = []

        # search params passed to the wikipedia api
        search_params = {'list': 'search', 'srprop': '', 'srlimit': result_count, 'srsearch': query,
                         'format': 'json', 'action': 'query'}

        if suggestion: search_params['srinfo'] = 'suggestion'

        headers = {'User-Agent': self.user_agent}

        try:
            import requests
            r = requests.get(self.wiki_search_api_url, params=search_params, headers=headers, verify=False)

            for i, title in enumerate(r.json()["query"]["search"]):

                logger.info(f"update:  wiki results - {i} - {title}")

                new_entry = {"num": i, "title": title["title"], "pageid": title["pageid"]}
                output.append(new_entry)

        except:
            logger.error("error: could not connect with Wikipedia to retrieve search results")

        return output


class YFinance:

    """ YFinance class implements the Yahoo Finance API. """

    def __init__(self, ticker=None):

        """
        Widely used Yahoo Finance API - key object = "
        TickerObj = yahooFinance.Ticker("META")
        print("All Info : ", TickerObj.info)
        for keys, values in TickerObj.info.items():
            print("keys: ", keys, values)

        # display Company Sector
        print("Company Sector : ", TickerObj.info['sector'])

        # display Price Earnings Ratio
        print("Price Earnings Ratio : ", TickerObj.info['trailingPE'])

        # display Company Beta
        print(" Company Beta : ", TickerObj.info['beta'])
        print(" Financials : ", TickerObj.get_financials())
        """

        self.company_info = None

        self.financial_summary_keys = ["shortName", "symbol","marketCap", "totalRevenue", "ebitda", "revenueGrowth", "grossMargins",
                                   "freeCashflow", "priceToSalesTrailing12Months", "grossMargins","currency"]

        self.stock_summary_keys = ["shortName", "symbol", "exchange","bid", "ask", "fiftyTwoWeekLow", "fiftyTwoWeekHigh", "symbol",
                                   "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice",
                                   "returnOnAssets", "returnOnEquity", "trailingPE", "forwardPE", "volume",
                                   "forwardEps", "pegRatio", "currency"]

        self.risk_summary_keys = ["shortName","symbol", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk", "overallRisk",
                                  "shortName", "longBusinessSummary"]

        self.company_summary_keys = ["shortName", "longName", "symbol", "marketCap", "companyOfficers", "website",
                                     "industry", "sector", "longBusinessSummary", "fullTimeEmployees"]

        self.keys = ["address1", "city", "state", "zip", "country", "phone","website","industry",
                     "industryDisp", "sector", "sectorDisp", "longBusinessSummary", "fullTimeEmployees",
                     "companyOfficers", "auditRisk", "boardRisk", "compensationRisk", "shareHolderRightsRisk",
                     "overallRisk", "previousClose", "open", "dayLow", "dayHigh", "regularMarketPreviousClose",
                     "regularMarketOpen", "regularMarketDayLow", "regularMarketDayHigh", "payoutRatio", "beta",
                     "trailingPE", "forwardPE", "volume", "regularMarketVolume", "averageVolume",
                     "averageVolume10days", "bid", "ask", "bidSize", "askSize", "marketCap", "fiftyTwoWeekLow",
                     "fiftyTwoWeekHigh", "priceToSalesTrailing12Months", "fiftyDayAverage", "twoHundredDayAverage",
                     "trailingAnnualDividendRate", "trailingAnnualDividendYield", "currency", "enterpriseValue",
                     "profitMargins", "floatShares", "sharesOutstanding", "sharesShort", "sharesShortPriorMonth",
                     "sharesShortPreviousMonthDate", "dateShortInterest", "sharesPercentSharesOut",
                     "heldPercentInsiders", "heldPercentInstitutions", "shortRatio", "shortPercentOfFloat",
                     "impliedSharesOutstanding", "bookValue", "priceToBook", "lastFiscalYearEnd",
                     "nextFiscalYearEnd", "mostRecentQuarter", "earningsPerQuarterlyGrowth", "netIncomeToCommon",
                     "trailingEps", "forwardEps", "pegRatio", "enterpriseToRevenue", "enterpriseToEbitda",
                     "52WeekChange", "SandP52WeekChange", "exchange", "quoteType", "symbol", "underlyingSymbol",
                     "shortName", "longName", "currentPrice", "targetHighPrice", "targetLowPrice", "targetMeanPrice",
                     "targetMedianPrice", "recommendationMean", "recommendationKey", "numberOfAnalystOpinions",
                     "totalCash", "totalCashPerShare", "ebitda", "totalDebt", "quickRatio", "currentRatio",
                     "totalRevenue", "debtToEquity", "revenuePerShare", "returnOnAssets" "returnOnEquity", "grossProfits",
                     "freeCashflow", "operatingCashflow", "earningsGrowth", "revenueGrowth", "grossMargins",
                     "ebitdaMargins", "operatingMargins", "financialCurrency", "trailingPegRatio"]

        try:
            import yfinance
        except ImportError or ModuleNotFoundError:
            raise LLMWareException(message="Exception: YFinance library not installed - "
                                           "fix with `pip3 install yfinance`")

        self.ticker = None

        if ticker:

            self.ticker = self._prep_ticker(ticker)

            try:
                self.company_info = yfinance.Ticker(self.ticker)
            except:
                logger.warning(f"YFinance - attempted to retrieve company info based on ticker lookup with "
                               f"ticker - {self.ticker} - and did not succeed.  Please check the ticker.")

        else:
            self.company_info = None

    def _prep_ticker(self, ticker):

        """ Yfinance API is particular about the ticker format, so a little prep handling to
        maximize likelihood of positive response. """

        #   if ticker includes exchange (often used in formal formats of exchange), then strip
        ticker_core = ticker.split(":")[-1]

        #   check that all characters are alpha
        ticker_remediated = ""
        for letters in ticker_core:
            if 97 <= ord(letters) <= 122:
                cap_letter = chr(ord(letters)-32)
                ticker_remediated += cap_letter
            elif 65 <= ord(letters) <= 90:
                ticker_remediated += letters
            elif 48 <= ord(letters) <= 57:
                ticker_remediated += letters
            else:
                #   skip and do not include
                logging.warning(f"YFinance - prep ticker - found unexpected letter in ticker - removing - {letters}")

        #   TODO: add more remediation steps

        return ticker_core

    def ticker(self, company_ticker, **kwargs):

        """ Retrieves company information based on the company_ticker. """

        self.ticker = self._prep_ticker(company_ticker)

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        try:
            company_info = yfinance.Ticker(self.ticker)
        except:
            company_info = {}
            logger.warning(f"YFinance - ticker - not successful looking up company information using the "
                           f"company ticker - {self.ticker}")

        return company_info

    def get_company_summary(self, ticker=None, **kwargs):

        """ Retrieves company summary based on the ticker. """

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        self.ticker = self._prep_ticker(ticker)

        output_info = {}

        try:
            company_info = yfinance.Ticker(self.ticker).info
        except:
            company_info = {}
            logger.warning(f"YFinance - ticker - not successful looking up company summary using the "
                           f"ticker - {ticker}")

        for targets in self.company_summary_keys:
            found_key = False
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
                    found_key = True
            if not found_key:
                output_info.update({targets: "NA"})
                logger.warning(f"YFinance - get_company_summary - could not find {targets} in web service response.")

        return output_info

    def get_financial_summary(self, ticker=None, **kwargs):

        """ Retrieves financial summary based on the ticker. """

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        if ticker:
            self.ticker = self._prep_ticker(ticker)

        try:
            company_info = yfinance.Ticker(self.ticker).info
        except:
            company_info = {}
            logger.warning(f"YFinance - ticker - not successful looking up company summary using the "
                           f"ticker - {self.ticker}")

        output_info = {}
        for targets in self.financial_summary_keys:
            found_key = False
            for keys, values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
                    found_key = True
            if not found_key:
                output_info.update({targets:"NA"})
                logger.warning(f"YFinance - get_financial_summary - could not find {targets} in web service response.")

        return output_info

    def get_stock_summary(self, ticker=None, **kwargs):

        """ Retrieves the stock summary based on ticker. """

        try:
            import yfinance
        except ImportError:
            raise LLMWareException(message="Exception: need to `pip install yfinance` library.")

        if ticker:
            if isinstance(ticker, dict):
                ticker = ticker["ticker"]

            self.ticker = self._prep_ticker(ticker)

        output_info = {}
        try:
            company_info = yfinance.Ticker(self.ticker).info
        except:
            company_info = {}
            logger.warning(f"YFinance - ticker - not successful looking up company summary using the "
                           f"ticker - {self.ticker}")

        for targets in self.stock_summary_keys:
            key_found = False
            for keys,values in company_info.items():
                if targets == keys:
                    output_info.update({targets: values})
                    key_found = True
            if not key_found:
                output_info.update({targets:"NA"})
                logger.warning(f"YFinance - get_stock_summary - could not find {targets} in web service response.")

        return output_info


class WebSiteParser:

    """ WebSiteParser implements a website-scraping parser.   It can be accessed directly, or through the Parser
    and Library classes indirectly.

    Scraping web content is generally permissible in most cases, although ethical guidelines and sensible best
    practices should be followed.  Scraped content does not grant any license to the content, and still must be
    used in compliance with any associated copyrights.

    For a good introduction to recommended web scraping practices, see
    https://monashdatafluency.github.io/python-web-scraping/section-5-legal-and-ethical-considerations/

    This website parser implementation is designed to quickly extract content from HTML-oriented websites, and
    is not intended for use on large commercial websites, which tend to be primarily dynamic javascript.

    If your local SSL certificate is out-of-date, you will likely receive errors - this can be updated easily
    with a python command script, or you can select unverified_context=True to ignore

    """

    def __init__(self, url_or_fp, link="/", save_images=True, reset_img_folder=False, local_file_path=None,
                 from_file=False, text_only=False, unverified_context=False):

        try:
            from bs4 import BeautifulSoup
            import requests
            from urllib.request import urlopen, Request
            import lxml

        except ModuleNotFoundError or ImportError:
            raise LLMWareException(message="Exception: to use WebSiteParser requires additional Python "
                                           "dependencies via pip install:  "
                                           "\n -- pip3 install beautifulsoup4 (or bs4)"
                                           "\n -- pip3 install lxml"
                                           "\n -- pip3 install requests"
                                           "\n -- pip3 install urllib3")

        #   note: for webscraping, unverified ssl are a common error
        #   to debug, if the risk environment is relatively low, set `unverified_context` = True, although
        #   preferred method is to update the ssl certificate to remove this error
        self.unverified_context=unverified_context

        # by default, assume that url_or_fp is a url path
        self.url_main = url_or_fp

        # by default, will get images and links
        self.text_only = text_only

        # by passing link - provides option for recursive calls to website for internal links
        if link == "/":
            self.url_link = ""
        else:
            self.url_link = link

        self.url_base = self.url_main + self.url_link

        # check for llmware path & create if not already set up
        if not os.path.exists(LLMWareConfig.get_llmware_path()):
            # if not explicitly set up by user, then create folder directory structure
            LLMWareConfig.setup_llmware_workspace()

        if not local_file_path:
            # need to update this path
            self.local_dir = os.path.join(LLMWareConfig.get_llmware_path(), "process_website/")
        else:
            self.local_dir = local_file_path

        if reset_img_folder:
            if os.path.exists(self.local_dir):
                # important step to remove & clean out any old artifacts in the /tmp/ directory
                shutil.rmtree(self.local_dir)
            os.makedirs(self.local_dir, exist_ok=True)

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir, exist_ok=True)

        if from_file:
            # interpret url as file_path and file_name
            try:
                html = open(url_or_fp, encoding='utf-8-sig', errors='ignore').read()
                bs = BeautifulSoup(html, features="lxml")
                self.html = bs.findAll()
                success_code = 1
                self.text_only = True
            except:
                logger.error(f"error: WebSite parser- could not find html file to parse at {url_or_fp}")
                success_code = -1
                self.text_only = True
        else:
            # this is the most likely default case -interpret url_or_fp as url
            try:
                req = Request(self.url_base, headers={'User-Agent': 'Mozilla/5.0'},unverifiable=True)

                if self.unverified_context:
                    import ssl
                    ssl._create_default_https_context = ssl._create_unverified_context
                    html = urlopen(req).read()
                else:
                    html = urlopen(req).read()

                bs = BeautifulSoup(html, features="lxml")

                self.bs = bs
                self.html = bs.findAll()

                out_str = ""
                for x in self.html:
                    out_str += str(x) + " "

                with open(os.path.join(self.local_dir, "my_website.html"), "w", encoding='utf-8') as f:
                    f.write(out_str)
                f.close()

                success_code = 1

            except Exception as e:
                success_code = -1
                raise LLMWareException(message=f"Exception: website_parser could not connect to website - "
                                               f"caught error - {e}.  Common issues: \n"
                                               f"1.  Update your certificates in the Python path, e.g., "
                                               f"'Install Certificates.command'\n"
                                               f"2.  Set unverified_context=True in the constructor for "
                                               f"WebSiteParser.\n"
                                               f"Note: it is also possible that the website does not exist, "
                                               f"or that it is restricted and rejecting your request for any "
                                               f"number of reasons.  The website may have other restrictions on "
                                               f"programmatic 'bot' access, and if so, those should be followed.")

        self.save_images = save_images
        self.image_counter = 0
        self.links = []
        self.mc = None
        self.entries = None
        self.core_index = []
        self.header_text = []
        self.internal_links = []
        self.external_links = []
        self.other_links = []

        # meta-data expected in library add process
        self.source = str(self.url_base)
        self.success_code = success_code

    def website_main_processor(self, img_start, output_index=True):

        """ Main processing of HTML scraped content and converting into blocks. """

        logger.info(f"update: WebSite Parser - initiating parse of website: {self.url_main}")

        output = []
        counter = 0
        # by passing img_start explicitly- enables recursive calls to links/children sites
        img_counter = img_start

        long_running_string = ""

        # new all_text to remove duplications
        all_text = []

        internal_links = []
        external_links = []
        header_text = []
        unique_text_list = []
        unique_header_list = []

        last_text = ""
        last_header = ""

        text = ""

        for elements in self.html:

            content_found = 0
            img = ""
            img_success = 0
            img_url = ""
            img_name = ""

            link = ""
            link_type = ""

            # text = ""
            text_dupe_flag = False
            entry_type = "text"

            # if text only, then skip checks for images and links
            if not self.text_only:

                if "property" in elements.attrs:
                    if elements.attrs["property"] == "og:image":
                        if "content" in elements.attrs:

                            img_extension = elements["content"]
                            img_success, img, img_url, img_name = \
                                self.image_handler(img_extension, elements, img_counter)

                            if img_success == 1:
                                img_counter += 1
                                content_found += 1

                if "src" in elements.attrs:

                    img_extension = elements["src"]
                    img_success, img, img_url, img_name = self.image_handler(img_extension, elements, img_counter)

                    if img_success == 1:
                        img_counter += 1
                        content_found += 1

                if "href" in elements.attrs:

                    if elements.attrs["href"]:
                        link_success, link, link_type = self.link_handler(elements)
                        content_found += 1

                        if link_success == 0:
                            # skip .js files and other formatting in link crawling
                            # link_success == 0 if not .js // ==1 if .js file

                            if link_type == "internal":
                                if link != "/":
                                    if link not in internal_links:
                                        internal_links.append(link)

                            if link_type == "external":
                                external_links.append(link)

            # main check for text
            if elements.get_text():

                get_text = 1

                if elements.attrs == {}:
                    get_text = -1

                if "type" in elements.attrs:
                    # skip css and javascript
                    if elements.attrs["type"] in ["text/css", "text/javascript", "application/ld+json",
                                                  "application/jd+json"]:

                        get_text = -1

                #   wip - generally associated with javascript inline script
                if "charset" in elements.attrs:
                    get_text = -1

                if "jsname" in elements.attrs:
                    get_text = -1

                if "jscontroller" in elements.attrs:
                    get_text = -1

                if get_text == 1:

                    # text handler
                    s_out = ""

                    # alt for consideration to clean up string
                    # s_out += string.replace('\n', ' ').replace('\r', ' ').replace('\xa0', ' ').replace('\t', ' ')

                    js_markers = ["{", "function", "(function", "if (", "window", "on", "#", "this.", ".",
                                  "var", ";", "html", "@"]

                    keep_adding = True

                    for string in elements.stripped_strings:

                        if not s_out:

                            # kludge -  list of exclusions to remove the most common javascript in site
                            for marker in js_markers:
                                if string.startswith(marker):
                                    keep_adding = False
                                    break

                        #   if found at start of any substring - high probability inline js -  break
                        if string.startswith("(function") or string.startswith("window.") or string.startswith("this."):
                            break

                        if keep_adding:
                            s_out += string + " "
                        else:
                            break

                    text += s_out

                    if text.strip():
                        header_entry = []

                        if text not in unique_text_list:
                            unique_text_list.append(text)
                            content_found += 1
                            long_running_string += text + " "
                            last_text = text
                            text_dupe_flag = False
                        else:
                            text_dupe_flag = True

                        if "h1" in elements.name:
                            header_entry = (counter, "h1", text)

                        if "h2" in elements.name:
                            header_entry = (counter, "h2", text)

                        if "h3" in elements.name:
                            header_entry = (counter, "h3", text)

                        if header_entry:
                            if text not in unique_header_list:
                                last_header = text
                                header_text.append(header_entry)
                                unique_header_list.append(text)

            # if looking for images and links, then prioritize in attribution
            if not self.text_only:
                if img and img_success == 1:
                    entry_type = "image"
                else:
                    if link:
                        entry_type = "link"
                    else:
                        if text:
                            entry_type = "text"
                        else:
                            content_found = 0
            else:
                entry_type = "text"

            if content_found > 0:
                master_index = (self.url_main, self.url_link, counter)

                if text and not text_dupe_flag:

                    entry = {"content_type": entry_type,
                             "text": text,
                             "image": {"image_name": img_name, "image_url": img_url},
                             "link": {"link_type": link_type, "link": link},
                             "master_index": master_index,
                             "last_header": last_header}

                    counter += 1
                    # save entry if image, or if (A) text > 50 and (B) not a dupe
                    if entry_type == "image" or (len(text) > 50 and text not in all_text):
                        output.append(entry)
                        all_text.append(text)
                        text = ""

        self.image_counter = img_counter
        self.internal_links = internal_links
        self.external_links = external_links
        self.header_text = header_text

        if header_text:
            header_text_sorted = sorted(header_text, key=lambda x: x[1])
            self.header_text = header_text_sorted

        self.core_index = output
        self.entries = len(output)

        logger.info(f"update: WebSite Parser - completed parsing: {self.url_main}")
        logger.info(f"update: extracted {len(self.core_index)} elements")

        if self.image_counter > 0:
            logger.info(f"update: extracted {self.image_counter} images and saved @ path: {self.local_dir}")

        if not output_index:
            return len(output), img_counter

        return self.core_index

    def link_handler(self, elements):

        """ Handles processing of links found in main page content. """

        link_out = ""
        link_type = ""
        js_skip = 0

        if elements.attrs["href"].endswith(".js"):
            link_out = elements.attrs["href"]
            link_type = "js"
            js_skip = 1

        if elements.attrs["href"].endswith(".ico") or elements.attrs["href"].endswith(".ttf"):
            link_out = elements.attrs["href"]
            link_type = "other_formatting"
            js_skip = 1

        if elements.attrs["href"].endswith(".css"):
            link_out = elements.attrs["href"]
            link_type = "css"
            js_skip = 1

        if elements.attrs["href"].startswith(self.url_base):
            # save relative link only
            link_out = elements.attrs["href"][len(self.url_base):]
            link_type = "internal"

        if str(elements.attrs["href"])[0] == "/":
            # relative link
            if elements.attrs["href"]:
                if not elements.attrs["href"].startswith("//"):
                    link_out = elements.attrs["href"]
                    link_type = "internal"

        if elements.attrs["href"].startswith("https://") and \
                not elements.attrs["href"].startswith(self.url_base):
            # website but not the url_base - external link
            link_out = elements.attrs["href"]
            link_type = "external"

        return js_skip, link_out, link_type

    def image_handler(self, img_extension, elements, img_counter):

        """ Handles and processes images found in main content. """

        success = -1
        img_raw = []
        image_name = ""
        full_url = ""

        try:
            img_raw, response_code, full_url = self._request_image(img_extension, elements)

            if response_code == 200:

                if self.save_images:

                    # need to capture img type, e.g., .jpg
                    img_type = ""
                    if img_extension.endswith("png"): img_type = "png"
                    if img_extension.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                    if img_extension.endswith("tiff"): img_type = "tiff"
                    if img_extension.endswith("svg"): img_type = "svg"

                    # secondary check if not at end - break off at '?' query string
                    if img_type == "":
                        original_img_name = img_extension.split("/")[-1]
                        original_img_name = original_img_name.split("?")[0]
                        if original_img_name.endswith("png"): img_type = "png"
                        if original_img_name.endswith("jpg") or img_extension.endswith("jpeg"): img_type = "jpg"
                        if original_img_name.endswith("tiff"): img_type = "tiff"
                        if original_img_name.endswith("svg"): img_type = "svg"

                    # only save image if valid img format found
                    if img_type in ("png", "jpg", "svg", "tiff"):
                        image_name = "image{}.{}".format(img_counter, img_type)
                        fp = self.local_dir + image_name
                        s = self._save_image(img_raw, fp)
                        success = 1

                    else:
                        logger.info(f"update:  WebSite -  found image OK but could not "
                                    f"figure out img type: {img_extension} ")

        except:
            logger.info(f"warning: WebSite - could not retrieve potential image: {elements.attrs['src']}")
            success = -1

        return success, img_raw, full_url, image_name

    def _save_image(self, img_raw, fp):

        """ Internal utility to save images found. """

        with open(fp, 'wb') as f:
            img_raw.decode_content = True
            shutil.copyfileobj(img_raw, f)

        return 0

    def _save_image_website(self, fp, img_num, doc_id, save_file_path):

        """ Internal utility for images. """

        # internal method to save image files and track counters

        img_type = img_num.split(".")[-1]
        img_core = img_num[len("image"):].split(".")[0]

        # image name of format:   image{{doc_ID}}_{{img_num}}.png
        new_img_name = "image" + str(doc_id) + "_" + str(img_core) + "." + img_type
        created = 0

        img = open(os.path.join(fp, img_num), "rb").read()
        if img:
            f = open(os.path.join(save_file_path, new_img_name), "wb")
            f.write(img)
            f.close()
            created += 1

        return new_img_name, created

    def _request_image(self, img_extension, img):

        """ Retrieve images from links. """
        try:
            import requests
        except ImportError:
            raise LLMWareException(message="Exception: could not import `requests` library which is a required "
                                           "dependency for web parsing.")

        # relative link - refers back to main index page
        # check if url_main gives better performance than .url_base

        url_base = self.url_main
        url_ext = img_extension

        full_url = url_ext

        if url_ext:
            if url_ext.startswith("https:"):
                # this is an external link - just use the source
                full_url = url_ext

            if url_ext.startswith("/"):
                # relative ID - add url_base to get img

                full_url = url_base + url_ext

        r = requests.get(full_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})

        return r.raw, r.status_code, full_url

    def get_all_links(self):

        """ Utility to retrieve all links. """

        # note: not called by the main handler - kept as direct callable method

        internal_links = []
        external_links = []
        other_links = []
        js_links = []

        for content in self.html:

            found = 0
            js = 0

            if "href" in content.attrs:
                if content.attrs["href"]:

                    if content.attrs["href"].endswith(".js"):
                        js_links.append(content.attrs["href"])
                        js = 1

                    if content.attrs["href"].startswith(self.url_base):
                        # save relative link only
                        out = content.attrs["href"][len(self.url_base):]
                        internal_links.append(out)
                        found = 1

                    if str(content.attrs["href"])[0] == "/":
                        # relative link
                        out = content.attrs["href"]
                        if out:
                            # skip double //
                            if not out.startswith("//"):
                                internal_links.append(out)
                        found = 1

                    if content.attrs["href"].startswith("https://") and \
                            not content.attrs["href"].startswith(self.url_base):
                        # website but not the url_base - external link
                        out = content.attrs["href"]
                        external_links.append(out)
                        found = 1

                    if found == 0:
                        other_links.append(content.attrs["href"])

        self.internal_links = internal_links
        self.external_links = external_links
        self.other_links = other_links

        top_links = []

        for z in range(0, len(internal_links)):

            link_tokens = internal_links[z].split("/")
            for y in range(0, len(self.mc)):
                if self.mc[y][0].lower() in link_tokens:
                    if internal_links[z] not in top_links:
                        top_links.append(internal_links[z])
                    break

        link_results = {"internal_links": internal_links, "external_links": external_links,
                        "other_links": other_links, "top_links": top_links}

        return link_results

    def get_all_img(self, save_dir):

        """ Utility to get all images from html pages. """

        # note: not called by main handler - kept as separate standalone method

        counter = 0
        for content in self.html:
            counter += 1
            if "src" in content.attrs:
                if str(content).startswith("<img"):

                    if content.attrs["src"]:
                        try:
                            img_raw, response_code, full_url = self._request_image(content, self.url_base)

                            if response_code == 200:

                                # need to capture img type, e.g., .jpg
                                original_img_name = content.attrs["src"].split("/")[-1]
                                original_img_name = original_img_name.split("?")[0]
                                img_type = ""
                                if original_img_name.endswith(".png"):
                                    img_type = "png"
                                if original_img_name.endswith(".jpg"):
                                    img_type = "jpg"
                                if original_img_name.endswith(".svg"):
                                    img_type = "svg"
                                if img_type == "":
                                    img_type = original_img_name.split(".")[-1]

                                fp = save_dir + "img{}.{}".format(counter, img_type)
                                s = self._save_image(img_raw, fp)
                                counter += 1
                        except:
                            logger.info(f"update: could not find image: {content.attrs['src']}")

        return 0

