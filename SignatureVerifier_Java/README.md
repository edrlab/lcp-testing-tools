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
