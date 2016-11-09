# Compliance tests for LCP/LSD server

## Requirements

  - **python 3.x**

  - **jsonschema**

## Recommendations

To avoid pollution of you global python environment, we advise you to use virtualenv:
```
virtualenv <virtualenv_dir>
```

and install jsonschema:

```
<virtualenv_dir>/bin/pip3 install jsonschema
```
# Configuration file

A sample of configuration file is provided in etc/config.yml.dist

```
# Configuration sample to use with readium-lcp-server-docker
lcp_encrypt:
  # cmd_path: Path the lcpencrypt command
  cmd_path: /tmp/readium-lcp-server-docker/bin/lcpencrypt
lcp_server:
  # base_uri: Url of lcp server
  base_uri: http://localhost:8989
  # external_repository_path: External path where LCP server files are stored
  external_repository_path: /tmp/readium-lcp-server-docker/lcp-server/files
  # internal_repository_path: Path where LCP server files are stored
  internal_repository_path: /files
  auth:
    # user: Auth username to connect to lcp server
    user: lcp
    # passwd: Auth password to connect to lcp server
    passwd: readium
lsd_server:
  base_uri: http://localhost:8990
  auth:
    # user: Auth username to connect to lsd server
    user: lsd
    # passwd: Auth password to connect to lsd server
    passwd: readium
# working_path: Working path of test suite
working_path: /tmp
```

## Run tests

Before launching tests you require :

  - a specific config.yml
  - a clear sample epub

Then you can launch tests:

```
<virtualenv_dir>/bin/python3 src/client.py [-vvv] <config_file> <epub_file>
```

The verbose option allows you to get more and more verbose information:
  - "-v": only **error** messages are displayed
  - "-vv": **info** and error messages are displayed
  - "-vvv": **debug**, info and error messages are displayed
