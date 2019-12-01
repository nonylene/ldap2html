# ldap2html

Schemas and tools to store HTML documents in LDAP.

## Sample

- [sample](./sample) directory
- [ku-ldif/ku-ldif.github.io repository](https://github.com/ku-ldif/ku-ldif.github.io)

## Schemas

### HTML File

ObjectClass: `htmlFile`

- `o`: Filename.

### HTML Element

ObjectClass: `htmlNormalElement`, `HTMLVoidElement` (for elements without children like `br`)

- `ou`: Element name. `dn` will be the id of the element!
- `htmlTagName`: Tag name.
- `htmlNthChild`: (Optional) Position among the children (elements and texts).


#### Element attributes

You can set pre-defined HTML Element attributes to LDAP elements. Each LDAP attribute is named like `htmlAttr{HTMLAttribute}`.

Available LDAP attributes:

- `htmlAttrClass`
- `htmlAttrHref`
- `htmlAttrLang`

### Text

ObjectClass: `htmlText`

- `cn`: Identifier (required to set dn on LDAP, but is ignored on ldap2html).
- `htmlTextValue`: Text value.
- `htmlNthChild`: (Optional) Position among the children (elements and texts).

## Tools

### Setup

```cosnsole
$ poetry install [--no-dev]
```

### LDAP -> HTML

```console
$ poetry run ldap2html -h
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
  -v, --verbose         Verbose output
```

### HTML -> LDAP

```console
$ poetry run html2ldif -h
usage: html2ldif [-h] -n DOMAIN [-d DIRECTORY] [-m] [-v] file [file ...]

Convert LDAP entries to HTML file

positional arguments:
  file                  HTML files

optional arguments:
  -h, --help            show this help message and exit
  -n DOMAIN, --domain DOMAIN
                        Domain name for HTML files
  -d DIRECTORY, --dir DIRECTORY
                        Target directory to save files. Default value is
                        out/ldif.
  -m, --modify          Generate LDIF for ldapmodify
  -v, --verbose         Verbose output
```

## Develop

### Setup LDAP environment via Docker

```console
$ docker run -p 389:389 -p 636:636 -v `pwd`:/app -v `pwd`/schema:/container/service/slapd/assets/config/bootstrap/ldif/custom \
    --env LDAP_DOMAIN="example.com" --rm --name ldap -it \
    osixia/openldap --copy-service
$ docker exec ldap2html ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w admin  -f /app/sample/helloworld.html.ldif
```

### How to add HTML element attributes

1. Add `htmlAttr{AttrName}` LDAP attribute in [schema](./schema/html.ldif).
2. Add python model mapping to `LdapHTMLElement` in `ldap/model.py`.
3. Add python LDAP-HTML convertion mapping to `ELEMENT_ATTR_DICT` in `ldap/model.py`.
4. Document new attributes in README.
