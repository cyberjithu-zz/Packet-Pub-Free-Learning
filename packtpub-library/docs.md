activate the virtual env

install the dependencies

# Create DB
```
	// Switch to postgres account
	sudo -i -u postgress

	//Run PostgreSQL command line client.
	psql

	//create role
	create user packtpubuser with password 'mypackTpubp@ssW0rd';

	//create db and make the packtpubuser as the owner of the db
	create database packtpubdb owner packtpubuser encoding 'utf-8';

```