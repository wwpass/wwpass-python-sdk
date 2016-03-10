# WWPass Python SDK

The WWPass Web Application SDK for Python comprises examples, documentation and a library,  that is installed on a Service Provider’s system to allow authentication using the WWPass system. The WWPass Authentication Service is an alternative to, or replacement for, other authentication methods such as user name/password.

### Prerequisites
You have to register your site and receive **WWPass Service Provider (SP) credentials (certificate and private key)** at <https://developers.wwpass.com/>. If, for example, your site has the URL of "mysite.com" and you follow the recommended file naming convention when obtaining SP credentials, the files will be named as mysite.com.crt (for the certificate) and mysite.com.key (for the private key). The [WWPass CA certificate](https://developers.wwpass.com/downloads/wwpass.ca) should also be downloaded and made accessible to WWPass application. If you have root access to your computer, then the /etc/ssl folder is an appropriate place to store the certificates and the key.  Make sure that the script will have enough rights to read the files there. Usually access to /etc/ssl/private is quite limited.

The **WWPass PassKey** or **WWPass PassKey Lite** is a requirement for user authentication. 
**PassKey** is a hardware device that enables authentication and access for a given user.  A major component of the WWPass authentication capability is the software that supports the PassKey itself. Without this software, requests to an end user to authenticate their identity will fail since this software is used to directly access information stored on the PassKey and communicate with WWPass. To allow Administrator testing of the authentication infrastructure, this client software and an accompanying PassKey is required. 
**PassKey Lite** is an application for Android and iOS smartphones and tablets. The application is used to scan QR codes to authenticate into WWPass-enabled sites. Alternatively, when browsing with these mobile devices, you can tap the QR code image to authenticate into the site to access protected information directly on your phone or tablet. 
For more information about how to obtain a PassKey and register it, please refer to the WWPass web site (<http://www.wwpass.com>)  

### Installation
To install WWPass Python SDK run: `#python setup.py install`

### Licensing
Copyright 2016 WWPass Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Read more about WWPass Python SDK in WWPass-Python-SDK.md