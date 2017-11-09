# wildcardip-miner
Extension that generates CIDR variances out of a list of IPv4 wildcards (IP/mask)

## How it works

It parses each IPv4 string (A.B.C.D/M.M.M.M). Each "zero" in the mask is replaced by a unique variance.

In example, 10.0.10.0/255.252.255.0 will generate the following list of entries
- 10.0.10.0/24
- 10.1.10.0/24
- 10.2.10.0/24
- 10.3.10.0/24


## Installation

Add it as an external extension as introduced in [MineMeld 0.9.32](https://live.paloaltonetworks.com/t5/MineMeld-Discussions/What-s-new-in-MineMeld-0-9-32/td-p/141261 "What's new in MineMeld 0.9.32")

Use the **git** option with the URL of this repository ( https://github.com/PaloAltoNetworks/wildcardip-miner.git )