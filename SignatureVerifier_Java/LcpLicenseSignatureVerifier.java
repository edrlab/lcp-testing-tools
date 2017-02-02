import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonPrimitive;
import com.google.gson.JsonSerializationContext;
import com.google.gson.JsonSerializer;
import com.google.gson.reflect.TypeToken;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;

import java.lang.reflect.Type;

import java.math.BigDecimal;

import java.nio.file.Files;
import java.nio.file.Paths;

import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.PublicKey;
import java.security.Signature;
import java.security.SignatureException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;
import java.util.TreeMap;

import org.bouncycastle.util.encoders.Base64;

public class LcpLicenseSignatureVerifier {
		
	public static final String ANSI_RESET = "\u001B[0m";
	public static final String ANSI_BLACK = "\u001B[30m";
	public static final String ANSI_RED = "\u001B[31m";
	public static final String ANSI_GREEN = "\u001B[32m";
	public static final String ANSI_YELLOW = "\u001B[33m";
	public static final String ANSI_BLUE = "\u001B[34m";
	public static final String ANSI_PURPLE = "\u001B[35m";
	public static final String ANSI_CYAN = "\u001B[36m";
	public static final String ANSI_WHITE = "\u001B[37m";

	private static final String USAGE_INFO =
		ANSI_BLUE +
		"==================================\n" +
		ANSI_RESET +
		" LcpLicenseSignatureVerifier.java\n" +
		ANSI_BLUE +
		"==================================\n\n" +
		ANSI_RESET +

		"This is a command line tool that verifies the signature\n" +
		"of a given LCP license based on a given certificate.\n\n" +

		"The executable returns (0) to denote success,\n" +
		"otherwise error code (1) in case of failure.\n\n" +

		"The mandatory command line input parameters are:\n" +
		"    [1] " + ANSI_GREEN + "root certificate\n" + ANSI_RESET +
		"        (relative or absolute path to file with extension '.pem' or '.crt')\n" +
		"        e.g. " + ANSI_PURPLE + "../certs/root_certificate.pem" + ANSI_RESET +
		"\n\n" +
		"    [2] " + ANSI_GREEN + "LCP license\n" + ANSI_RESET +
		"        (relative or absolute path to file with extension '.lcpl')\n" +
		"        e.g. " + ANSI_PURPLE + "ebook_unzipped/META-INF/license.lcpl" + ANSI_RESET +
		"\n\n" +
		
		"The optional command line input parameters are:\n" +
		"    [3] " + ANSI_GREEN + "verbose\n" + ANSI_RESET +
		"        (if set, more information will be printed to standard output)\n" +
		"\n\n" +

		ANSI_BLUE +
		"==================================\n" +
		ANSI_RESET +
		"\n";
		
	
	private final Gson m_Gson =
		new GsonBuilder()
		.serializeNulls()
		.disableHtmlEscaping()
		.registerTypeAdapter(Double.class, new JsonSerializer<Double>() {
		    @Override
		    public JsonElement serialize(Double originalValue, Type typeOf, JsonSerializationContext context) {
		        BigDecimal bigValue = BigDecimal.valueOf(originalValue);
		        bigValue = new BigDecimal(bigValue.toBigIntegerExact());
		        return new JsonPrimitive(bigValue);
		    }
		})
		.create();
	
	private final File m_certificateFile;
	private final File m_lcpFile;
	public LcpLicenseSignatureVerifier(File certificateFile, File lcpFile) {
		m_certificateFile = certificateFile;
		m_lcpFile = lcpFile;
	}

	private X509Certificate m_rootCertificate = null;
	private void loadRootCertificate() {
		try {
			CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
			m_rootCertificate = (X509Certificate)certificateFactory.generateCertificate(new FileInputStream(m_certificateFile));

			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "Root certificate from [" + ANSI_YELLOW + m_certificateFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
				System.out.println(m_rootCertificate);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}
		} catch (Exception e) {
			System.err.println(ANSI_RED + "### Problem loading root certificate from [" + ANSI_YELLOW + m_certificateFile.getAbsolutePath() + ANSI_RED + "].\n\n" + ANSI_RESET);

			System.err.println(e.getMessage());
			
			System.exit(1); // FAILURE
			return;
		}
	}

	private X509Certificate m_providerCertificate = null;
	private void loadProviderCertificate(String base64certificate) {
		try {
			CertificateFactory certificateFactory = CertificateFactory.getInstance("X.509");
			m_providerCertificate = (X509Certificate)certificateFactory.generateCertificate(new ByteArrayInputStream(Base64.decode(base64certificate.getBytes())));
			
			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "Provider certificate from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
				System.out.println(m_providerCertificate);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}
		} catch (Exception e) {
			System.err.println(ANSI_RED + "### Problem loading provider certificate from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_RED + "].\n\n" + ANSI_RESET);

			System.err.println(e.getMessage());
			
			System.exit(1); // FAILURE
			return;
		}
	}

	private String m_lcp_canonicalJsonString = null;
	private String m_lcp_base64certificate = null;
	private String m_lcp_signature = null;
	private String m_lcp_signatureAlgorithmURI = null;
	private void loadLcp() {

		try {
			String lcp_jsonString = null;

			// String lineStr = "";
			// lcp_jsonString = "";
			// BufferedReader lcpBufferedReader = new BufferedReader(new InputStreamReader(new FileInputStream(m_lcpFile), "UTF8"));
			// while ((lineStr = lcpBufferedReader.readLine()) != null) { lcp_jsonString += lineStr; }

			lcp_jsonString = new String(Files.readAllBytes(Paths.get(m_lcpFile.getAbsolutePath())));
			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "LCP license JSON [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
				System.out.println(lcp_jsonString);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}

			Type type = new TypeToken<Map<String, Object>>(){}.getType();
			Map<String, Object> lcpJsonMap = m_Gson.fromJson(lcp_jsonString, type);
			for (String key : lcpJsonMap.keySet()) {
				if (key.equalsIgnoreCase("signature")) {
					Map<String, Object> signatureJsonMap = m_Gson.fromJson(m_Gson.toJson(lcpJsonMap.get(key)), type);
					
					m_lcp_signatureAlgorithmURI = (String)signatureJsonMap.get("algorithm");
					if (m_verbose) {
						System.out.println("\n\n");
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println(ANSI_CYAN + "LCP signature algorithm URI from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
						System.out.println(m_lcp_signatureAlgorithmURI);
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println("\n\n");
					}

					if (m_lcp_signatureAlgorithmURI == null
					|| (!m_lcp_signatureAlgorithmURI.equalsIgnoreCase("http://www.w3.org/2001/04/xmldsig-more#rsa-sha256")
					&& !m_lcp_signatureAlgorithmURI.equalsIgnoreCase("http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"))
					) {					
						System.err.println(ANSI_RED + "### Bad signature algorithm in LCP license [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_RED + "] ('" + m_lcp_signatureAlgorithmURI + "' should be 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256' or 'http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256').\n\n" + ANSI_RESET);

						System.exit(1); // FAILURE
						return;
					}
					
					m_lcp_signature = (String)signatureJsonMap.get("value");
					if (m_verbose) {
						System.out.println("\n\n");
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println(ANSI_CYAN + "LCP signature from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
						System.out.println(m_lcp_signature);
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println("\n\n");
					}

					m_lcp_base64certificate = (String)signatureJsonMap.get("certificate");
					if (m_verbose) {
						System.out.println("\n\n");
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println(ANSI_CYAN + "LCP provider certificate (base64) from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
						System.out.println(m_lcp_base64certificate);
						System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
						System.out.println("\n\n");
					}

					break;
				}
			}
			
			Iterator<Map.Entry<String, Object>> iter = lcpJsonMap.entrySet().iterator();
			while (iter.hasNext()) {
				Map.Entry<String, Object> entry = iter.next();
				if ("signature".equalsIgnoreCase(entry.getKey())) {
					iter.remove();
					break;
				}
			}
			String lcp_jsonString_withoutSignature = m_Gson.toJson(lcpJsonMap);
			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "LCP license JSON, without signature [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
				System.out.println(lcp_jsonString_withoutSignature);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}

			TreeMap<String, Object> canonicalLcpJsonMap = sortJsonKeysAlphabetically(lcp_jsonString_withoutSignature);
			m_lcp_canonicalJsonString = m_Gson.toJson(canonicalLcpJsonMap);
			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "LCP license canonical JSON [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "]: " + ANSI_RESET);
				System.out.println(m_lcp_canonicalJsonString);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}

		} catch (Exception e) {
			System.err.println(ANSI_RED + "### Problem loading LCP license from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_RED + "].\n\n" + ANSI_RESET);

			System.err.println(e.getMessage());
			
			System.exit(1); // FAILURE
			return;
		}
	}

	private void verifyProviderCertificate(X509Certificate providerCertificate, X509Certificate rootCertificate) {

		PublicKey publicKey = rootCertificate.getPublicKey();
		try {
			providerCertificate.verify(publicKey);
			if (m_verbose) {
				System.out.println("\n\n");
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "Succesfully verified the provider certificate from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_CYAN + "] against the root certificate from [" + ANSI_YELLOW + m_certificateFile.getAbsolutePath() + ANSI_CYAN + "] using public key [" + ANSI_YELLOW + publicKey + ANSI_CYAN + "].\n\n" + ANSI_RESET);
				System.out.println(ANSI_CYAN + "----------------------------------------------------------" + ANSI_RESET);
				System.out.println("\n\n");
			}
		} catch (Exception e) {
			System.err.println(ANSI_RED + "### Error verifying the provider certificate from [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_RED + "] against the root certificate from [" + ANSI_YELLOW + m_certificateFile.getAbsolutePath() + ANSI_RED + "] using public key [" + ANSI_YELLOW + publicKey + ANSI_RED + "].\n\n" + ANSI_RESET);

			System.err.println(e.getMessage());
			
			System.exit(1); // FAILURE
			return;
		}
	}

	private void verifyLcpSignature(String lcp_canonicalJsonString, String lcp_signature, X509Certificate providerCertificate) {
		try {
			
			//"http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
			Signature signatureVerifier = Signature.getInstance("SHA256withRSA");

			if (m_lcp_signatureAlgorithmURI.equalsIgnoreCase("http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256")) {
				signatureVerifier = Signature.getInstance("SHA256withECDSA");
			}

			PublicKey publicKey = providerCertificate.getPublicKey();
			signatureVerifier.initVerify(publicKey);

			byte[] lcp_canonicalJsonBytes = lcp_canonicalJsonString.getBytes();
			signatureVerifier.update(lcp_canonicalJsonBytes);

			byte[] lcp_signatureBytes = Base64.decode(lcp_signature.getBytes());
			boolean verified = signatureVerifier.verify(lcp_signatureBytes);
			
			if (verified) {
				System.out.println("\n\n");
				System.out.println(ANSI_GREEN + "### VALID SIGNATURE ###" + ANSI_RESET);
				System.out.println("\n\n");
				System.exit(0); // SUCCESS
				return;
			}

			System.out.println("\n\n");
			System.out.println(ANSI_RED + "### INVALID SIGNATURE ###" + ANSI_RESET);
			System.out.println("\n\n");
			System.exit(1); // FAILURE
			return;
		} catch (Exception e) {
			System.err.println(ANSI_RED + "### Problem verifying the LCP signature for [" + ANSI_YELLOW + m_lcpFile.getAbsolutePath() + ANSI_RED + "] against the root certificate from [" + ANSI_YELLOW + m_certificateFile.getAbsolutePath() + ANSI_RED + "].\n\n" + ANSI_RESET);

			System.err.println(e.getMessage());
			
			System.exit(1); // FAILURE
			return;
		}
	}
	
	// Recursive function
	@SuppressWarnings("unchecked")
	private TreeMap<String, Object> sortJsonKeysAlphabetically(String jsonString) {
		
		TreeMap<String, Object> jsonMap = m_Gson.fromJson(jsonString, TreeMap.class);

		for(String key : jsonMap.keySet()) {
			Object jsonObj = jsonMap.get(key);

			if (jsonObj instanceof Map) {
				String subJsonString = m_Gson.toJson(jsonObj);
				jsonMap.put(key, sortJsonKeysAlphabetically(subJsonString));

			} else if (jsonObj instanceof String) {
				//  NOOP

			} else if (jsonObj instanceof Double) {
				//  NOOP

			} else if (jsonObj instanceof ArrayList) {
				ArrayList arr = (ArrayList)jsonObj;
				
				for (int i = 0; i < arr.size(); i++) {
					Object subJsonObj = arr.get(i);

					if (subJsonObj instanceof Map) {
						String subJsonString = m_Gson.toJson(subJsonObj);
						arr.set(i, sortJsonKeysAlphabetically(subJsonString));
					} else {
						System.out.println(ANSI_RED + "Unexpected JSON type?" + ANSI_RESET);
						System.out.println(subJsonObj);
					}
				}
			} else {
				System.out.println(ANSI_RED + "Unexpected JSON type?" + ANSI_RESET);
				System.err.println(jsonObj);
			}
		}

		return jsonMap;
	}
	
	private boolean m_verbose = false;
	public void verify(boolean verbose) {
		m_verbose = verbose;

		// m_rootCertificate
		loadRootCertificate();

		// m_lcp_base64certificate
		// m_lcp_canonicalJsonString
		// m_lcp_signature
		// m_lcp_signatureAlgorithmURI
		loadLcp();

		// m_providerCertificate
		loadProviderCertificate(m_lcp_base64certificate);

		verifyProviderCertificate(m_providerCertificate, m_rootCertificate);

		verifyLcpSignature(m_lcp_canonicalJsonString, m_lcp_signature, m_providerCertificate);
	}
	
	public static void main(String[] args) {
		
		if (args.length < 2) {
			System.err.println(ANSI_RED + "### Missing input parameter(s).\n\n" + ANSI_RESET);

			System.err.println(USAGE_INFO);
			return;
		}
		
		String certificateFilePath = args[0];
		String certificateFilePath_lowerCase = certificateFilePath.toLowerCase();
		if (!certificateFilePath_lowerCase.endsWith(".crt") && !certificateFilePath_lowerCase.endsWith(".pem")) {
			System.err.println(ANSI_RED + "### Input parameter (1) [" + ANSI_YELLOW + certificateFilePath + ANSI_RED + "] must be filename with extension '.crt' or '.pem'.\n\n" + ANSI_RESET);

			System.err.println(USAGE_INFO);
			return;
		}
		
		File certificateFile = new File(certificateFilePath);
		if (!certificateFile.exists()) {
			System.err.println(ANSI_RED + "### Input parameter (1) [" + ANSI_YELLOW + certificateFilePath + ANSI_RED + "] file does not exist.\n\n" + ANSI_RESET);

			System.err.println(USAGE_INFO);
			return;
		}
		
		String lcpFilePath = args[1];
		String lcpPath_lowerCase = lcpFilePath.toLowerCase();
		if (!lcpPath_lowerCase.endsWith(".lcpl")) {
			System.err.println(ANSI_RED + "### Input parameter (2) [" + ANSI_YELLOW + lcpFilePath + ANSI_RED + "] must be filename with extension '.lcpl'.\n\n" + ANSI_RESET);

			System.err.println(USAGE_INFO);
			return;
		}
		
		File lcpFile = new File(lcpFilePath);
		if (!lcpFile.exists()) {
			System.err.println(ANSI_RED + "### Input parameter (2) [" + ANSI_YELLOW + lcpFilePath + ANSI_RED + "] file does not exist.\n\n" + ANSI_RESET);

			System.err.println(USAGE_INFO);
			return;
		}

		boolean verbose = false;
		if (args.length >= 3 && args[2].equalsIgnoreCase("verbose")) {
			verbose = true;
			
			System.out.println("\n\n");
			System.out.println(ANSI_CYAN + "####################################################################" + ANSI_RESET);
			System.out.println(ANSI_CYAN + "## MAX VERBOSITY ###################################################" + ANSI_RESET);
			System.out.println(ANSI_CYAN + "####################################################################" + ANSI_RESET);
			System.out.println("\n\n");
		}

		LcpLicenseSignatureVerifier verifier = new LcpLicenseSignatureVerifier(certificateFile, lcpFile);
		verifier.verify(verbose);
	}
}
