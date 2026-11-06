# docker-python

this client is basically docker-py but:

* auto-generated / multiple versions
* more ergonomically typed

## installation and usage

(this library will get published on pypi soon.)

```shell
pip install \
  https://github.com/alexanderankin/docker-python/releases/download/v0.3.0/docker_python_core-0.3.0-py3-none-any.whl \
  https://github.com/alexanderankin/docker-python/releases/download/v0.3.0/docker_python_requests-0.3.0-py3-none-any.whl \
  https://github.com/alexanderankin/docker-python/releases/download/v0.3.0/docker_python_v_1_55-0.3.0-py3-none-any.whl
```

```python
import os
from docker_python.core import DockerError
from docker_python.transports.requests import RequestsTransport
from docker_python.versions.v_1_55 import DockerClient

transport = RequestsTransport(os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock'))
client = DockerClient(transport)
client.check_version()
for image in client.list_images().with_all(True).execute():
    print(str(image))
```

## dependency tree

```text
.
├── docker-engine-api-specs
└── core
    ├── generator
    ├── docker-python-requests
    └── python-docker-v-*
```
