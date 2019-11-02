from .model import LdapBase, from_ldap_entry
import dataclasses
from typing import Set, Type, Iterable
import ldap3


def _get_atrributes(cls: Type[LdapBase]) -> Set[str]:
    return {
        field.name for field in dataclasses.fields(cls)
        # dn is not included here
        if field.name != 'dn'
    }


def search(
        conn: ldap3.Connection, search_base: str, search_filter: str, cls: Type[LdapBase]
) -> Iterable[LdapBase]:
    # Set search_scope as LEVEL (one for ldapsearch) to get direct children.
    conn.search(search_base, search_filter, attributes=_get_atrributes(cls), search_scope=ldap3.LEVEL)
    return (from_ldap_entry(entry, cls) for entry in conn.entries)
