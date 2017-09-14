cd ./SignatureVerifier_Java 
javac LcpLicenseSignatureVerifier.java -Xlint:unchecked -d "out" -classpath "lib/bcprov-jdk15on-1.56.jar;lib/gson-2.3.1.jar;lib/json-schema-validator-2.2.6.jar"
java -cp "lib/bcprov-jdk15on-1.56.jar;lib/gson-2.3.1.jar;lib/json-schema-validator-2.2.6.jar;./out" LcpLicenseSignatureVerifier %1 %2 %3
