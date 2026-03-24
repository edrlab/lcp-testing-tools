NOTE: add "BC" (without the quotes) at the end of the CLI (after "verbose")
in order to select the BouncyCastle crypto provider instead of the default Sun ones.

Windows / MS-DOS command line:

run.bat "./example/cacert.pem" "./example/license.lcpl" verbose

run.bat "./example/lcp.crt" "./example/license2.lcpl" verbose


*nix command line:

chmod a+x run.sh && ./run.sh "./example/cacert.pem" "./example/license.lcpl" verbose

chmod a+x run.sh && ./run.sh "./example/lcp.crt" "./example/license2.lcpl" verbose

If this error occurs:

```
LcpLicenseSignatureVerifier.java:21: error: package javax.xml.bind does not exist
import javax.xml.bind.DatatypeConverter;
                     ^
1 error
```

...make sure to install Java 1.8 and invoke this command line to set a temporary `JAVA_HOME` environment variable: `export JAVA_HOME="$(/usr/libexec/java_home -v 1.8)"`.

On MacOS, the `/Library/Java/JavaVirtualMachines` folder would typically contain `jdk1.8.0_202.jdk` (manually installed in order to support `javax.xml.bind`),  as well as `jdk-12.0.1.jdk` and/or `jdk-11.0.1.jdk` (pre-installed?). To switch to another Java runtime, simply `export JAVA_HOME="$(/usr/libexec/java_home -v 11)"` (in this example, v11).

Using a Docker image (`adoptopenjdk/openjdk8:jdk8u292-b10`) to run a temporary Apple Container with a local mount (on MacOS, but this is obviously replicable in Windows and Linux):

`set -xv ; container --version ; container system stop ; container system start ; container system status ; container stop test-container ; container rm --force test-container ; container prune ; container list --all ; container run --cpus 4 --memory 2g --platform linux/arm64 --name test-container --volume ${PWD}:/MOUNT -w /MOUNT adoptopenjdk/openjdk8:jdk8u292-b10 sh -c 'set -xv ; cd SignatureVerifier_Java ; rm -rf out_classes ; mkdir -p out_classes ; javac -version ; javac LcpLicenseSignatureVerifier.java -Xlint:unchecked -Xdiags:verbose -d "out_classes" -classpath "lib/bcprov-jdk15on-1.56.jar:lib/gson-2.3.1.jar:lib/json-schema-validator-2.2.6.jar" && java -cp "lib/bcprov-jdk15on-1.56.jar:lib/gson-2.3.1.jar:lib/json-schema-validator-2.2.6.jar:./out_classes" LcpLicenseSignatureVerifier /MOUNT/cacert.pem /MOUNT/test.lcpl verbose ; rm -rf out_classes' ; container list --all ; container stop test-container ; container rm --force test-container ; container prune ; container system status ; container system stop ; set +xv`

Short, more readable version with the essential bits (Apple `container` can be replaced with `docker` from the official Docker Desktop on MacOS):

`container run --volume ${PWD}:/MOUNT -w /MOUNT adoptopenjdk/openjdk8:jdk8u292-b10 sh -c 'cd SignatureVerifier_Java ; javac LcpLicenseSignatureVerifier.java -Xlint:unchecked -Xdiags:verbose -d "." -classpath "lib/bcprov-jdk15on-1.56.jar:lib/gson-2.3.1.jar:lib/json-schema-validator-2.2.6.jar" && java -cp "lib/bcprov-jdk15on-1.56.jar:lib/gson-2.3.1.jar:lib/json-schema-validator-2.2.6.jar:./" LcpLicenseSignatureVerifier /MOUNT/cacert.pem /MOUNT/test.lcpl verbose'`

`./SignatureVerifier_Java/cacert.pem`:

```
-----BEGIN CERTIFICATE-----
MIIDxDCCAqygAwIBAgIIbAdC85NXQDEwDQYJKoZIhvcNAQELBQAwTjEUMBIGA1UE
ChMLUmVhZGl1bSBMQ1AxGDAWBgNVBAsTD1JlYWRpdW0gTENQIFBLSTEcMBoGA1UE
AxMTUmVhZGl1bSBMQ1AgUm9vdCBDQTAeFw0xNjExMjkxMDAwMDJaFw00NjExMjky
MzU5NTlaMEIxEzARBgNVBAoTCmVkcmxhYi5vcmcxFzAVBgNVBAsTDmVkcmxhYi5v
cmcgTENQMRIwEAYDVQQDEwlFRFJMYWIgQ0EwggEiMA0GCSqGSIb3DQEBAQUAA4IB
DwAwggEKAoIBAQDLuJoDa6bdqNBDjo130aYOVweEFz//+ythWxd9BmWy4QZ4F6kf
U9oTLmgRgZ2LWa48Z4PwmNX04bZ/JeWT3ACAfHZj0JXXc+uz+evVSgiRcxw8k/JS
YMDiCpj8SgP4LVbfO7Pg+LzFBtjiHp/5KZtl3DO/caeWxfBXaxT64CEGqigpLiZ7
EaPp3/mmBAx1n1AJrvyUnJvQ17e5i75WjEnTXybuCGWZMHwtB/qatFp8E5gs52+1
gSlrJzRtE0jAA1AG6wFAb2bXoCheLRR7n3AASezbmE2oEKeJPXDxBGezz+Yqem/1
smTv16AQKo4bfwuSaBQTm8V3um5HlOmW+M5LAgMBAAGjgbEwga4wDgYDVR0PAQH/
BAQDAgGGMB0GA1UdDgQWBBTcXPyT5B+f7rC66lILK8pSXODJhzAfBgNVHSMEGDAW
gBR6reuglOgbGTVJUvMTTwm5teTdMDASBgNVHRMBAf8ECDAGAQH/AgEAMEgGA1Ud
HwRBMD8wPaA7oDmGN2h0dHA6Ly9jcmwuZWRybGFiLnRlbGVzZWMuZGUvcmwvUmVh
ZGl1bV9MQ1BfUm9vdF9DQS5jcmwwDQYJKoZIhvcNAQELBQADggEBALQcmcf1XApy
TkPPmk5noiNuIm9OR7weaU8Wi4h0KxvQnbBX5csWbb3gspDSqUTTFZb7fvuD5U3c
mnuNst8jmJ9J1h7oYkNY8PyAS0CPl9ccG890ObJ7iv4tJ5gEMI83dlFzd8rps08m
uQJNGPbzZUP4WAWAQXS6AHS+cEj+9ykml3lhm6/OpzlMl6CPjdYD8k4eAo4KJlLg
mQKygYoBiVQdl2rmUgrMWv2vLmu5lgrCXfyynobAgHGhB5K0rMtu7moOkwekh1fe
qhGRLy/wMBsZ2AZEux17m6h8ead+1Eh7qCkVtLMPj18zthimKhmAzR9UODNO8adb
28V6rdu3cxE=
-----END CERTIFICATE-----
```
