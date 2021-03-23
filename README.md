# Vendorlist explorer

A Flask application to run the Vendorlist explorer. See live version here: https://vendorlistexplorer.site.

This website extracts information from the vendorlist of IAB Europe Transparency & Consent Framework and makes this information human-readable. The goal is to provide Data Protection Agencies, privacy researchers and activists a tool to easily get statistics on purpose declarations by advertisers and their legal basis, and obtain lists of vendor in potentiel violation of the GDPR and other European laws. This website get automatically updated with the latest vendorlist every week.

Associated paper: *Purposes in IAB Europe's TCF: which legal basis and how are they used by advertisers?*  
Célestin Matte*, Cristiana Santos*, Nataliia Bielova (*co-first authors)  
APF'20 (Annual Privacy Forum)  
[![paper](static/pdf_32.png?raw=true "Paper")](https://hal.inria.fr/hal-02566891/document)
[![slides](static/slides.png?raw=true "Slides")](https://ploudseeker.com/files/docs/slides_APF.pdf)
[![video](static/video_32.png?raw=true "Video")](https://youtu.be/pTMKmRp4pSI)

Author: [Célestin Matte](https://cmatte.me)

This repository contains:
- a script to automatically download TCFv2 vendorlists and import them into a database,
- the Web application to display statistics about advertisers declarations in these vendorlists

## Dependencies
- Flask
- python-sqlalchemy
- MySQL/MariaDB

## Install


### Database

Create a database, create database user and give it access right to the `iabsite` catabase:
```sql
CREATE DATABASE iabsite;
CREATE USER '<user>'@localhost IDENTIFIED BY '<password>';
GRANT ALL ON iabsite.* TO '<user>'@localhost;
```
The database tables will be created automatically when the first vendorlist is imported.

### Vendorlists downloading
- fill `config.conf.example` and rename it `config.conf`
- In your crontab, add a line to execute `download_import_vendorlists.sh` every week:
```
45 17 * * 4 /path/to/vendorlistexplorer/download_import_vendorlists.sh
```

You can also download vendorlists manually (they're all stored on the following address: https://vendor-list.consensu.org/v2/archives/vendor-list-vVERSION.json where VERSION is the version number). Then import them using:
```bash
python import_vendorlist.py vendor-list-vVERSION.json
```

If you want to download older vendorlists, this is pretty straightforward since they all remain on IAB's server:
```bash
for i in $(seq 1 68) ; do wget -O vendorlistv2_"$i".json https://vendor-list.consensu.org/v2/archives/vendor-list-v"$i".json ; done
```

### Web application
- run `iabsite.py`:
```bash
python iabsite.py
```
- App is now reachable on address http://127.0.0.1:5000/

If you want it to run inside apache2:
- fill `iabsite.wsgi.example` and rename it `iabsite.wsgi`
- follow these instructions: https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/
See also an example VirtualHost config file for apache in `apache_example_config.conf`.
