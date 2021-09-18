import PySimpleGUI as sg
import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time
from cx_Freeze import setup, Executable


"""
Using ParseHub to scrap Covid19 stats from the internet.
Showing it to the user with PySimpleGui gui windows. The user have an option to speak his query or type his query.
The available data is number of total deaths in the world caused by Covid19, number of cases in the world of Covid19 and
specific data of deaths and cases of each country. The speaking is optimized by pyaudio and speech_recognition libraries.
The audio inputted by the user is later diagnosed by regex speech patterns.
"""

# Essential parameters of ParseHub run
API_KEY = "ttHf5ObQg-o_"
PROJECT_TOKEN = "tGtRh0hEmA7y"
RUN_TOKEN = "t44su9_gHOTs"
isUpdated = 0

"""
base = None

executables = [Executable("main.py", base=base)]

packages = ["idna","PySimpleGUI", "pyttsx3", "speech_recognition"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name="<Covid19 stats>",
    options=options,
    version="0.11",
    description='<Web Scrapper project>',
    executables = executables
)

"""

# Data class holds all the essential methods to extract our desired data.

class Data:

	def __init__(self, api_key, project_token):
		self.api_key = api_key
		self.project_token = project_token
		self.params = {
			"api_key" : self.api_key
		}
		self.data = self.get_data()

	def get_data(self):
		response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',
		                        params=self.params) #acutal extracting of our scrapped data
		data = json.loads(response.text)
		return data

	def get_total_cases(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Coronavirus Cases:":
				return content['value']

	def get_total_deathes(self):
		data = self.data['total']

		for content in data:
			if content['name'] == "Deaths:":
				return content['value']

	def get_country_data(self,country):
		data = self.data["country"]

		for content in data:
			if content['name'].lower() == country.lower():
				return content

	def get_list_of_countries(self):
		countries = []
		for country in self.data['country']:
			countries.append(country['name'].lower())
		return countries

	# The function initalize a thread that always looking for updated data. That ensures as that even if the user is running the program non stop for days,
	# as long as we call update_Data once (and we call it every time at our initial run, in main()) , the data will keep being updated.
	def update_data(self):
		response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run',
		                         params=self.params)


		def poll():
			time.sleep(0.1)
			old_data = self.data
			while True:
				new_data = self.get_data()
				# when we get the slightest change, we update our data
				if new_data != old_data:
					self.data = new_data
					isUpdated = 1
					break
				time.sleep(5)

		t = threading.Thread(target = poll)
		t.start()


def speak(text):
	print(text)
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()


def get_audio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		r.adjust_for_ambient_noise(source)
		audio = r.listen(source)
		said = ""

		try:
			said = r.recognize_google(audio)
		except Exception as e:
			print("Command didn't recognized")

		print(said.lower())
		return said.lower()


def main():
	data = Data(API_KEY, PROJECT_TOKEN)

	data.update_data() #to keep the data updated all the time. in the function a new run of scraping is done.
	country_list = data.get_list_of_countries()
	font = ("Arial, 11")

	sg.theme('DarkAmber')


	layout = [[sg.Text("All data is taken from https://www.worldometers.info/coronavirus/ and being updated automatically"
	                   "\n Please choose if you want to get your query by typing or speaking",font=font)], [sg.Button("Type")], [sg.Button("Speak")]]

	# Create the window
	window = sg.Window("Covid19 stats", layout)

	# Create an event loop
	while True:
		event, values = window.read()
		# End program if user closes window or
		# presses the OK button
		if event == sg.WIN_CLOSED:
			break

		elif event == "Type":
			TypeChose(data,country_list)

		elif event == "Speak":
			SpeakChose(data,country_list)

	window.close()
	exit(0)
	

def TypeChose(data,country_list):
	sg.theme('DarkAmber')
	layout = [[sg.Text("To see total cases and deaths, type 'total' . \nTo see country"
	                   " specific stats, type country name, small letters")], [sg.InputText()], [sg.Text("Answer")],
	          [sg.MLine(size=(40, 1), key='ans')], [sg.Button("OK")], [sg.Button("GO BACK")]]

	window = sg.Window("Covid19 Stats", layout)
	while True:
		event, values = window.read()
		if event == "OK":
			text = values[0]
			ans = "Sorry, try again"
			for country in country_list:
				if text == country:
					country_data = data.get_country_data(country)
					ans = "Total cases in "+ text + " = " + country_data['total_cases'] +"\nToatl deathes in " + text + "= " + country_data['total_deathes']
			if text == "total":
				ans = "The total cases is :" + data.get_total_cases() +"\nThe total deaths is :" + data.get_total_deathes()

			window['ans'].update(ans)

		if event in (sg.WIN_CLOSED, "GO BACK"):
			break

	window.close()


def SpeakChose(data,country_list):
	sg.theme('DarkAmber')

	layout = [[sg.Text("Click record to start speaking, when you wish to end, say 'stop'.")], [sg.Button("RECORD")], [sg.Button("GO BACK")]]

	window = sg.Window("Covid19 stats", layout)

	while True:
		event, values = window.read()

		if event in ("GO BACK", sg.WIN_CLOSED):
			break

		if event == "RECORD":
			record(data, country_list)

	window.close()


def record(data, country_list):
	while True:
		END_PHASE = "stop"

		TOTAL_PATTERNS = {
			re.compile("[\w\s]+ total [\w\s] + cases"): data.get_total_cases,
			re.compile("[\w\s]+ total cases"): data.get_total_cases,
			re.compile("[\w\s]+ total [\w\s] + deaths"): data.get_total_deathes(),
			re.compile("[\w\s]+ total deaths"): data.get_total_deathes()
		}

		COUNTRY_PATTERNS = {
			re.compile("[\w\s]+ cases [\w\s]"): lambda country: data.get_country_data(country)['total_cases'],
			re.compile("[\w\s]+ deaths [\w\s]"): lambda country: data.get_country_data(country)['total_deathes']
		}

		text = get_audio()
		result = "Sorry, try again"

		isCountry = 0

		# First of all, we try to see if there is a country name in our text. If not, check if the text is compatible
		# with the pattern of the total stats around the world.
		for pattern, func in COUNTRY_PATTERNS.items():
			if pattern.match(text):
				for country in country_list:
					words = set(text.split(" "))
					if country in words:
						isCountry = 1
						if "cases" in words:
							result = "          the total number of cases in " + country + " is " + func(country)
						elif "deaths" in words or "death" in words:
							result = "          the total number of deaths in " + country + " is " + func(country)
						break

		if isCountry == 0:
			for pattern, func in TOTAL_PATTERNS.items():
				if pattern.match(text):
					result = func()
					break

		if text.find(END_PHASE) != -1:
			speak("        GoodBye")
			break

		if result:
			speak(result)


if __name__ == "__main__":
	main()



