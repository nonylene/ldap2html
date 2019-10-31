# ldap2html

WIP

## Schemas

### Common

- `x-html-nth`: Position between the children (elements and texts!)

### HTML Element

ObjectClass: `x-html-element`

- `ou`: Element name. `dn` will be the id of the element!
- `x-html-tag-name`: Tag name


#### HTML attributes

You can set defined HTML attributes to elements. Each LDAP attribute is named like `x-html-attr-{HTML attribute}`.

Available LDAP attributes:

- `x-html-attr-class`

### Text

ObjectClass: `x-html-text`

- `cn`: Identifier (required to set dn on LDAP, but ignored on ldap2html)
- `x-html-text-value`: Text value

## Debug

```console
$ docker run -v `pwd`:/app --env LDAP_DOMAIN="example.com" --rm --name ldap -it osixia/openldap
$ docker exec ldap ldapadd -Y EXTERNAL -H ldapi://  -f /app/schema/html.ldif
$ docker exec ldap ldapadd -x -H ldap://localhost -D "cn=admin,dc=example,dc=com" -w admin  -f /app/sample/index.html.ldif
```
