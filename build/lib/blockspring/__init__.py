import sys
import os
import requests
import json
from mimetypes import MimeTypes
import base64

def run(block, data):
	api_key = os.environ.get('BLOCKSPRING_API_KEY')

	if(not(api_key)):
		raise Exception("BLOCKSPRING_API_KEY environment variable not set")

	blockspring_url = os.environ.get('BLOCKSPRING_URL') or 'https://sender.blockspring.com'

	block_parts = block.split("/")
	block = block_parts[len(block_parts) - 1]

	response = requests.post( blockspring_url + "/api_v2/blocks/" + block + "?api_key=" + api_key, data = data )

	body = response.text
	
	try:
		body = json.loads(body)
		return body
	except:
		return body

def define(block):
	result = {
		"data": {},
		"files": {},
		"errors": None
	}

	request = {
		"params": {},
		"stdin": ""
	}

	class Response:
		def addOutput(self, name, value):
			result["data"][name] = value
			return self

		def addFileOutput(self, name, filepath):
			filename = os.path.basename(filepath)
			mime = MimeTypes()
			mime_guess = mime.guess_type(filename)[0]

			data = open(filepath).read()

			result["files"][name] = {
				"filename": filename,
				"mimeType": mime_guess,
				"data": base64.b64encode(data)
			}
			return self

		def end(self):
			output = json.dumps(result)
			print output

	def processStdin():
		if(not(sys.stdin.isatty())):
			request["params"] = json.loads(sys.stdin.read())
			sys.stdin.close()

	def processArgs():
		if (len(sys.argv) > 1):
			argv = dict(map(lambda x: x.lstrip('-').split('='),sys.argv[1:]))
		else:
			argv = {}

		for key in argv.keys():
			if (not(key in ["_", "$0"])):
				request["params"][key] = argv[key]

	processStdin()
	processArgs()

	response = Response()

	block(request, response)
