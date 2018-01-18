import zipfile
from lxml import etree

from config.testconfig import TestConfig


class EncryptionXml():
  NS = {
    'enc': 'http://www.w3.org/2001/04/xmlenc#',
    'dsig': 'http://www.w3.org/2000/09/xmldsig#',
    'comp': 'http://www.idpf.org/2016/encryption#compression'
  }
  ENCRYPTION_URI = 'license.lcpl#/encryption/content_key'
  ENCRYPTION_TYPE = 'http://readium.org/2014/01/lcp#EncryptedContentKey'
  ENCRYPTION_METHOD = 'http://www.w3.org/2001/04/xmlenc#aes256-cbc'

  def __init__(self, content):
    self.config = TestConfig()
    self.content = content
    self.xml = etree.fromstring(content)
    self.schema = etree.parse(self.config.encryption_schema())
  
  def check_schema(self):
    xsd = etree.XMLSchema(self.schema)
    return xsd.validate(self.xml)

  def get_all_uri(self):
      return self.xml.xpath('//enc:EncryptedData[enc:EncryptionMethod[@Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc"]]/enc:CipherData/enc:CipherReference/@URI', namespaces=self.NS)

  def get_compressed_uri(self):
      return self.xml.xpath('//enc:EncryptedData[enc:EncryptionMethod[@Algorithm="http://www.w3.org/2001/04/xmlenc#aes256-cbc"] and enc:EncryptionProperties/enc:EncryptionProperty/comp:Compression[@Method="8"]]/enc:CipherData/enc:CipherReference/@URI', namespaces=self.NS)


class ePub():

  ENCRYPTION_XML = 'META-INF/encryption.xml'
  LCP_LICENSE = 'META-INF/license.lcpl'
  UNENCRYPTED_FILES = [
    'mimetype', 'META-INF/container.xml', 'META-INF/encryption.xml',
    'META-INF/license.lcpl', 'META-INF/manifest.xml',
    'META-INF/metadata.xml', 'META-INF/rights.xml', 'META-INF/signatures.xml'
  ]
  MEDIA_EXTENSIONS=['.jpg','.png','.gif','.mp3', '.mp4', '.ogg', '.avi', '.mov']

  def __init__(self, epub_path):
    self.epub_path = epub_path
    self.epub = zipfile.ZipFile(self.epub_path, 'r')
    self.xml = None

  def contains(self, name):
    try:
      self.epub.getinfo(name)
      return True
    except KeyError:
      return False

  def get_encryption_xml(self):
    with self.epub.open(self.ENCRYPTION_XML) as xmlfile:
      return EncryptionXml(xmlfile.read())

  def read(self, name):
    with self.epub.open(name) as f:
      return f.read()
