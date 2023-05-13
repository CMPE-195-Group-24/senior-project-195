### Website Interface
---

##### Website Description
The website interface is created to allow administrators in an oragnization and/or root users to manage the personnels within an organization through creating accounts and maaging their information and access to a door.

---

##### Content
Folders:
* static
	* css &rarr; CSS files for website
	* pictures &rarr; Contains pictures used in the website
* template &rarr; Contains all HTML pages for the website

Files:
* auxiliary_functions.py &rarr; contains Support functions (blocks of code to simply as a function call for redundant calls)
* database_config.yaml &rarr; contains information of the specific database the web interface will utilize from AWS RDS
* database_functions.py &rarr; contains support functions for database interaction from AWS RDS
* webapp.wsgi &rarr; Web server gateway interface configuration file for Web Server on AWS EC2
* web_main.py &rarr; contains the code that frames the website (main file that brings all files together to run as a whole)
* requirements.txt &rarr; contains all the python packages to install via CLI.
* \_\_init\_\_.py &rarr; File to provide path for initalizing website interface (not initalizing virtual host; essentially providing the path for website interface upon enabling virtual host)

---

##### How to Host the Website Interface on a Web Server
Source: https://youtu.be/YFBRVJPhDGY (by [Tech With Tim](https://www.youtube.com/@TechWithTim))

1. [Create an AWS EC2 Instance](https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html)

2. Log into the AWS EC2 via a Command Line Interface (CLI). Download and Install Apache using the following commands...
```
sudo apt update
sudo apt install apache2
apache2 -version
```

3. Configure Firewall
```
sudo ufw app list
sudo ufw allow 'Apache'
```

4. Configure apache
```
sudo systemctl status apache2
```

5. Install and enable mod_wsgi
```
sudo apt-get install libapache2-mod-wsgi-py3 python3-dev
```

6.   Creating flask app
```
cd /var/www
sudo mkdir webApp
cd webApp
```

7. Put all content of Flask config in "/var/www/webApp"

	- static
	- templates
	- [ Main file for running framework ]
	- \_\_init\_\_.py

```
sudo vi /var/www/webApp/webapp.wsgi
```
In *\_\_init\_\_.py*:
```
from .web_main import app
```
*Press "Esc" and type ":x" and press enter to save.*

8. Install flask
```
sudo apt-get install python-pip
sudo pip install Flask
```

9. Use [WinSCP](https://winscp.net/eng/download.php) to transfer python files to server

10. Configure virtual host
```
sudo vi /etc/apache2/sites-available/webApp.conf
```

In "/etc/apache2/sites-available/webApp.conf":
```
<VirtualHost *:80>
		ServerName ip
		ServerAdmin email@mywebsite.com
		WSGIScriptAlias / /var/www/webApp/webapp.wsgi
		<Directory /var/www/webApp/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/webApp/static
		<Directory /var/www/webApp/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
*Press "Esc" and type ":x" and press enter to save.*

11. Install the required Python packages using the following command: `pip install --pre -r requirements.txt`

12. Enable Virtual Host
```
sudo a2ensite /var/lib/webApp
systemctl reload apache2
```

13. Create .wsgi file
```
sudo vi webapp.wsgi
```

In webapp.wsgi:
```
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/webApp/")

from webApp import app as application
application.secret_key = 'Add your secret key'
```
*Press "Esc" and type ":x" and press enter to save.*

14. Restart and reload apache
```
sudo service apache2 restart
sudo service reload apache2
```
