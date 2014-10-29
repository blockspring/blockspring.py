# blockspring.py

Python module to assist in creating blocks on Blockspring.

### Installation

```bash
pip install blockspring
```

### Example Usage

Save the following script to an example.py file:
```python
import blockspring

def myFunction(request, response):
    mySum = request["params"]["num1"] + request["params"]["num2"]
    
    response.addOutput('sum', mySum)

    response.end()

blockspring.define(myFunction)
```

Then in your command line write:
```shell
python example.py --num1=20 --num2=50
```

or

```shell
echo '{"num1":20, "num2": 50}' | python example.py
```

### License

MIT

### Contact

Email us: founders@blockspring.com
