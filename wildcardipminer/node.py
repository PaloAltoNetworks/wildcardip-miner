import logging

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)


class _wildcard_ipv4(object):
    IPPART = 0
    NETPART = 1

    def _parse_ipnet(self, ip_netmask):
        net_parts = ip_netmask.split('/')
        if len(net_parts) != 2:
            raise ValueError('Invalid IPv4/netmask string "{}"'.format(ip_netmask))
        self._ip_part = [0L, 0L]
        for idx in range(2):
            parts = net_parts[idx].split('.')
            if len(parts) != 4:
                raise ValueError('Invalid IPv4/netmask string "{}"'.format(ip_netmask))
            for val in parts:
                int_value = int(val)
                if not 0 <= int_value < 256:
                    raise ValueError('Invalid IPv4/netmask string "{}"'.format(ip_netmask))
                self._ip_part[idx] = (self._ip_part[idx] << 8) + int_value
        # Let's get the tailing zeros in the mask
        self._hostbits = 0
        idx = 1L
        while idx & self._ip_part[1] == 0 and self._hostbits < 32:
            self._hostbits += 1
            idx <<= 1;
        if self._hostbits == 32:
            raise ValueError('Invalid IPv4/netmask string "{}"'.format(ip_netmask))
        # Time to create the list of zero slices in the mask
        self._total_bits = 0
        self._zero_slice = []
        bit_pointer = self._hostbits
        slice_start = 0
        counting_ones = True
        for bit_pointer in range(self._hostbits, 32):
            if counting_ones and idx & self._ip_part[1] == 0:
                counting_ones = False
                slice_start = bit_pointer
            if not counting_ones and idx & self._ip_part[1] != 0:
                self._zero_slice.append((slice_start, bit_pointer - slice_start))
                self._total_bits += bit_pointer - slice_start
                counting_ones = True
            idx <<= 1
        if not counting_ones:
            self._zero_slice.append((slice_start, 32 - slice_start))
            self._total_bits += 32 - slice_start
        self.size = 1 << self._total_bits

    def _generate_cdir(self, ip_object, masklen):
        return "{}.{}.{}.{}/{}".format(ip_object >> 24 & 0xffl,
                                       ip_object >> 16 & 0xffl,
                                       ip_object >> 8 & 0xffl,
                                       ip_object & 0xffl,
                                       masklen)

    def _iterate(self, ip, pending_slices):
        if len(pending_slices) > 1:
            current_slice = pending_slices[-1]
            for e in range(1 << current_slice[1]):
                for b in self._iterate(ip | e << current_slice[0], pending_slices[:-1]):
                    yield b
        else:
            for e2 in range(1 << pending_slices[0][1]):
                yield self._generate_cdir(ip | e2 << pending_slices[0][0], 32 - self._hostbits)

    def iterate(self):
        if len(self._zero_slice) == 0:
            return [self._generate_cdir(self._ip_part[0] & self._ip_part[1], 32 - self._hostbits)]
        return self._iterate(self._ip_part[0] & self._ip_part[1], self._zero_slice)

    def __init__(self, ip_netmask):
        self._parse_ipnet(ip_netmask)


class Miner(BasePollerFT):
    def configure(self):
        super(Miner, self).configure()
        self.wildcard_list = self.config.get('wildcard_list', [])
        self.max_entries = self.config.get('max_entries', 50000)
        self.wildcard_object = []
        self.size = 0
        for entry in self.wildcard_list:
            w_object = _wildcard_ipv4(entry)
            self.size += w_object.size
            self.wildcard_object.append(w_object)

    def _build_iterator(self, item):
        if self.size > self.max_entries:
            raise ValueError(
                'Wildcard list will generate {} entries. It is over the limit of {}.'.format(self.size,
                                                                                             self.max_entries))

        def main_loop():
            for o in self.wildcard_object:
                for e in o.iterate():
                    yield e

        return main_loop()

    def _process_item(self, item):
        indicator = item
        value = {
            'type': 'IPv4',
            'confidence': 100
        }

        return [[indicator, value]]
