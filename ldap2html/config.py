from dataclasses import dataclass


@dataclass
class Config:
    ldap_uri: str
    search_base: str
    bind_dn: str
    bind_dn_passwd: str

    directory: str
