from jumpscale.loader import j
from jumpscale.sals.fs import pathlib
import toml

PACKAGE_CONFIG_PATH = pathlib.Path(__file__).parent.resolve() / 'package.toml'
class owncloud:
    def install(self, **kwargs):
        domain = kwargs.get('domain')
        letsencryptemail = kwargs.get('letsencryptemail')
        acme_url = kwargs.get('acme_url')
        j.logger.debug('Installing owncloud package..')
        if not all([domain, letsencryptemail]):
            j.logger.warning('One or more required parameters missing. Please provide domain and letsencryptemail')
            j.logger.warning(f'Usage: j.servers.threebot.default.packages.add(path="<package_path>", domain="<domain>", letsencryptemail="<letsencryptemail>")')
        
        with open(PACKAGE_CONFIG_PATH, 'rt') as f:
            parsed_toml = toml.load(f)
        
        if domain:
            parsed_toml['servers'][0]['domain'] = domain
            j.logger.debug(f"set the domain to {domain}")

        if letsencryptemail:
            parsed_toml['servers'][0]['letsencryptemail'] = letsencryptemail
            j.logger.debug(f"set the email to {letsencryptemail}")

        if acme_url:
            parsed_toml['servers'][0]['acme_server_type'] = "custom"
            parsed_toml['servers'][0]['acme_server_url'] = acme_url
            j.logger.debug(f"set the acme_url to {acme_url}")

        with open(PACKAGE_CONFIG_PATH, 'wt') as f:
            _ = toml.dump(parsed_toml, f)
        j.logger.info('owncloud package installed successfully!')
