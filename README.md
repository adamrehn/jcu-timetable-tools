JCU Timetable Tools
===================

The tools in this repository are designed to build on top of the new JCU timetable system, first introduced in 2016. The following tools are included:

- **core/scrape-timetable.py** - this Python script scrapes the JCU timetable and exposes data to the other tools via a REST API endpoint. Every other tool sources its data from this endpoint.
- **classic-ui/** - a web front-end that mimics the UI of the 2015-era JCU timetable.


Installation
------------

Before using any other tool, the core scraping script must first be running. Install the dependencies for the script:

```
pip3 install -r core/requirements.txt
```

Then, start the script:

```
python3 core/scrape-timetable.py
```

Each of the other tools can then be installed as required:

- The "Classic" UI is written in PHP and has no dependencies. It can simply be placed within the document root of any webserver running PHP 5 or newer.


REST API
--------

The core scraping script listens on port 5000 and exposes the REST API endpoint `/timetable`, which requires the following arguments:

- `subjects` - a space-delimited list of subject codes
- `campus` - one of the campus codes from the table below
- `sp` - the study period number, which must be an integer between 1 and 11 inclusive

Valid campus codes are listed in the [timetable help document](https://www.jcu.edu.au/__data/assets/pdf_file/0003/202899/TT-Information-for-Students.pdf), and are reproduced below:

|Code|Campus|
|----|------|
|CBH|Cairns Base Hospital|
|CCC|Cairns City|
|CNJ|Cloncurry|
|CNS|Cairns Smithfield|
|ISA|Mount Isa|
|MKY|Mackay|
|TCC|Townsville City|
|TIS|Thursday Island|
|TMH|Townsville Mater Hospital|
|TSV|Townsville Douglas|
|TTH|The Townsville Hospital|
