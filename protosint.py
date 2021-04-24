#!/usr/bin/env python3

#Python libraries
import requests
from datetime import datetime
import re
import ipaddress

#Color setup
class bcolors:
	OKGREEN = '\x1b[92m'
	WARNING = '\x1b[93m'
	FAIL = '\x1b[91m'
	ENDC = '\x1b[0m'

def printAscii():
	"""
	ASCII Art
	"""
	print("""
   ___		   _			_	   _   
  / _ \_ __ ___ | |_ ___  ___(_)_ __ | |_ 
 / /_)/ '__/ _ \| __/ _ \/ __| | '_ \| __|
/ ___/| | | (_) | || (_) \__ \ | | | | |_  (author: pixelbubble)
\/	|_|  \___/ \__\___/|___/_|_| |_|\__| (forked by alol)
											  
	""")

	
def checkProtonAPIStatut():
	"""
	This function check proton API statut : ONLINE / OFFLINE

	"""
	requestProton_mail_statut = requests.get('https://api.protonmail.ch/pks/lookup?op=index&search=test@protonmail.com')
	if requestProton_mail_statut.status_code == 200:
		print(f"Protonmail API is {bcolors.OKGREEN}ONLINE{bcolors.ENDC}")
	else:
		print(f"Protonmail API is {bcolors.FAIL}OFFLINE{bcolors.ENDC}")

	requestProton_vpn_statut = requests.get('https://api.protonmail.ch/vpn/logicals')
	if requestProton_vpn_statut.status_code == 200:
		print(f"Protonmail VPN is {bcolors.OKGREEN}ONLINE{bcolors.ENDC}")
	else:
		print(f"Protonmail VPN is {bcolors.FAIL}OFFLINE{bcolors.ENDC}")


def printWelcome():
	welcome = """
Let's take a look at your target:
1 - Test the validity of a protonmail account
2 - Try to find if your target has a protonmail account
3 - Find if an IP is currently affiliated to ProtonVPN

[q]uit
"""
	print(welcome)


def checkValidityOneAccount():
	"""
	PROGRAM 1 : Test the validity of a protonmail account
	
	"""
	regexEmail = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
	
	print("You want to know if a protonmail email is real ?")
	mail = input("Give me your email: ")

	if not re.search(regexEmail,mail):
		mail+= "@protonmail.com"

	#Check if the protonmail exist : valid / not valid
	requestProton = requests.get('https://api.protonmail.ch/pks/lookup?op=index&search='+mail)
	bodyResponse = requestProton.text
	
	protonNoExist = "info:1:0" #not valid
	protonExist = "info:1:1" #valid

	if protonNoExist in bodyResponse:
		print(f"Protonmail email is {bcolors.FAIL}not valid{bcolors.ENDC}")

	if protonExist in bodyResponse:
		print(f"Protonmail email is {bcolors.OKGREEN}valid{bcolors.ENDC}")
		regexPattern1 = "2048:(.*)::" #RSA 2048-bit (Older but faster)
		regexPattern2 = "4096:(.*)::" #RSA 4096-bit (Secure but slow)
		regexPattern3 = "22::(.*)::" #X25519 (Modern, fastest, secure)
		try:
			timestamp = int(re.search(regexPattern1, bodyResponse).group(1))
			dtObject = datetime.fromtimestamp(timestamp)
			print("Date and time of the creation:", dtObject)
			print("Encryption : RSA 2048-bit (Older but faster)")
		except:
			pass

		try:
			timestamp = int(re.search(regexPattern2, bodyResponse).group(1))
			dtObject = datetime.fromtimestamp(timestamp)
			print("Date and time of the creation:", dtObject)
			print("Encryption : RSA 4096-bit (Secure but slow)")
		except:
			pass

		try:
			timestamp = int(re.search(regexPattern3, bodyResponse).group(1))
			dtObject = datetime.fromtimestamp(timestamp)
			print("Date and time of the creation:", dtObject)
			print("Encryption : X25519 (Modern, fastest, secure)")
		except:
			pass

		#Download the public key attached to the email
		invalidResponse = True

		while invalidResponse:
			#Input
			responseFromUser = input('Do you want to view the public key attached to the email ? [y]/n ')
			#Text if the input is valid
			if responseFromUser.lower().startswith('y') or not responseFromUser:
				invalidResponse = False
				requestProtonPublicKey = requests.get('https://api.protonmail.ch/pks/lookup?op=get&search='+mail)
				bodyResponsePublicKey = requestProtonPublicKey.text
				print(bodyResponsePublicKey)

				saveKey = True

				while saveKey:

					responseFromUser = input('Do you want to download the public key attached to the email ? y/[n] ')

					if responseFromUser.lower().startswith('y'):
						with open(f'{mail}_{dtObject}.pub', 'w') as keyfile:
							writelines(bodyResponsePublicKey)
						saveKey = False
					elif responseFromUser.lower().startswith('n') or not responseFromUser:
						saveKey = False
					else:
						print("Invalid Input")
						saveKey = True

			elif responseFromUser.lower().startswith('n'):
				invalidResponse = False
			else:
				print("Invalid Input")
				invalidResponse = True

def checkGeneratedProtonAccounts():
	"""
	PROGRAM 2 : Try to find if your target have a protonmail account by generating multiple adresses by combining information fields inputted
	
	"""

	#Input
	#TODO (alol) : add day/month of birth or find a bigger (?) combination creater
	print("Let's try to find your protonmail target (leave blank if unknown):")
	firstName = input("First name: ").lower()
	lastName  = input("Last name: ").lower()
	dayOfBirth   = input("Day of birth: ")
	monthOfBirth = input("Month of birth: ")
	yearOfBirth  = input("Year of birth: ")
	pseudo1 = input("Pseudo 1: ").lower()
	pseudo2 = input("Pseudo 2: ").lower()
	zipCode = input("zipCode: ")

	if not any([firstName, lastName, dayOfBirth, monthOfBirth, yearOfBirth, pseudo1, pseudo2, zipCode]):
		print('No information specified')
		# tu m'emmerdes nico
		return 

	#Protonmail domain
	domainList = ["@protonmail.com","@protonmail.ch","@pm.me"]

	#List of combinaison
	pseudoList = set()
	
	for domain in domainList:
		#For domain
		pseudoList.add(firstName+lastName+domain)
		pseudoList.add(lastName+firstName+domain)
		pseudoList.add(firstName[0]+lastName+domain)
		pseudoList.add(pseudo1+domain)
		pseudoList.add(pseudo2+domain)
		pseudoList.add(lastName+domain)
		pseudoList.add(firstName+lastName+yearOfBirth+domain)
		pseudoList.add(firstName[0]+lastName+yearOfBirth+domain)
		pseudoList.add(lastName+firstName+yearOfBirth+domain)
		pseudoList.add(pseudo1+yearOfBirth+domain)
		pseudoList.add(pseudo2+yearOfBirth+domain)
		pseudoList.add(firstName+lastName+yearOfBirth[-2:]+domain)
		pseudoList.add(firstName+lastName+yearOfBirth[-2:]+domain)
		pseudoList.add(firstName[0]+lastName+yearOfBirth[-2:]+domain)
		pseudoList.add(lastName+firstName+yearOfBirth[-2:]+domain)
		pseudoList.add(pseudo1+yearOfBirth[-2:]+domain)
		pseudoList.add(pseudo2+yearOfBirth[-2:]+domain)
		pseudoList.add(firstName+lastName+zipCode+domain)
		pseudoList.add(firstName[0]+lastName+zipCode+domain)
		pseudoList.add(lastName+firstName+zipCode+domain)
		pseudoList.add(pseudo1+zipCode+domain)
		pseudoList.add(pseudo2+zipCode+domain)
		pseudoList.add(firstName+lastName+zipCode[:2]+domain)
		pseudoList.add(firstName[0]+lastName+zipCode[:2]+domain)
		pseudoList.add(lastName+firstName+zipCode[:2]+domain)
		pseudoList.add(pseudo1+zipCode[:2]+domain)
		pseudoList.add(pseudo2+zipCode[:2]+domain)

	#Remove all irrelevant combinations
	#not sure what this does but ok ¯\_(ツ)_/¯
	for domain in domainList:
		if domain in pseudoList: pseudoList.remove(domain)
		if zipCode+domain in pseudoList: pseudoList.remove(zipCode+domain)
		if zipCode[:2]+domain in pseudoList: pseudoList.remove(zipCode[:2]+domain)
		if yearOfBirth+domain in pseudoList: pseudoList.remove(yearOfBirth+domain)
		if yearOfBirth[-2:]+domain in pseudoList: pseudoList.remove(yearOfBirth[-2:]+domain)
		if firstName+domain in pseudoList: pseudoList.remove(firstName+domain)

	print("===============================")
	print("I'm trying some combinaison: " + str(len(pseudoList)))
	print("===============================")

	for pseudo in pseudoList:
		requestProton = requests.get('https://api.protonmail.ch/pks/lookup?op=index&search='+pseudo)
		bodyResponse = requestProton.text

		protonNoExist = "info:1:0" #not valid
		protonExist = "info:1:1" #valid

		if protonNoExist in bodyResponse:
			print(f"{pseudo} is {bcolors.FAIL}not valid{bcolors.ENDC}")

		if protonExist in bodyResponse:
			regexPattern1 = "2048:(.*)::"
			regexPattern2 = "4096:(.*)::"
			regexPattern3 = "22::(.*)::"
			try:
				timestamp = int(re.search(regexPattern1, bodyResponse).group(1))
				dtObject = datetime.fromtimestamp(timestamp)
				print(f"{pseudo} is {bcolors.OKGREEN}valid{bcolors.ENDC}" + " - Creation date:", dtObject)
			except:
				pass

			try:
				timestamp = int(re.search(regexPattern2, bodyResponse).group(1))
				dtObject = datetime.fromtimestamp(timestamp)
				print(f"{pseudo} is {bcolors.OKGREEN}valid{bcolors.ENDC}" + " - Creation date:", dtObject)
			except:
				pass

			try:
				timestamp = int(re.search(regexPattern3, bodyResponse).group(1))
				dtObject = datetime.fromtimestamp(timestamp)
				print(f"{pseudo} is {bcolors.OKGREEN}valid{bcolors.ENDC}" + " - Creation date:", dtObject)
			except:
				pass

def checkIPProtonVPN():
	"""
	PROGRAM 3 : Find if your IP is currently affiliate to ProtonVPN
	
	"""
	while True:
		try:
			ip = ipaddress.ip_address(input('Enter IP address: '))
			break
		except ValueError:
			continue

	requestProton_vpn = requests.get('https://api.protonmail.ch/vpn/logicals')
	bodyResponse = requestProton_vpn.text
	if str(ip) in bodyResponse:
		print("This IP is currently affiliate to ProtonVPN")
	else:
		print("This IP is currently not affiliate to ProtonVPN")
	#print(bodyResponse)


# Entry point of the script
def main():
	printAscii()
	checkProtonAPIStatut()

	run = True
	while run:
		printWelcome()
		choice = input("Choose a program: ")
		if choice == "1":
			checkValidityOneAccount() 
		elif choice == "2":
			checkGeneratedProtonAccounts()
		elif choice == "3":
			checkIPProtonVPN()
		elif choice.lower().startswith('q'):
			run = False
			print('Bye bye!')
		else:
			print(f'{choice} is not a valid option')

if __name__ == '__main__':
	main()
