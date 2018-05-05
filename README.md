# BoonTorrent
# A Real-Time Monitoring Tool for BitTorrent DHT Traffic

##### 2018 Penn Senior Design Project

##### Team: David Cao, Dylan Mann, Alex Moses, and Graham Mosley

##### Advisor: Boon Thau Loo

##### First Place in CIS Department

## Abstract

BitTorrent traffic is abundant, but difficult to analyze. To capture enough data for significant analysis, a large distributed solution is needed. Currently, research firms like Nielsen fail to properly account for illegal media consumption. Analyzing BitTorrent traffic would allow firms to study consumer behaviors that were previously invisible to traditional measures of media popularity.

Our solution is to deploy nodes that listen to the BitTorrent Mainline Distributed Hash Table (DHT).  Each node runs a forked version of the excellent repo [mldht by the8472](https://github.com/the8472/mldht).  Our fork can be found [here](https://github.com/dylanmann/mldht).  Once our node is discovered by peers in the DHT, it begins routing queries, resolving torrents, and collecting metadata about the queries it receives. We process this data through our pipeline and store the processed results in Amazon S3 for easy access.

The main product of BoonTorrent is machine readable time-series data for research. We also implemented two proof of concept applications built on that data.  The first is a heatmap visualization that is updated in real time with the last 2 minutes of traffic, and the second is a search engine for locating specific torrent files. In one month our search engine has indexed 1.2 million torrents representing 46 million files totaling nearly 4 petabytes in size.  Our pipeline and both applications run for roughly $10 a day, and we are logging and analyzing roughly 7 million data points daily.  Our work has shown that it is possible to cost effectively monitor BitTorrent traffic.

## Project Structure

| Location | Description |
|----------|-------------|
| [classification](/classification) | Some attempts at naive classification. |
| [indexer-lambda](/indexer-lambda) | AWS Lambda that indexes resolved torrents, triggered by s3 object creation events. |
| [torrent-summary-lambda](/torrent-summary-lambda) | AWS Lambda that retrieves a given torrent from S3 and decodes the metadata. |
| [prototypes](/prototypes) | Prototype implementations. |
| [spark-scala](/spark-scala) | Local spark processing code. |
| [userdata.sh](/userdata.sh) | Userdata script for EC2 instances. |
| [docs](/docs) | screenshots and reference material. |
| [app](/app) | Proof of concept web applications written with ejs. |

An example firehose log file can be found [here](docs/boonlog-firehose-1-2018-04-30-17-59-50-13ee9501-0921-45ef-a0af-23e9cc13f023).

## Screenshots

![World Map][map1]

![Asia Map][map2]

![Europe Map][map3]

![Statistics][stats]

![Search][search1]

![Search Results][search2]

![Individual Search Result][search3]

[map1]: /docs/map.PNG "World Map"
[map2]: /docs/map2.PNG "Asia Map"
[map3]: /docs/map3.PNG "Europe Map"
[stats]: /docs/stats.PNG "Country Statistics"
[search1]: /docs/search1.PNG "Search Page"
[search2]: /docs/search2.PNG "Search Results"
[search3]: /docs/search3.PNG "Individual Search Result"
