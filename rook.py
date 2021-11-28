def run(shutit_sessions, machines):
	shutit_session = shutit_sessions['machine1']
	# Set up rook https://rook.io/docs/rook/v1.7/quickstart.html
	shutit_session.pause_point('ROOK END')
