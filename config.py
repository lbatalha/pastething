#new paste defaults
defaults = {
	'ttl': 1.0,
	'lexer': 'txt',
	'paste': '',

}

#paste options
ttl_max = 730 #maximum allowed paste ttl in hours
ttl_min = 0 #minimum allowed paste ttl in hours
token_len = 6 #delete token length in bytes/characters

#flask configuration
secret_key = 'some_secret'
max_content_length = 10 * 1024 * 1024 #max form upload size in bits

#paste url
url_len = 1 #minimum paste url length in characters
url_alph = tuple("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghkmnpqrstuvwxyz") #alphabet used to generate paste url
base = len(url_alph)

#error messages
empty_paste = "pls, actually paste something k?\n"
invalid_ttl = "ttl must be between " + str(ttl_min) + " and " + str(ttl_max) +" hours\n"