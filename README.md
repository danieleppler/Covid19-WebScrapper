

<img width="271" alt="C19 webscrapper logo" src="https://user-images.githubusercontent.com/46427281/133890194-c682aeb4-2e31-4b7d-ba19-fa3a7de81aca.png">


# Overview

*Exe file in dist/main*

This project assembles a Web scrapper scraping covid 19 pandemic statistic around the world. 
User can invoke the data by typing a query or speaking a query, using voice recognition technique.

# features

* The user is channeled when the program starts to a main page. The user can choose from this page to type or speak his query.
* The Data available to the user is number of cases in total around the world, number of deaths in total around the world,
  number of cases of each country, and number of deaths of each country.
* The data is taken from the web ( https://www.worldometers.info/coronavirus/ ) and updated every time the program starts.

# System Interfaces

* The data is scrapped from the web, from https://www.worldometers.info/coronavirus/ website. The data in the website is updated regularly and every time the program start,
 it invokes data from this website.
* The scrapping is done by ParseHub program.
* The GUI for the user is made with PySimpleGui library.
* The voice recognition is modeled by voice recognition, re, and PyAudio libraries, and uses Google Voice-To-Text technique.
*  Seperate Thread is use for consistent check for update from the web.
*  Written in Python PL

