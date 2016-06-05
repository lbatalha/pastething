#new paste defaults

#ttl = 60 #default paste TTL
#lexer = 'txt' #default paste lexer
defaults = {
	'ttl': 60,
	'lexer': 'txt',
	'paste': '',
}

#app configuration
secret_key = 'some_secret'
max_content_length = 10 * 1024 * 1024 #max form upload size

#paste url
url_len = 1 #minimum paste url length
url_alph = tuple("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghkmnpqrstuvwxyz") #alphabet used to generate paste url
base = len(url_alph)