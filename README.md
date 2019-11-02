# ldap2html

Schemas and tools to store HTML documents in LDAP.

## Sample

See [sample](./sample) directory.

## Schemas

### Common

- `htmlNthChild`: Position among the children (elements and texts)

### HTML Element

ObjectClass: `htmlNormalElement`, `HTMLVoidElement` (for elements without children like `br`)

- `ou`: Element name. `dn` will be the id of the element!
- `htmlTagName`: Tag name


#### Element attributes

You can set pre-defined HTML Element attributes to LDAP elements. Each LDAP attribute is named like `htmlAttr{HTMLAttribute}`.

Available LDAP attributes:

- `htmlAttrClass`

### Text

ObjectClass: `htmlText`

- `cn`: Identifier (required to set dn on LDAP, but is ignored on ldap2html)
- `htmlTextValue`: Text value

## Tools

### Setup

```cosnsole
$ pipenv install
```

### LDAP -> HTML

```console
$ pipenv run python3 main.py -h
usage: main.py [-h] [-H LDAP_URI] -b SEARCH_BASE -D BIND_DN -w BIND_DN_PASSWD
               [-d DIRECTORY]

Convert LDAP entries to HTML file

optional arguments:
  -h, --help            show this help message and exit
  -H LDAP_URI, --uri LDAP_URI
                        LDAP uri
  -b SEARCH_BASE, --searchbase SEARCH_BASE
                        LDAP search base
  -D BIND_DN, --binddn BIND_DN
                        LDAP bind dn
  -w BIND_DN_PASSWD, --passwd BIND_DN_PASSWD
                        LDAP bind dn password
  -d DIRECTORY, --dir DIRECTORY
                        Target directory to save files

```

### HTML -> LDAP

TODO

## Debug

### Setup LDAP environment via Docker

```console
$ docker run -p 389:389 -p 636:636 -v `pwd`:/app -v `pwd`/schema:/container/service/slapd/assets/config/bootstrap/ldif/custom \
    --env LDAP_DOMAIN="example.com" --rm --name ldap -it \
    osixia/openldap --copy-service
$ docker exec ldap2html ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w admin  -f /app/sample/helloworld.html.ldif
```
