#!/usr/bin/env python3
from bs4 import BeautifulSoup
from flask import Flask
from flask import request
import requests
import json
import re

# The URLs for the login page and the main timetable page
LOGIN_PAGE = 'https://timetable.jcu.edu.au/2016/Login.aspx'
MAIN_PAGE = 'https://timetable.jcu.edu.au/2016/Default.aspx'

# The list of valid campus codes, from
# <https://www.jcu.edu.au/__data/assets/pdf_file/0003/202899/TT-Information-for-Students.pdf>
CAMPUS_CODES = {
    'CBH': 'Cairns Base Hospital',
    'CCC': 'Cairns City',
    'CNJ': 'Cloncurry',
    'CNS': 'Cairns Smithfield',
    'ISA': 'Mount Isa',
    'MKY': 'Mackay',
    'TCC': 'Townsville City',
    'TIS': 'Thursday Island',
    'TMH': 'Townsville Mater Hospital',
    'TSV': 'Townsville Douglas',
    'TTH': 'The Townsville Hospital'
}

# Mapping specifying the weeks to display, based on a given study period
WEEKS_MAPPING = {
    'sp1':  '9;10;11;12;13;14;15;16;18;19;20;21;22',
    'sp10': '48;49;50;51;52;53;54',
    'sp11': '48;49;50;51;52;53;54;55;56;57;58;59',
    'sp2':  '31;32;33;34;35;36;37;38;39;41;42;43;44',
    'sp3':  '2;3;4;5;6;7;8',
    'sp4':  '9;10;11;12;13;14;15;16;17;18',
    'sp5':  '17;18;19;20;21;22;23;24;25',
    'sp6':  '23;24;25;26;27;28;29;30',
    'sp7':  '26;27;28;29;30;31',
    'sp8':  '31;32;33;34;35;36;37;38;39;40',
    'sp9':  '39;40;41;42;43;44;45;46;47'
}


# Resonsible for scraping the JCU timetable
class TimetableScraper:

    def __init__(self):

        # Create the session, and set our user-agent
        self._session = requests.Session()
        self._session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Linux) Gecko/20100101 Firefox/43.0'})

    # Parses the HTML content from a HTTP response
    def _parse_content(self, response):
        return BeautifulSoup(response.text, 'html.parser')

    # Extracts the server-generated hidden form field values
    def _extract_hidden_fields(self, pageContents):
        fields = {}
        for field in pageContents.select('input[type=hidden]'):
            key = field['name']
            value = field['value']
            fields[key] = value

        return fields

    # Matches subjects based on a set of filters
    def _match_subjects(self, subjects, filters):
        matched = []
        for currFilter in filters:
            try:
                filterRegex = re.compile(currFilter, re.IGNORECASE)
                for key in subjects:
                    if filterRegex.match(key):
                        matched.append(subjects[key])
            except:
                # Invalid regex string
                continue

        return matched

    # Transforms a set of filters into regular expressions
    def _transform_filters(self, filters, sp, campus):
        transformed = []
        for currFilter in filters:
            currFilter = currFilter.replace('*', '.+')
            transformed.append(currFilter + '.*_' + campus.upper() +
                               '.*_' + sp.upper())

        return transformed

    # Extracts the string from an element that specifies the date ranges for
    # an event
    def _extract_dates(self, elem):
        return ' '.join(list(elem.stripped_strings)).replace('\u2011', '-')

    # Performs the scrape
    def scrape(self, filters, campus, sp):

        # Request the login page
        loginPage = self._session.get(LOGIN_PAGE)

        # Login as a student
        params = self._extract_hidden_fields(self._parse_content(loginPage))
        params = list(params.items()) + [
            ('tUserName', ''),
            ('tPassword', ''),
            ('bGuestLogin', 'TIMETABLE')
        ]
        headers = {'Referer': LOGIN_PAGE}
        loginReq = self._session.post(LOGIN_PAGE, data=params, headers=headers)

        # Navigate to the subject selection page
        params = self._extract_hidden_fields(self._parse_content(loginReq))
        params['__EVENTTARGET'] = 'LinkBtn_modules'
        params = list(params.items()) + [
            ('tLinkType', 'information')
        ]
        headers['Referer'] = MAIN_PAGE
        uiPage = self._session.post(MAIN_PAGE, data=params, headers=headers)
        uiPageContent = self._parse_content(uiPage)

        # Extract the subject list
        subjectList = uiPageContent.select('#dlObject option')
        subjectValues = list(s['value'] for s in subjectList)
        subjectLabels = list(s.text.split(' - ')[0] for s in subjectList)
        subjects = {}
        for index, key in enumerate(subjectLabels):
            subjects[key] = subjectValues[index]

        # Match subjects using the supplied parameters
        matches = self._match_subjects(
            subjects,
            self._transform_filters(filters, sp, campus))

        # Render the timetable for the selected subjects
        params = self._extract_hidden_fields(uiPageContent)
        params = list(params.items()) + [
            ('tLinkType', 'modules'),
            ('dlFilter2', '%'),
            ('dlFilter', ''),
            ('tWildcard', ''),
            ('lbWeeks', WEEKS_MAPPING[sp]),
            ('lbDays', '1-7'),
            ('dlPeriod', '1-34'),
            ('dlType', 'jcu_module_list;cyon_reports_list_url;dummy'),
            ('bGetTimetable', 'View+Timetable')
        ]
        for subject in matches:
            params.append(('dlObject', subject))
        timetableData = self._session.post(
            MAIN_PAGE,
            data=params,
            headers=headers)

        # Extract the data from the timetable list view
        parsedPage = BeautifulSoup(timetableData.text, 'html.parser')
        tableRows = parsedPage.select('.cyon_table tbody tr')

        # Remove hidden text used for sortng data
        for p in parsedPage.select('p.sort'):
            p.clear()

        # Extract the column headings
        columnLabels = list(th.text for th in
                            parsedPage.select('.cyon_table thead th'))

        # Iterate over the events and process each one
        processedEvents = []
        for row in tableRows:

            processed = {}
            for index, td in enumerate(row.select('td')):

                # Determine if this table cell contains the dates popup
                dateDiv = td.select('div')
                if len(dateDiv) > 0:
                    dateDiv = dateDiv[0]
                    dateString = self._extract_dates(dateDiv)
                    processed['dates'] = dateString.replace('Date(s): ', '')
                    dateDiv.clear()

                # Extract the value and store it with the correct key
                key = columnLabels[index] \
                    .replace('(', '') \
                    .replace(')', '') \
                    .replace(' ', '_') \
                    .lower()
                processed[key] = self._extract_dates(td)

            processedEvents.append(processed)

        # Return processed event data
        return processedEvents


# Sanitises user input for the list of subject codes
def sanitise(s):
    s = s.replace(',', ' ')
    s = s.replace(';', ' ')
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s.strip()


# The main REST API endpoint
app = Flask(__name__)


@app.route("/timetable")
def requestHandler():
    try:
        # Check that the required arguments have been provided
        if 'subjects' not in request.args \
                or 'campus' not in request.args or 'sp' not in request.args:
            raise Exception('The following arguments are required:'
                            '"subjects", "campus", "sp"')

        # Parse the supplied arguments
        filters = sanitise(request.args['subjects'].lower()).split(' ')
        campus = request.args['campus'].lower()
        sp = 'sp' + request.args['sp'].lower()

        # Check that the specified Campus is valid
        if campus.upper() not in CAMPUS_CODES:
            message = 'Invalid Campus specified. Valid values are: ' \
                + ', '.join((code + ' (' + CAMPUS_CODES[code] + ')')
                            for code in CAMPUS_CODES)
            raise Exception(message)

        # Check that the specified Study Period is valid
        if sp not in WEEKS_MAPPING:
            raise Exception('Invalid Study Period specified.'
                            ' An integer between 1 and 11 must be provided.')

        # Perform the timetable scrape
        scraper = TimetableScraper()
        return json.dumps(
            scraper.scrape(filters, campus, sp), sort_keys=True, indent=4)

    except Exception as e:
        # Report any errors to the client
        return json.dumps({'error': str(e)})

# Listen on all interfaces
app.run(host='0.0.0.0')
