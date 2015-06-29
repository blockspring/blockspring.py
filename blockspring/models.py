import os
import json
import base64

from mimetypes import MimeTypes

__all__ = ['Request', 'Response']

class Request:
    def __init__(self):
        self.params = {}
        self._errors = []
        self._headers = {}

    def getErrors(self):
        return self._errors

    def addError(self, error):
        self._errors.append(error)

    def addHeaders(self, headers):
        self._headers = headers

    def getHeaders(self):
        return self._headers

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

    def addErrorOutput(self, title, message = None):
        self.result["_errors"].append({
            "title": title,
            "message": message
            }
        )
        return self

    def end(self):
        print(json.dumps(self.result))
