import os
import re

from ansible import errors


def extract_kernel_version(deb_package):
    """
    Read filename for linux-image Debian package and return only
    the kernel version it would install, e.g. "4.4.4-grsec".
    """

    # Convert to basename in case the filter call was not prefixed with '|basename'.
    deb_package = os.path.basename(deb_package)
    try:
        results = re.findall(r'^linux-image-([\d.]+-grsec)', deb_package)[0]
    except IndexError:
        msg = ("Could not determine desired kernel version in '{}', make sure it matches "
              "the regular expression '^linux-image-[\d.]+-grsec'").format(deb_package)
        raise errors.AnsibleFilterError(msg)

    return results


class FilterModule(object):
    def filters(self):
        return {
            'extract_kernel_version': extract_kernel_version
        }
