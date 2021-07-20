from setuptools import findpackages
from setuptools import setup

setup(
	name='SailSheets',
	version='2.0.0',
	description='''Creates a Sail Plan for renting sailing club 
		sail boats, then allows the Captain to add crew and guests, 
		and when the Sail Plan is saved it logs the start time.  
		When the Sail Plan is closed it logs the end time and total
		sailing hours and then computes various fees based on member type.

		This app is not used online, but is used on a dedicated stand-
		alone PC in the clubhouse. Members are trusted to enter data
		correctly -- version 1 has been in use for 11 years but due
		to a Linux update one of the key admin utilities no longer works.

		This version corrects the admin utility and duplicates the 
		functionality of version 1.  
		''',
	auther='Tim Holland',
	author_email='hollandt@md.metrocast.net',
	url='',
	install_requires=[],
	packages=find_packages(exclude=('tests*', 'testing*')),
	entry_points=(
		'console_scripst': [
			'SailSheets-cli = SailSheets.main:main',
			]
		)

	)