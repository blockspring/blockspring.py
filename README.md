# blockspring.py

Python module to assist in creating blocks on Blockspring.

### Installation

```bash
pip install blockspring
```

### Example Usage

```python
import blockspring

def myFunction(request, response):
    mySum = request["params"]["num1"] + request["params"]["num2"]
    
    response.addOutput('sum', data["sum"])

    response.end()

blockspring.define(myFunction)
```

### License

MIT

### Contact

Email us: founders@blockspring.com
