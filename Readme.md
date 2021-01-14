Ertis Auth Initializer CLI
===

Ertis Auth Command Line Interface. 

# Package Index


## Migrate 

Init your database (mongodb) for using ertis auth.

If you are using ertis auth, you should create first membership, role and user.
This manually operation have some risks. 
    
* You may not be sure about Membership, user and role database models. 
* sys field. who is created that documents and when?
* You can forget database indexes before using. 

Ertis Auth CLI create first models and create mongodb indexes by your given mongodb connection string.

### Usage

#### Installation


```bash
$ pip install migrate
```

#### Help

```bash
$ migrate --help
```

#### Setup
```bash
$ migrate -c <mogno_connection_string> -d <datbase_name>

```
Then cli asks some questions to you. 

```bash
Initialize you ertis auth service.
? Enter a membership name:  ertis
? Enter a role name:  admin
? Enter a username:  admin
? Enter a password:  mySecretP@assWord!
? Enter token ttl value as a minutes:  60
? Enter refresh token ttl value as a minutes:  120
? Enter max active token count by user:  120
? Do you want create indexes on mongodb for ertis auth? [y|N]  True
```

You can check your mongodb collections and indexes after installation. 

> Note:  if you have memberships, roles and users collections already this cli will be created only documents. s
> And documents means new membership, new role under membership and new user under membership. 