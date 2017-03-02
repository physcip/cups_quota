This is a small Python script to be used as a deamon to enact printing quotas for CUPS. It tracks CUPS' _page_log_ and maintains a SQLite database to store the printed pages for each user.
You can supply an external command to take away printer access from a user when the page quota is reached.

The script handles log rotations properly.
The timezone information in the log's time information is not currently taken into account.

# Setup on Mac OS X Server 10.8
## Web interface
	cd /Library/Server/Web/Data/WebApps
	git clone git@github.com:rempferg/cups_quota.git
	cd cups_quota
	cp cups_quota.conf.example cups_quota.conf
	# Edit configuration file cups_quota.conf, provide password for LDAP user
	cd /Library/Server/Web/Config/apache2/webapps
	sudo ln -s ../../../Data/WebApps/cups_quota/osx/de.uni-stuttgart.physcip.cupsquota.plist .

Enable the webapp in Server.app and restart the web server.

## Daemon and cron job

	cd /Library/Server/Web/Data/WebApps/cups_quota
	sudo cp osx/de.uni-stuttgart.physcip.cupsquota.*.plist /Library/LaunchDaemons
	cd /Library/LaunchDaemons
	sudo chown root:wheel de.uni-stuttgart.physcip.cupsquota.*.plist
	sudo chmod 644 de.uni-stuttgart.physcip.cupsquota.*.plist
	for f in de.uni-stuttgart.physcip.cupsquota.*.plist; do sudo launchctl load $f; done
