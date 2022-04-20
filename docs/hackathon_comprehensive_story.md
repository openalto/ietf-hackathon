# Hackathon comprehensive story 

ATLAS [[2]](#2) experiment is one the four major scietific experiments at the Large Hadron Collider (LHC) [[3]](#3) at CERN [[4]](#4). Atlas generates more than one petabyte of data every day [[5]](#5), and has  unprecedentedly heterogenous computing and storage needs, because in addition to massive volume, **data generation, storage, access, and processing locations are divergent.**

Rucio is built on top of Atlas storage systems to s**calably and efficiently manage the replication and archiving of the created data and administer accesses to the data**. "**One of the guiding principles of Rucio is data flow autonomy and automation**": As a result, Rucio provides a unified interface for accessing and controlling the underlying diversified networking and storage services (such as XRootD and S3). Scientists and admins then manage data replication and access with Rucio integrated modules, **without dealing with underlying complexitites**.   

To optimize metrics (cost, speed, etc.) **Rucio collects various information about the network and storage devices** that guide _data 1st) identifier transfers between sites (RSEs) and 2nd) source selections before downloads_ [[8]](#8). Most important collected measures are distances between RSEs (Rucio Storage Elements), **according to the aggregated download throughput between RSEs or geographical location databases** [[1]](#1). However, such metrics are (static and non-informative) as they might get stale and do not reflect cost parameters that Alto offers. 

ALTO (Application-Layer Traffic Optimization) framework collects network information and exposes it to applications to steer traffi: **So we believe that ALTO integration in the Rucio environment, can improve transfer metrics.** ALTO is currently used in multiple large-scale systems such as ...

At IETF 113 Hackathon event, ALTO is used to provide Rucio's replication sorting and transfer scheduling parts with more accurate and up-t-date information about the network state (distances and available bandwidth). [Evaluation results](#Evaluations) showed that Alto-based replica sorting decreases replica transfer times by up to 66% (depending on the network structure and the bottlenecks). 

In this document, we first describe the components of the devised system and then present the experiments setup and evaluation results. 

## Infrastructure and the Transfer services
Rucio manages large volume data transfers of the ATLAS experiment. ATLAS infrastructure comprises a wide variety of storage and network systems. In this section, we briefly introduce these systems. Then provide a detailed description of our development environment networking and storage components.  

### Storage Systems 

ATLAS comprises a wide variety of storage systems, such as XRootD, EOS, and dCache. These systems use multiple protocols to manage data accesses, such as S3, ROOT, and Gsiftp. A more detailed list can be found on [[1]](#1). Rucio has interfaces to all of the mentioned systems. An up-to-date list of implemented systems and protocols is on Rucio's code-base [[11]](#11).

Rucio development environment uses XRootD storage instances [[12]](#12). Although our contributions to Rucio are not dependent on a specific storage system on the specific, we adapted the same containers to maximize environment compatibility and to comply with Rucio's development guidelines.

#### XRootD 
XRootD is a highly-configurable, scalable and high performance data server used by sites in OSG. Rucio interfaces with XRootD through xrdfs command [[15]](#15) (see the regarding implementation on [[14]](#14)). Scalla paper [[13]](#13) provides a architectural reference for the components of XRootD architecture and its scalable cluster management. You can also find reference on how XRootD is used on OSG experiments including ATLAS on [[17]](#17).

#### FTS 

In high energy physics experiments, TPS (Third party copy) over HTTP is used to overcome GridFTP limitations and provides Tbps rate data transfer between sites by 2027 [[18]](#18). FTS ([[19]](#19) and [[20]](#20)) is the TPS solution of LHC that distributes data over LHC computation grid (WLCG). Rucio uses FTS to submit bulk transfer requests between sites [[1]](#1). Rucio development environment includes FTS image.  

### Networking

#### Research Networks
LHC utilizes multiple National Research and Education networks (including ESnet, and Geant) to provide connectivity between data collection and processing sites. This network scales to an aggregated link capacity of 2Tbps and has specific peering points to commercial cloud providers for low-latency data accesses [[1]](#1). Although Rucio manages rule-based data transfers on these networks, it does not have access to the real-time network metrics for efficient or cost-optimized transfer schdeduling. Our ultimate goal in this study is to forify Rucio network information base and enable optimized transfer scheduling.

#### Mininet 
Mininet simulates a realistic virtual network with desired metrics on VMs. We use Mininet as the underlying network between XRD servers and endhosts (as depicted in ... ) to realisticly simulate link capacities and bottleneck strcutures in this study. Containernet (a Mininet extension) is used to enable docker containers as Mininet end hosts. We also used G2-mininet to simplify setting up mininet topologies. G2 is a flow optimization framework based gradient that formulates bottleneck structures in a network. For a detailed description on the environment setup please refer to [[23]](#23).

### Rucio 


#### Data Identifiers
Rucio namespace comprises DIDs (data identifiers) with different granularities. DIDs can either be files containing immutable experiment data, a collection of files (datasets), or a set of datasets (containers). Each DID consists of a unique string tuple divided by a colon indicating a scope (experimental data or simulation data for example) and a name. Each DID will be replicated on multiple (possibly zero) locations on the ATLAS storage systems. Replication of the data inside Rucio obeys the replication rules. More details on how Rucio manages namespace, access lists and accounting is out of scope for this document, but reader can refer to the Rucio's documentation, reference paper, or source code.

#### Resource Storage Elements
RSE (Resource Storage Element) is an abstraction for the minimal level of the addressable storage system in Rucio's underlying storage and networking systems [[1]](#1). Each DID will eventually be replicated on some RSEs. 

#### Rucio DID Transfers 
Data identifiers in Rucio are transferred from RSE to RSE or downloaded from RSEs to the end hosts. DID transfers are requested by the replication rules to keep the namespace coherent, whereas downloads are initiated by scientists from local sites to copy experiments data. In IETF 113 hackathon the team only focused on DID downloads.

Rucio collects system state information to optimize DID transfers. Rucio also uses different [Replica sorting](https://github.com/rucio/rucio/blob/master/lib/rucio/core/replica_sorter.py) functions to find the best possible download source for a given DID and recommend it to the researchers.


#### Replication Rules
Rucio formally expresses the requirements for the experiments' data replications with the complete language of the replication rules ([[1]](#1)-[[23]](#23)). A replication rule consists of four parts, denoting a set of DIDs, their acceptable destination RSEs, the number of desired replicas, and an availability deadline (after which data would no longer be required.) 

#### Replica sorting
Scientists can download data identifiers manifestation on a specific RSE from end hosts. Replica sorter returns a sorted list of PFNs on different RSEs based on different distance measures between the scientist location and the destination RSEs. Scientists then download the DID from the best candidate PFN based on replica sorter recommendations. [[24]](#24) documents `rucio list-file-replicas` specs. OpenAlto IETF113 environment setup document shows replica sorter output in detail [[25]](#25). Native replica sorter implementation includes several sorting functions based on static IP measures, most importantly GeoIP city distance [[26]](#26). 

However, GeoIP distances are inherently unreliable due to low accuracy (only in Switzerland 25% of the entries are incorrectly resolved [[27]](#27)). We aim to augment distance metrics accuracy using ALTO provided information to enable more efficinet downloads.

##### Transfer Scheduling

### ALTO Server 
Application Layer Traffic Optimization (ALTO) is a protocol that expose network information to ISPs to steer traffic efficiently. ALTO uses **Cost Maps** ([sample](https://github.com/openalto/pyalto-client/blob/main/examples/cm.json)) and **Network Maps** ([sample](https://github.com/openalto/pyalto-client/blob/main/examples/nm.json)) abstractions to report requested measures to the clients [[9]](9). Sextant is an open source implementation of ALTO that works on [Opendaylight](https://www.opendaylight.org/).

### ALTO Client 
Alto client [[28]](#28) is a python library that enables access to the ALTO server and fetches cost maps and network maps. 

### Topology
Sextant can extract information from general topologies, however in IETF hackathon 113 a simple topology is used to demonstrate ALTO replication sorting effectiveness.

```
              Rucio
      1Mbps    |     5Mbps
      25ms     |     25ms
  s1 --------- s3 ----------- s4 -- XRD3
  |            |              |
  |            | 25ms         | 50ms
  |            | 1Mbps        | 2Mbps
  |            |              |
 XRD1          s2 -- XRD2     s5 -- XRD4
```
*Architecture for the mininet of the demo environment*

#### G2 Mininet

G2 (Gradient Graph) ([[29]](#29), [[30]](#30), [[31]](#31)) is a framework for network optimization through bottleneck structures. ALTO and G2 complete each other as information extraction and information based optimization frameworks. G2 mininet is a module that simplifies mininet network configurations and executions with **topologies**, **network schemas** and **flow configurations** [[32]](#32) and has lots of [interesting topologies](https://github.com/reservoirlabs/g2-mininet/tree/master/experiments) (like [Google B4](https://github.com/reservoirlabs/g2-mininet/blob/master/experiments/g2_network01/input/g2.conf)) preimplemented. More information on how G2 mininet can be integrated in the Rucio+ALTO demo environment can be found on [[25]](#25) [here](https://github.com/openalto/ietf-hackathon/blob/main/docs/environment_setup.md).

## Demos
Over the course of IETF hackathon 113 three demos have been implemented to demonstrate the effects of ALTO and the provided information on Rucio replica download. These demos are respectively designed to: 
> 1- Add alto cost maps to sort replicas based on **dynamic** network information provided by the ALTO server. [](link to specific document)

> 2- Given a list of flows between RSEs and end terminals (link to specific document), transfer rates are estimated using network utility fuctions. [](link to specific document)

> 3- Iteratively search download options for different DIDs and a set of terminals to find a viable solution with respect to minimum acceptable download rates (transfer deadlines). [](link to specific document)

## Conclusoin 
During IETF hackathon 113, use cases of **dynamic** network information (collected and reflected via ALTO server) were demonstrated.


## Future Work

## References
<a id="1">[1]</a> 
Barisits, Martin, et al. “Rucio: Scientific Data Management.” Computing and Software for Big Science, vol. 3, no. 1, Aug. 2019, p. 11. Springer Link, https://doi.org/10.1007/s41781-019-0026-3.

<a id="2">[2]</a> Collaboration, The ATLAS, et al. “The ATLAS Experiment at the CERN Large Hadron Collider.” Journal of Instrumentation, vol. 3, no. 08, Aug. 2008, pp. S08003–S08003. DOI.org (Crossref), https://doi.org/10.1088/1748-0221/3/08/S08003.

<a id="3">[3]</a> Evans, Lyndon, and Philip Bryant. “LHC Machine.” Journal of Instrumentation, vol. 3, no. 08, Aug. 2008, pp. S08001–S08001. DOI.org (Crossref), https://doi.org/10.1088/1748-0221/3/08/S08001.

<a id="4">[4]</a> European Organization for Nuclear Research (CERN). https://home.cern/. Accessed 28 Mar. 2022.

<a id="5">[5]</a> by Mélissa Gaillard and Stefania Pandolfi. CERN Data Centre Passes the 200-Petabyte Milestone. 2017. https://cds.cern.ch/record/2276551

<a id="6">[6]</a> XRootD collaboration | XRootD. https://xrootd.slac.stanford.edu/. Accessed 28 Mar. 2022.

<a id="7">[7]</a> Replica Management with Replication Rules | Rucio Documentation. https://rucio.github.io/documentation/replica_management. Accessed 28 Mar. 2022.

<a id="8">[8]</a> Rucio C3PO daemon information collectors “Rucio/Lib/Rucio/Daemons/C3po/Collectors at Master · Rucio/Rucio.” GitHub, https://github.com/rucio/rucio. Accessed 29 Mar. 2022.

<a id="8">[9]</a> Alimi, R., Ed., Penno, R., Ed., Yang, Y., Ed., Kiesel, S., Previdi, S., Roome, W., Shalunov, S., and R. Woundy, "Application-Layer Traffic Optimization (ALTO) Protocol", RFC 7285, DOI 10.17487/RFC7285, September 2014, <https://www.rfc-editor.org/info/rfc7285>

<a id="10">[10]</a> FTS Codebase, “CERN FTS.” GitHub, https://github.com/cern-fts. Accessed 31 Mar. 2022.

<a id="11">[11]</a> Rucio RSE description and management - “Rucio/Lib/Rucio/Rse/Protocols at Master · Rucio/Rucio.” GitHub, https://github.com/rucio/rucio. Accessed 4 Apr. 2022.

<a id="12">[12]</a> Setting up a Rucio Demo Environment | Rucio Documentation. https://rucio.github.io/documentation/setting_up_demo. Accessed 4 Apr. 2022.

<a id="13">[13]</a> Boeheim, Chuck et al. “Scalla : Scalable Cluster Architecture for Low Latency Access Using xrootd and olbd Servers.” (2006).

<a id="14">[14]</a> Rucio XRootD interface implementation - “/lib/rucio/rse/protocols/xrootd.py at Master · Rucio/Rucio.” GitHub, https://github.com/rucio/rucio. Accessed 4 Apr. 2022.

<a id="15">[15]</a> Xrdfs command manual page. https://xrootd.slac.stanford.edu/doc/man/xrdfs.1.html. Accessed 4 Apr. 2022.

<a id="16">[16]</a> “The XRootD Collaboration.” GitHub, https://github.com/xrootd. Accessed 4 Apr. 2022.

<a id="17">[17]</a> XRootD Overview - OSG Site Documentation. https://opensciencegrid.org/docs/data/xrootd/overview/. Accessed 4 Apr. 2022.

<a id="18">[18]</a> “Third Party Copy.” Institute for Research and Innovation in Software for High Energy Physics, http://iris-hep.org/projects/tpc.html. Accessed 4 Apr. 2022.

<a id="19">[19]</a> Ayllon, A. A., et al. "FTS3: new data movement service for WLCG." Journal of Physics: Conference Series. Vol. 513. No. 3. IOP Publishing, 2014.

<a id="20">[20]</a> Introduction | FTS3 Documentation. https://fts3-docs.web.cern.ch/fts3-docs/. Accessed 4 Apr. 2022.

<a id="21">[21]</a> “Containernet.” Containernet, https://containernet.github.io/. Accessed 4 Apr. 2022.

<a id="22">[22]</a> “Containernet code-base.” GitHub, https://github.com/containernet/containernet. Accessed 4 Apr. 2022.

<a id="23">[23]</a> Barisits, Martin, et al. "ATLAS replica management in Rucio: replication rules and subscriptions." Journal of Physics: Conference Series. Vol.  513. No. 4. IOP Publishing, 2014.

<a id="24">[24]</a> Rucio CLI — Rucio 1.2 Documentation. https://rucio.readthedocs.io/en/latest/man/rucio.html#list-file-replicas. Accessed 11 Apr. 2022.

<a id="25">[25]</a> “Ietf-Hackathon/Docs at Main · Openalto/Ietf-Hackathon.” GitHub, https://github.com/openalto/ietf-hackathon. Accessed 11 Apr. 2022.

<a id="26">[26]</a> GeoLite DB: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data?lang=en. Accessed 11 Apr. 2022.

<a id="27">[27]</a> “ALTO Open Source Community - Sextant Repository” GitHub, https://github.com/openalto/sextant. Accessed 11 Apr. 2022.r

<a id="28">[28]</a> “Pyalto client - ALTO Open Source Community.” GitHub, https://github.com/openalto. Accessed 11 Apr. 2022.

<a id="29">[29]</a> J. Ros-Giralt, A. Bohara, S. Yellamraju, H. Langston, R. Lethin, Y. Jiang, L. Tassiulas, J. Li, Y. Lin, Y. Tan, M. Veeraraghavan, "On the Bottleneck Structure of Congestion-Controlled Networks," ACM SIGMETRICS, Boston, June 2020.

<a id="30">[30]</a> Jordi Ros-Giralt, Noah Amsel, Sruthi Yellamraju, James Ezick, Richard Lethin, Yuang Jiang, Aosong Feng, Leandros Tassiulas, Zhenguo Wu, Min Yeh Teh, Keren Bergman, "Designing Data Center Networks Using Bottleneck Structures," Accepted for publication at ACM SIGCOMM 2021.

<a id="31">[31]</a> Jordi Ros-Giralt, Noah Amsel, Sruthi Yellamraju, James Ezick, Richard Lethin, Yuang Jiang, Aosong Feng, Leandros Tassiulas, Zhenguo Wu, Min Yeh Teh, Keren Bergman, "A Quantitative Theory of Bottleneck Structures for Data Networks," Submitted to Transactions on Networking, 2021. (Under review).

<a id="32">[32]</a> “G2-mininet - Reservoir Labs.” GitHub, https://github.com/reservoirlabs. Accessed 11 Apr. 2022.
