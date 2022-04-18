#  betfair-application-development

Betfair data threatment API repository

##  Requirements
The project was maded using [Python 3.10.0](https://www.python.org/downloads/release/python-3100/), for a single use I recommend to run the virtual environment by the command:
#### Windows
```sh
.\ambvir\Scripts\activate.bat
```
#### Linux and Mac
```sh
./ambvir/Scripts/activate
```

If you want to run the code as part of another code, you can see the requirements at the requirements.txt file at root dir, or install it with
```sh
pip install -r requirements.txt
```
##  SSL certificates
As especified by betfair dev doc, you have to generate a self-signed certificate and then link the certificate to your Betfair account by following the steps:
### Generate Certificate File (CSR) With [openssl](https://www.openssl.org)
1. Create a certs inside the root directory of project (the same that have a app.py file)
2. Then run the commands inside the certs directory:
```sh
openssl genrsa -out client-2048.key
```
to create public or private RSA key using openssl.
3. Create a file named openssl.cnf inside the certs directory with
```txt
basicConstraints = CA:FALSE
nsCertType = client
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
```
4.  Llet's create the CSR file
```sh
openssl req -new -config openssl.cnf -key client-2048.key -out client-2048.csr
```
5. Then finally
```sh
openssl x509 -req -days 365 -in client-2048.csr -signkey client-2048.key -out client-2048.crt -extfile openssl.cnf -extensions ssl_client
```
\
You can also generate the certificate of the previous steps with [XCA](http://sourceforge.net/projects/xca/) an OpenSSL toolset as specified [here](https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Certificate+Generation+With+XCA).
### Register Generated CSR Within The Account
 1. After creating the CSR file, let's link the certificate with our
    Betfair account:
    
 2. Log in to your Betfair account through betfair.com. Paste the
        following URL into the address bar of your browser
 3. Navigate to
        https://myaccount.betfair.com/accountdetails/mysecurity?showAPI=1
 4. Scroll to the section titled “Automated Betting Program Access” and
        click 'Edit'
 5. Click on “Browse” and then locate and select the file
        client-2048.crt created above.
 6. Click on the “Upload Certificate” button.
 7. Scroll down to the “Automated Betting Program Access” section if
        required and the certificate details should be shown. You should now
        be able to log in to your Betfair account using the Betfair API
        endpoint.
