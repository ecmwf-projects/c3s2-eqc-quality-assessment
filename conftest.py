import ssl

# Use standard OpenSSL defaults to allow connections to legacy servers
ssl.create_default_context()
