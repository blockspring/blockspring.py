import sys
import os
import requests
import json
from mimetypes import MimeTypes
import base64
import re
import tempfile
from urlparse import urlparse

def run(block = None, data = None, api_key = None):
	if(not(block)):
		raise Exception("you forgot to pass in your block!")

	if(not(data)):
		data = {}

	try:
		data = json.dumps(data)
	except:
		raise Exception("your data needs to be json.")

	api_key = api_key or os.environ.get('BLOCKSPRING_API_KEY')

	if(not(api_key)):
		sys.stderr.write("BLOCKSPRING_API_KEY environment variable not set.\n")
		api_key = ""

	blockspring_url = os.environ.get('BLOCKSPRING_URL') or 'https://sender.blockspring.com'

	block = block.split("/")[-1]

	response = requests.post( blockspring_url + "/api_v2/blocks/" + block + "?api_key=" + api_key, data = data , headers = {'content-type': 'application/json'})

	results = response.text
	
	try:
		return json.loads(results)
	except:
		return results

def define(block = None):
	if (not(block)):
		raise Exception("you forgot to pass in your function!")

	request = {
		"params": {},
		"stdin": ""
	}

	def processStdin():
		# check if something coming into stdin
		if(not(sys.stdin.isatty())):
			# try to parse inputs as json
			try:
				params = json.loads(sys.stdin.read())
			except:
				raise Exception("You didn't pass valid json inputs.")
			# if inputs json, check if they're a dictionary
			if (type(params) is dict):
				# check if following blockspring spec
				if (("blockspring_data" in params) and params["blockspring_data"]):
					# we're following spec so lets remove blockspring_data, print errors to stderr, and parse files.
					for var_name in params.keys():
						# remove blockspring_data flag from params
						if (var_name == "blockspring_data"):
							pass
						# print errors to stderr
						elif (
						(var_name == "blockspring_errors") and 
						type(params[var_name] is list)):
							for error in params[var_name]:
								if ((type(error) is dict) and ("title" in error)):
									pass
						# add files to tempdir
						elif (
						# file must be dictionary
						(type(params[var_name]) is dict) and 
						# filename must exist and not be empty
						("filename" in params[var_name]) and 
						(params[var_name]["filename"] is not None) and 
						# either data or url must exist and not be empty
						(
							(("data" in params[var_name]) and params[var_name]["data"] is not None) or 
							(("url" in params[var_name]) and params[var_name]["url"] is not None))
						):
							suffix = "-%s" % params[var_name]["filename"]
						  	tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
						  	if ("data" in params[var_name]):
						  		try:
							  		tmp_file.write(base64.b64decode(params[var_name]["data"]))
							  		request["params"][var_name] = tmp_file.name
							  	except:
							  		sys.stderr.write("Can't decode base64 string. Leaving parameter as is.\n")
							  		request["params"][var_name] = params[var_name]
						  	else:
						  		try:
						  			r = requests.get(params[var_name]["url"], stream = True)
						  		except:
						  			sys.stderr.write("Can't get data from URL. Leaving parameter as is.\n")
						  			request["params"][var_name] = params[var_name]
						  		else:
							  		if (r.status_code == requests.codes.ok):
							  			data = r.raw.read(decode_content=True)
								  		tmp_file.write(data)
									  	request["params"][var_name] = tmp_file.name
								  	else:
								  		sys.stderr.write("Can't get data from URL. Leaving parameter as is.\n")
								  		request["params"][var_name] = params[var_name]
					  		tmp_file.close()
						# add rest key/values without any magic.
						else:
							request["params"][var_name] = params[var_name]
				# not following spec, naively set params.
				else:
					request["params"] = params
			# inputs not a json dictionary, don't pass them through.
			else:
				raise Exception("Can't parse keys/values from your json inputs.")
			
			sys.stdin.close()

	def processArgs():
		if (len(sys.argv) > 1):
			argv = {}

			for arg in sys.argv[1:]:
				found_match = re.search("([^=]*)\=(.*)", arg)
				if found_match:
					found_match = found_match.groups()
					if found_match[0][0:2] == "--":
						argv[found_match[0][2:]] = found_match[1]
					else:
						argv[found_match[0]] = found_match[1]
		else:
			argv = {}

		for key in argv.keys():
			if (not(key in ["_", "$0"])):
				request["params"][key] = argv[key]

	processStdin()
	processArgs()

	response = Response()

	block(request, response)

class Response:
	def __init__(self):	
		self.result = {
			"blockspring_data": True,
			"blockspring_errors": []
		}

	def addOutput(self, name = None, value = None):
		if (not(name)):
			raise Exception("Forgot to include a key_name.")
		else:
			if ((name != "blockspring_data") and (name != "blockspring_errors")):
				self.result[name] = value
			else:
				raise Exception("Cannot set key as 'blockspring_data' or 'blockspring_errors'.")
		return self

	def addFileOutput(self, name = None, filepath = None):
		if (not(name) or not(filepath)):
			raise Exception("Forgot to include a key_name or a filepath.")
		else:
			if ((name != "blockspring_data") and (name != "blockspring_errors")):
				try:
					data = open(filepath).read()
				except:
					sys.stderr.write("Couldn't find file in filepath, attempting to fetch as url.\n")
					try:
						r = requests.get(filepath, stream = True)
					except:
						raise Exception("File neither filepath nor url.")
					else:
						if (r.status_code == requests.codes.ok):
							data = r.raw.read(decode_content=True)

							filename = urlparse(filepath).path.split("/")[-1]
							mime = MimeTypes()
							mime_guess = mime.guess_type(filename)[0]

							self.result[name] = {
								"filename": filename,
								"content-type": mime_guess,
								"data": base64.b64encode(data)
							}
						else:
							r.raise_for_status()
				else:
					filename = os.path.basename(filepath)
					mime = MimeTypes()
					mime_guess = mime.guess_type(filename)[0]
					
					self.result[name] = {
						"filename": filename,
						"content-type": mime_guess,
						"data": base64.b64encode(data)
					}
			else:
				raise Exception("Cannot set key as 'blockspring_data' or 'blockspring_errors'.")
		return self

	def addError(self, title = None, message = None):
		if (title):
			self.result["blockspring_errors"].append({
				"title": title,
				"message": message
				}
			)
		else:
			# don't want to raise exception, right? it's just an error.
			sys.stderr.write("Forgot to include an error title.\n")
		return self

	def end(self):
		print json.dumps(self.result)