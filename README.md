# BoonTorrent, A Real-Time Monitoring Tool for BitTorrent DHT Traffic
##### 2018 Penn Senior Design Project
##### Team: David Cao, Dylan Mann, Alex Moses, and Graham Mosley
##### Advisor: Boon Thau Loo
##### CIS Department

## Abstract
BitTorrent traffic is abundant, but difficult to analyze. To capture enough data for significant analysis, a large distributed solution is needed. Currently, research firms like Nielsen fail to properly account for illegal media consumption. Analyzing BitTorrent traffic would allow firms to study consumer behaviors that were previously invisible to traditional measures of media popularity.

Our solution is to deploy nodes that listen to the BitTorrent Mainline Distributed Hash Table (DHT).  Once our node is discovered by peers in the DHT, it begins routing queries, resolving torrents, and collecting metadata about the queries it receives. We process this data through our pipeline and store the processed results in Amazon S3 for easy access.

The main product of BoonTorrent is machine readable time-series data for research. We also implemented two proof of concept applications built on that data.  The first is a heatmap visualization that is updated in real time with the last 2 minutes of traffic, and the second is a search engine for locating specific torrent files. In one month our search engine has indexed 1.2 million torrents representing 46 million files totaling nearly 4 petabytes in size.  Our pipeline and both applications run for roughly $10 a day, and we are logging and analyzing roughly 7 million data points daily.  Our work has shown that it is possible to cost effectively monitor BitTorrent traffic.

## Project Structure
An example log file can be found [here](screenshots/boonlog-firehose-1-2018-04-30-17-59-50-13ee9501-0921-45ef-a0af-23e9cc13f023)

## Screenshots

![World Map][map1]

![Asia Map][map2]

![Europe Map][map3]

![Statistics][stats]

![Search][search1]

![Search Results][search2]

![Individual Search Result][search3]

[map1]: /screenshots/map.PNG "World Map"
[map2]: /screenshots/map2.PNG "Asia Map"
[map3]: /screenshots/map3.PNG "Europe Map"
[stats]: /screenshots/stats.PNG "Country Statistics"
[search1]: /screenshots/search1.PNG "Search Page"
[search2]: /screenshots/search2.PNG "Search Results"
[search3]: /screenshots/search3.PNG "Individual Search Result"
