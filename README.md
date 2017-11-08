# wildcardipv4-miner
Extension that generates CIDR variances out of a list of IPv4 wildcards (IP/mask)

## How it works

It parses each IPv4 string (A.B.C.D/M.M.M.M). Each "zero" in the mask is replaced by a unique variance.

In example, 10.0.10.0/255.252.255.0 will generate the following list of entries
- 10.0.10.0/24
- 10.1.10.0/24
- 10.2.10.0/24
- 10.3.10.0/24
