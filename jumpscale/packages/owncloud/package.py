import toml
from pathlib import Path

PACKAGE_CONFIG_PATH = Path(__file__).parent.resolve() / 'package.toml'
class owncloud:
    def install(self, **kwargs):
        domain = kwargs.get('domain')
        letsencryptemail = kwargs.get('letsencryptemail')
        if not all([domain, letsencryptemail]):
            raise(f'usage: j.servers.threebot.default.packages.add(path="<package_path>", domain="<domain>", letsencryptemail="<letsencryptemail>")')
        
        with open(PACKAGE_CONFIG_PATH, 'rt') as f:
            parsed_toml = toml.load(f)
        
        if domain:
            parsed_toml['servers'][0]['domain'] = domain
            print(f"set the domain to {domain}")

        if letsencryptemail:
            parsed_toml['servers'][0]['letsencryptemail'] = letsencryptemail
            print(f"set the email to {letsencryptemail}")

        with open(PACKAGE_CONFIG_PATH, 'wt') as f:
            _ = toml.dump(parsed_toml, f)
        print('Package installation complete!')
