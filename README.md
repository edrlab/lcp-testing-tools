# Compliance tests for LCP/LSD server

## Requirements

  - **python 3.x**
  - **jsonschema**
  

## Recommendation

To avoid pollution of you global python environment, we advise you to use venv (unless you want to debug easily using e.g. VS Code):
```
python3 -m venv Pythonenv/lcpcheck
```

## Install the required Python modules

```
pip3 install jsonschema
pip3 install pyyaml
pip3 install lxml
pip3 install requests
pip3 install pyopenssl
pip3 install strict-rfc3339
pip3 install rfc3987
pip3 install python-dateutil
```

# Configuration file

A sample of configuration file is provided in etc/config.yml.dist

```
# Configuration of the lcp testing tool
lcp_encrypt:
  # cmd_path: Path to the lcpencrypt command
  cmd_path: /Work/gospace/bin/lcpencrypt
  
lcp_server:
  # base_uri: Url of the lcp server
  base_uri: <lcp-server-uri>
  auth:
    # user: Auth username to connect to lcp server
    user: <value>
    # passwd: Auth password to connect to lcp server
    passwd:"<value>
  # external_repository_path: External path where LCP server files are stored 
  # useful if the server is installed on a docker
  external_repository_path: <lcpfiles>
  # internal_repository_path: Path where LCP server files are stored
  internal_repository_path: <lcpfiles>
  # user_passphrase_hint: User passphrase hint used for license generation
  user_passphrase_hint: <hint-value>
  # user_passphrase: User passphrase  used for license generation
  user_passphrase: <passphrase-value>

lsd_server:
  # base_uri: Url of the lsd server
  base_uri: <lsd-server-uri>
  auth:
    # user: Auth username to connect to lsd server
    user: <value>
    # passwd: Auth password to connect to lsd server
    passwd: <value>
# working_path: Working path of the test suite
working_path: <value>
# root_cert_path: Path to the root certificate file
root_cert_path: <value>
```

## Run tests

Testing requires:

  - a customized config.yml (or .yaml)
  - an unprotected EPUB file
  - or a protected EPUB file
  - or an LCP license file

Then you can launch different tests:

Encrypt an EPUB file, generate a license and a protected file:

```
python3 src/client.py -vv config.yml -e <path-unprotected-epub>
```

Check a protected EPUB file:

```
python3 src/client.py -vv config.yml -p <path-protected-epub>
```

Check an LCP liense:

```
python3 src/client.py -vv config.yml -l <path-lcp-license>
```

Check the dynamic features (register, renew, return) of an LCP liense:

```
python3 src/client.py -vv config.yml -s <path-lcp-license>
```

The different tests can be easily chained. For exemple, if you have a protected EPUB file at hands, you can check the file, the embedded license and its dynamic features using: 

```
python3 src/client.py -vv config.yml -p <path-protected-epub> -l -s
```

And if you have an LCP license at hands, you can check the license and its dynamic features using: 

```
python3 src/client.py -vv config.yml -l <path-lcp-license> -s
```

The verbose option allows you to get more and more verbose information:
  - "-v": only **error** messages are displayed
  - "-vv": **info** and error messages are displayed
  - "-vvv": **debug**, info and error messages are displayed
