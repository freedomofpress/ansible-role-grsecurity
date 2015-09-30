#!/usr/bin/env python
DOCUMENTATION = '''
---
module: grsecurity_urls
short_description: Gather facts for grsecurity URLs
description:
  - Gather version and URL info for current grsecurity kernel patches
author:
    - Conor Schaefer (@conorsch)
    - Freedom of the Press Foundation (@freedomofpress)
requirements:
    - lxml
    - requests
options:
  patch_type:
    description:
      - branch of grsecurity kernel patches. Can be "test" or "stable".
    default: "test"
    choices: [ "test", "stable" ]
    required: no
notes:
  - The Linux kernel version is dependent on the grsecurity patch type.
    Using the `test`
'''
EXAMPLES = '''
- action: grsecurity_urls
- action: grsecurity_urls patch_type=test
- action: grsecurity_urls patch_type=stable
'''

from StringIO import StringIO
from urlparse import urljoin
import re

HAS_REQUESTS = True
HAS_LXML = True
try:
    import requests
except ImportError:
    HAS_REQUESTS = False
try:
    from lxml import etree
except ImportError:
    HAS_LXML = False


GRSECURITY_BASE_URL = 'https://grsecurity.net/'
GRSECURITY_RSS_FEED = 'https://grsecurity.net/{}_rss.php'
GRSECURITY_TEST_URL = 'https://grsecurity.net/test/'
GRSECURITY_STABLE_URL = 'https://grsecurity.net/download-restrict/download-redirect.php?file='
GRSECURITY_FILENAME_REGEX = re.compile(r'''
                                        grsecurity-
                                        (?P<grsecurity_version>\d+\.\d+)-
                                        (?P<linux_kernel_version>\d+\.\d+\.\d+)-
                                        (?P<grsecurity_patch_timestamp>\d{12})\.patch
                                        ''', re.VERBOSE)
LINUX_KERNEL_BASE_URL = "https://www.kernel.org/pub/linux/kernel/"


class LinuxKernelURLs():

    def __init__(self, linux_kernel_version):
        self.linux_kernel_version = linux_kernel_version
        self.ansible_facts = dict(
            linux_kernel_version=self.linux_kernel_version,
            linux_major_version=self.linux_major_version,
            linux_tarball_filename=self.linux_tarball_filename,
            linux_tarball_signature_filename=self.linux_tarball_signature_filename,
            linux_tarball_signature_url=self.linux_tarball_signature_url,
            linux_tarball_url=self.linux_tarball_url,
            )

    @property
    def linux_base_url(self):
        return urljoin(LINUX_KERNEL_BASE_URL, "v{}.x".format(self.linux_major_version))


    @property
    def linux_major_version(self):
        return self.linux_kernel_version.split('.')[0]


    @property
    def linux_tarball_filename(self):
        return "linux-{}.tar.xz".format(self.linux_kernel_version)


    @property
    def linux_tarball_url(self):
        return urljoin(self.linux_base_url, self.linux_tarball_filename)


    @property
    def linux_tarball_signature_filename(self):
        return "linux-{}.tar.sign".format(self.linux_kernel_version)

    @property
    def linux_tarball_signature_url(self):
        return urljoin(self.linux_base_url, self.linux_tarball_signature_filename)


class GrsecurityURLs():

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.ansible_facts = self.parse_grsecurity_rss_feed()

        if not self.ansible_facts:
            msg = """Could not parse grsecurity RSS feed. Inspect manually.
                  {}""".format(self.rss_feed_url)
            raise Exception(msg)


    @property
    def rss_feed_url(self):
        feed_identifier = ''
        if self.patch_type == "test":
            feed_identifier = "testing"
        else:
            feed_identifier = "stable2"
        return GRSECURITY_RSS_FEED.format(feed_identifier)


    @property
    def rss_feed_content(self):
        r = requests.get(self.rss_feed_url)
        return r.content


    def parse_grsecurity_rss_feed(self):
        """
        Figure out RSS URL based on patch_type, then parse it and return facts.
        """
        doc = etree.parse(StringIO(self.rss_feed_content))
        xmlroot = doc.getroot()

        def extract_xml_element(elem):
            try:
                return xmlroot.xpath('.//channel/item/{}'.format(elem))[0].text
            except IndexError:
                msg = "Could not find element '{}' in RSS feed".format(elem)
                raise Exception(msg=msg)

        config = dict()
        config['grsecurity_patch_filename'] = extract_xml_element('title')
        config['grsecurity_patch_url'] = extract_xml_element('link')
        config['grsecurity_signature_filename'] = config['grsecurity_patch_filename'] + '.sig'
        config['grsecurity_signature_url'] = config['grsecurity_patch_url'] + '.sig'
        config.update(re.match(GRSECURITY_FILENAME_REGEX,
                               config['grsecurity_patch_filename']).groupdict())
        return config


def main():
    module = AnsibleModule(
        argument_spec=dict(
            patch_type=dict(default="test", choices=["test", "stable"]),
        ),
        supports_check_mode=False
    )
    if not HAS_REQUESTS:
      module.fail_json(msg='requests required for this module')

    if not HAS_LXML:
      module.fail_json(msg='lxml required for this module')

    patch_type = module.params['patch_type']
    grsec_config = GrsecurityURLs(patch_type=patch_type)
    linux_config = LinuxKernelURLs(
            linux_kernel_version=grsec_config.ansible_facts['linux_kernel_version']
            )
    grsec_config.ansible_facts.update(linux_config.ansible_facts)

    results = grsec_config.ansible_facts

    if results:
        module.exit_json(changed=False, ansible_facts=results)
    else:
        msg = "Failed to fetch grsecurity URL facts."
        module.fail_json(msg=msg)

from ansible.module_utils.basic import *
main()
