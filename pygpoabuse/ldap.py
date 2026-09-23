import logging
import asyncio

from msldap.commons.factory import LDAPConnectionFactory
from msldap.ldap_objects import MSADGPO


class Ldap:
    def __init__(self, url, gpo_id, domain):
        self.domain_dn = ",".join("DC={}".format(d) for d in domain.split("."))
        self.dn = 'CN={' + gpo_id + '}},CN=Policies,CN=System,{}'.format(self.domain_dn)
        conn_url = LDAPConnectionFactory.from_url(url)
        self.ldap_client = conn_url.get_client()

    async def connect(self):
        ok, err = await self.ldap_client.connect()
        if err is not None or not ok:
            logging.error("LDAP connection failed: %s", err)
            return False
        return True

    async def get_attribute(self, attribute):
        async for gpo, err in self.ldap_client.get_object_by_dn(self.dn, expected_class=MSADGPO):
            if err is not None:
                logging.error("Could not read %s: %s", attribute, err)
                return False
            return getattr(gpo, attribute, None)
        logging.error("GPO was not found while reading %s", attribute)
        return False

    async def update_attribute(self, attribute, value, old_value=None):
        if old_value is None:
            action = 'add'
        else:
            action = 'replace'
        # msldap's single_int encoder expects a scalar; multi_str expects a list.
        values = value if attribute == "versionNumber" else [value]
        ok, err = await self.ldap_client.modify(self.dn, {
            attribute: [(action, values)]
        })
        if err is not None or not ok:
            logging.error("Error while updating %s: %s", attribute, err)
            return False
        return True

    async def clear_attribute(self, attribute):
        ok, err = await self.ldap_client.modify(self.dn, {
            attribute: [('replace', [])]
        })
        if err is not None or not ok:
            logging.error("Error while clearing %s: %s", attribute, err)
            return False
        return True
