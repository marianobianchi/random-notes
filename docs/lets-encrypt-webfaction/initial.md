## Manual way

Following these steps you are going to have a working webfaction https webpage
with a Let's Encrypt certificate. The idea is to have the certificates and
private keys in your webfaction account using your ssh account.

### What you have to know previously
* Configure a website in webfaction
* Access using ssh to your webfaction account
* Some linux commands


### Dependencies
We are going to use [letsacme](https://github.com/neurobin/letsacme). It is one of the [recommended scripts](https://letsencrypt.org/docs/client-options/) in the official
Let's Encrypt site.

To download it in your webfaction account, after login through ssh, follow these steps:

```
mkdir ~/letsacme
cd ~/letsacme
wget https://raw.githubusercontent.com/neurobin/letsacme/release/letsacme.py
wget https://github.com/neurobin/gencsr/archive/master.zip
unzip master.zip
```

### Proposed folder hierarchy
This is optional. We need to download/create some files so is good to organize
them somehow. This is my proposal:

```
mkdir -p ~/.letsencrypt/challenges/
mkdir -p ~/.letsencrypt/your.domain.here/
```

### Configure apache to your site
TODO

### Creating lets encrypt account key
```
openssl genrsa 4096 > ~/.letsencrypt/account.key
```

### Creating your domain keys
```
openssl genrsa 4096 > ~/.letsencrypt/your.domain.here/domain.key
```

### Generating a certificate request
```
cd ~/letsacme/gencsr
./gencsr -k ~/.letsencrypt/your.domain.here/domain.key -csr ~/.letsencrypt/your.domain.here/domain.csr
```

### Request signed certificate
```
cd ~/letsacme
python3 letsacme.py --no-chain --account-key ~/.letsencrypt/account.key --csr ~/.letsencrypt/your.domain.here/domain.csr --acme-dir ~/.letsencrypt/challenges/ > ~/.letsencrypt/your.domain.here/signed.crt
```
