# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

# Copyright (C) 2005-2007, 2009-2011 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import struct
import binascii

import dns.rdata
import dns.immutable
import dns.rdatatype


@dns.immutable.immutable
class TLSA(dns.rdata.Rdata):

    """TLSA record"""

    # see: RFC 6698

    __slots__ = ['usage', 'selector', 'mtype', 'cert']

    def __init__(self, rdclass, rdtype, usage, selector,
                 mtype, cert):
        super().__init__(rdclass, rdtype)
        self.usage = self.as_value(usage)
        self.selector = self.as_value(selector)
        self.mtype = self.as_value(mtype)
        self.cert = self.as_value(cert)

    def to_text(self, origin=None, relativize=True, **kw):
        return '%d %d %d %s' % (self.usage,
                                self.selector,
                                self.mtype,
                                dns.rdata._hexify(self.cert,
                                                  chunksize=128))

    @classmethod
    def from_text(cls, rdclass, rdtype, tok, origin=None, relativize=True,
                  relativize_to=None):
        usage = tok.get_uint8()
        selector = tok.get_uint8()
        mtype = tok.get_uint8()
        cert = tok.concatenate_remaining_identifiers().encode()
        cert = binascii.unhexlify(cert)
        return cls(rdclass, rdtype, usage, selector, mtype, cert)

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        header = struct.pack("!BBB", self.usage, self.selector, self.mtype)
        file.write(header)
        file.write(self.cert)

    @classmethod
    def from_wire_parser(cls, rdclass, rdtype, parser, origin=None):
        header = parser.get_struct("BBB")
        cert = parser.get_remaining()
        return cls(rdclass, rdtype, header[0], header[1], header[2], cert)
