# Ogarniacz okazji

## Table of contents
* [General info](#general-info)
* [Screens](#screens)
* [Usage](#usage)
* [Status](#status)
* [Changelog](#changelog)


## General info
This simple python script looks for all offers in Otomoto.pl, saves them in a local database and sends an e-mail with new offers. You can run the script automatically. Now, you don't have to search for offers manually.
	
## Screens
![](https://33333.cdn.cke-cs.com/kSW7V9NHUXugvhoQeFaf/images/a9996284414b1c315ed0cee42e12b094e5783d97e7c635a3.jpg)

### To Do
* Support for multiple searches
* Sending an SMS new offers (via API)
* Improve the layout of the mail
* Add exceptions
	
## Usage
* Copy files
* Install libraries from requirements.txt
* Complete data of smtp server and receiver - file html_template.py
* Run file scraper.py with parameter 
* Have a fun!

## Status
Complete

## Changelog
# 1.0
* Working app

# 2.0
* Changed method of sending an e-mail (via SMTP)
* Added HTML e-mail template
* Added web link as script parameter
* Fixed bug for one results page
* Fixed bug for various parameters in the link (? or &)
* Added car's foto
* Added exception handling
* Removed unnecessary files
* Other small fixes and optimalization