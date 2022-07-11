# Ogarniacz okazji

## Table of contents
* [General info](#general-info)
* [Features](#features)
* [Usage](#usage)
* [Status](#status)
* [Changelog](#changelog)


## General info
This simple python script looks for all offers in Otomoto.pl, saves them in a local database and sends an e-mail with new offers. You can run the script automatically. Now, you don't have to search for offers manually.
	
## Features
* Downloading all offers from otomoto.pl (web scraping)
* Storing data in sqlite database
* Sending an e-mail with new offers (via API)

### To Do
* Support for multiple searches
* Sending an SMS new offers (via API)
* Improve the layout of the mail
* Add exceptions
	
## Usage
* Copy files
* Install libraries from requirements.txt
* Create account on smtp2go.com
* Create mail account (no Gmail, Yahoo)
* Complete the configuration file - config.py
* Run file scraper.py
* Have a fun!

## Status
Complete

## Changelog
# 1.0
* Working app
