import sys
import os
import requests
import json
from mimetypes import MimeTypes
import base64
import re
import tempfile
from urlparse import urlparse

def run(block, data = {}, api_key = None):
	if type(data) is not dict:
		raise Exception("your data needs to be a dictionary.")

	data = json.dumps(data)

	api_key = api_key or os.environ.get('BLOCKSPRING_API_KEY')
	if(not(api_key)):
		api_key = ""
	
	blockspring_url = os.environ.get('BLOCKSPRING_URL') or 'https://sender.blockspring.com'
	block = block.split("/")[-1]
	response = requests.post( blockspring_url + "/api_v2/blocks/" + block + "?api_key=" + api_key, data = data , headers = {'content-type': 'application/json'})
	
	results = response.text
	try:
		return json.loads(results)
	except:
		return results

def define(block):
	def processStdin(request):
		# check if something coming into stdin
		if(not(sys.stdin.isatty())):
			# try to parse inputs as json
			try:
				params = json.loads(sys.stdin.read())
			except:
				raise Exception("You didn't pass valid json inputs.")
			
			# if inputs json, check if they're a dictionary
			if (type(params) is not dict):
				raise Exception("Can't parse keys/values from your json inputs.")
			
			# check if following blockspring spec
			if (not(("_blockspring_spec" in params) and params["_blockspring_spec"])):
				# not following spec, naively set params.
				request.params = params
			else:
				# we're following spec so lets remove _blockspring_spec, print errors to stderr, and parse files.
				for var_name in params.keys():
					# remove _blockspring_spec flag from params
					if (var_name == "_blockspring_spec"):
						pass
					# add errors to request object.
					elif ((var_name == "_errors") and type(params[var_name] is list)):
						for error in params[var_name]:
							if (type(error) is dict) and ("title" in error):
								request.addError(error)
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
						# create tmp file
						suffix = "-%s" % params[var_name]["filename"]
					  	tmp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
					  	# check if we have raw data
					  	if ("data" in params[var_name]):
					  		try:
					  			# decode raw data and save to tmp file
						  		tmp_file.write(base64.b64decode(params[var_name]["data"]))
						  		request.params[var_name] = tmp_file.name
						  	except:
						  		# couldn't decode base64, just setting param naively
						  		request.params[var_name] = params[var_name]
					  	else:
					  		try:
					  			# download file and save to tmp file
					  			r = requests.get(params[var_name]["url"], stream = True)
					  		except:
					  			# couldn't download file, just setting param naively
					  			request.params[var_name] = params[var_name]
					  		else:
						  		if (r.status_code == requests.codes.ok):
						  			# downloaded file and got normal status code. timpe to write to tmp.
						  			data = r.raw.read(decode_content=True)
							  		tmp_file.write(data)
								  	request.params[var_name] = tmp_file.name
							  	else:
							  		# downloaded file but didn't get normal status code, just setting param naively
							  		request.params[var_name] = params[var_name]
				  		tmp_file.close()
					# add rest key/values without any magic.
					else:
						request.params[var_name] = params[var_name]
			
			sys.stdin.close()

	def processArgs(request):
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
			request.params[key] = argv[key]

	request = Request()
	processStdin(request)
	processArgs(request)

	response = Response()
	block(request, response)

class Request:
	def __init__(self):
		self.params = {}
		self._errors = []

	def getErrors(self):
		return self._errors

	def addError(self, error):
		self._errors.append(error)

class Response:
	def __init__(self):	
		self.result = {
			"_blockspring_spec": True,
			"_errors": []
		}

	def addOutput(self, name, value = None):
		self.result[name] = value
		return self

	def addFileOutput(self, name, filepath):
		data = open(filepath).read()
		filename = os.path.basename(filepath)
		mime = MimeTypes()
		mime_guess = mime.guess_type(filename)[0]
		
		self.result[name] = {
			"filename": filename,
			"content-type": mime_guess,
			"data": base64.b64encode(data)
		}
		return self

	def addError(self, title, message = None):
		self.result["_errors"].append({
			"title": title,
			"message": message
			}
		)
		return self

	def end(self):
		print json.dumps(self.result)