import mechanize
import boto3
import os

sns=boto3.client('sns')
# E.g., a US phone number with area code 123: '+11239873456'
phone_number='PHONE NUMBER WITH COUNTRY AND AREA CODE'

# Load encrypted credit card information (stored in environment variables).
from base64 import b64decode
CC_number = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_number']))['Plaintext']
CC_expiration_month = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_month']))['Plaintext']
CC_expiration_year = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_year']))['Plaintext']
CC_CVV=boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['CC_CVV']))['Plaintext']

br = mechanize.Browser(factory=mechanize.RobustFactory()) 
br.set_debug_http(True)

def lambda_handler(event, context):
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    br.open('https://www.plannedparenthood.org/')

    # Find donation link.
    donate_links = br.links(url_regex='Donation')
    if not donate_links:
        print "Error: no donation link found."
        exit(1)
    donate_link = next(donate_links)

    br.open(donate_link.url)
    br.select_form('process')
    
    # One-time donation of $5.
    br.form['gift_type'] = ['onetime']
    br.form['level_standardexpanded'] = ['30882']
    amount_ctrl = br.form.find_control(name='level_standardexpanded30882amount', type='text')
    amount_ctrl.value = '5'

    br.form['billing_first_namename'] = 'FIRST NAME'
    br.form['billing_last_namename'] = 'LAST NAME'

    br.form['billing_addr_street1name'] = 'ADDRESS'
    br.form['billing_addr_cityname'] = 'CITY'
    # Two letter state abbreviation, all caps.
    br.form['billing_addr_state'] = ['STATE ABBREV']
    br.form['billing_addr_zipname'] = 'ZIPCODE'
    
    br.form['donor_email_addressname'] = 'EMAIL'
    
    ccnum_ctrl = br.form.find_control(name='responsive_payment_typecc_numbername', type='text')
    ccnum_ctrl.value = CC_number

    br.form['responsive_payment_typecc_exp_date_MONTH'] = [CC_expiration_month]
    br.form['responsive_payment_typecc_exp_date_YEAR'] = [CC_expiration_year]
    
    cvv_ctrl = br.form.find_control(name='responsive_payment_typecc_cvvname', type='text')
    cvv_ctrl.value = CC_CVV
    
    response = br.submit()
    
    # Validate donation / form submission.
    if 'thank you' in response.read().lower():
        message = "Success! You donated $5 to Planned Parenthood :)"
    else:
        message = "Error: Your donation didn't go through :("

    # Send text message.
    sns.publish(PhoneNumber=phone_number, Message=message)
