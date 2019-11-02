# ldap2html

WIP

## Schemas

### Common

- `htmlNth`: Position among the children (elements and texts)

### HTML Element

ObjectClass: `htmlElement`

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

## Debug

### Setup LDAP environment via Docker

```console
$ docker run -v `pwd`:/app -p 389:389 -p 636:636 --env LDAP_DOMAIN="example.com" --rm --name ldap2html -it osixia/openldap
$ docker exec ldap2html ldapadd -Y EXTERNAL -H ldapi:// -f /app/schema/html.ldif
$ docker exec ldap2html ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w admin  -f /app/sample/helloworld.html.ldif
```
