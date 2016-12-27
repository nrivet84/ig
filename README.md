# ig

IG REST trading API in Python
[IG Labs](http://labs.ig.com/)

## Purposes:
* trading
* intraday
* discrete time (non-continious = no streaming)
* decision concerning monitoring and execution supposed to be programmed in another software

## Running the tests
In tests\config.ini, add your IG credentials for demo account or live account.
The API key is mandatory, see how to [generate one](https://labs.ig.com/gettingstarted).

As the **ig** 'software' is not a package for now, you need to add its path.

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ig')))

import ig_service as igs
import ig_tools as igt
```

To get the 'demo' credentials and set up the proxies if needed.
```python
proxy_user, proxy_password, api_key, username, password, account = \
igt.getconfig('demo')
```

To create a session.
```python
service = igs.IGservice(username, password, api_key, account, 'demo', proxy_user, proxy_password)
service.login()
```

## License
MIT
