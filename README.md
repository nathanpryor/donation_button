# donation_button
This Python script was a quick-and-dirty solution to build an Amazon Dash button that would donate to the ACLU through the page https://action.aclu.org/donate-aclu

The script requires the Mechanize library (http://wwwsearch.sourceforge.net/mechanize/).

Replace the obvious placeholders with your own information. 

It's set up to be run on Amazon's AWS Lambda service, with the credit card info stored as the following encrypted environment variables for a tiny bit more security:
	CC_number
	CC_expiration_month
	CC_expiration_year
	CC_CSC
If you're not doing that, go ahead and put them in as strings.

Note that the state and country menus use numeric codes rather than abbreviations. See the file country_and_state_codes.txt for the select menus from the page so you can find the appropriate value and enter it.