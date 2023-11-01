import time

import keepasshttp
import sys
import pyperclip

if __name__ == '__main__':
    args = sys.argv[1:]  # Skip the script name itself at argv[0]
    #print('Arguments:', args)

    # get single credential
    #credential = keepasshttp.get("Paypal XIDA")
    #print(credential)
    #credentials = keepasshttp.search("https://www.paypal.com")
    credentials = keepasshttp.search(args[0])
    # check if the lenght of the list is 0
    if not credentials:
        print("No credentials found")
        sys.exit(1)
    # if length > 1
    if len(credentials) > 1:
        print("More than one credential found")
        sys.exit(1)

    #print(credentials)
    for credential in credentials:
        #print(credential.name)
        #print(credential.login)
        #print(credential.password)
        #print("-------------")

        pyperclip.copy("" + credential.password)
        time.sleep(0.5)
        pyperclip.copy("" + credential.login)
        sys.exit(1)


#with open('your_output_file.txt', 'w') as f:
#    f.write(credential.login + "|||" + credential.password)

