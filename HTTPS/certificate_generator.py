from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    NoEncryption,
    PrivateFormat
)
import datetime
import os

class CertificateGenerator:
    def __init__(self, root_ca_cert_path='MyOrg-RootCA.crt', root_ca_key_path='MyOrg-RootCA.key', root_ca_key_password=b"123123"):
        with open(root_ca_cert_path, 'rb') as cert_file:
            self.root_cert = x509.load_pem_x509_certificate(cert_file.read())
        
        with open(root_ca_key_path, 'rb') as key_file:
            self.root_key = load_pem_private_key(
                key_file.read(), password=root_ca_key_password
            )

    def create_signed_cert(self, domain_name, output_dir='certs'):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"YourState"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"YourCity"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"YourOrg"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain_name),
        ])
        csr = x509.CertificateSigningRequestBuilder().subject_name(subject).sign(key, hashes.SHA256())

        cert = (
            x509.CertificateBuilder()
            .subject_name(csr.subject)
            .issuer_name(self.root_cert.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName([x509.DNSName(domain_name)]),
                critical=False,
            )
            .sign(self.root_key, hashes.SHA256())
        )

        cert_pem = cert.public_bytes(Encoding.PEM)
        key_pem = key.private_bytes(
            Encoding.PEM, 
            PrivateFormat.PKCS8,
            NoEncryption()
        )

        certfile = os.path.join(output_dir, f"{domain_name}.crt")
        keyfile = os.path.join(output_dir, f"{domain_name}.key")
        
        with open(certfile, 'wb') as cert_out:
            cert_out.write(cert_pem)
        with open(keyfile, 'wb') as key_out:
            key_out.write(key_pem)

        return certfile, keyfile