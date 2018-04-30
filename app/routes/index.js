var express = require('express');
var router = express.Router();

var AWS = require("aws-sdk");
AWS.config.update({region: 'us-east-1'});
var s3 = new AWS.S3();
var lambda = new AWS.Lambda();

var newEpoch = Number((Date.now() - ((1) * 3600000)) / 1000);
var miss = 0;
var booncoordinates = [];



var elasticsearch = require('elasticsearch');

var client = new elasticsearch.Client({
  host: process.env.PROD ? 'https://vpc-boontorrent-giarxt7zrugwle2okjyqc67b6m.us-east-1.es.amazonaws.com':'localhost:9200',
  log: 'trace'
});

/* GET home page. */
router.get('/', function (req, res, next) {
  total_torrents = 0
  client.count({
    index: 'torrents',
    type: '_doc',
  }, function (error, response) {
    if (error) {
      console.log(error)
    } else {
      total_torrents = response.count;
      console.log("COUNT: ", + total_torrents);
    }
  });
  s3.getObject({ Bucket: 'boontorrent-dump', Key: 'latest.txt' }, function (err, data) {
    if (err) {
      console.log(err);
      return;
    }
    booncoordinates = [];
    key = data.Body.toString();
    console.log(key);
    s3.getObject({ Bucket: 'boontorrent-kinesis', Key: key }, function (err, data) {
      if (err) throw err
      var lines = data.Body.toString().split(/\n/).map(function (str, i) {
        if (str.trim() === '') return;
        var record = JSON.parse(str);
        if (record.location !== undefined && record.location !== null && record.location.city != null) {
          if (record.location.latitude !== undefined && record.location.latitude !== null) {
            var booncoord = { lat: record.location.latitude, lon: record.location.longitude, country: record.location.country };
            booncoordinates[i] = booncoord;
          }
        }
      })
      console.log(booncoordinates.length);

      return res.render('index.ejs', { title: 'BoonTorrent', coordinates: booncoordinates, torrents: total_torrents });
    })
  })
});


router.get('/search', function (req, res) {
  client.search({
    index: 'torrents',
    q: 'name:' + req.query.q,
    size: 50
  }).then(function (resp) {
    var time = resp.took;
    if (resp.hits.total <= 0) {
      res.render('noresults', {
        time: time,
        querystring: req.query.q,
        title: req.query.q + " - BoonTorrent Search",
      });
    } else {
      var hits = resp.hits.hits;
      var max_score = resp.hits.max_score;

      return res.render('search', {
        time: time,
        max_score: max_score,
        querystring: req.query.q,
        title: req.query.q + " - BoonTorrent Search",
        hits: hits,
        numhits: resp.hits.total,
      });
    }
  }, function (err) {
    console.trace(err.message);
    res.send(err.message);
  });
});

router.get('/torrent/:infohash', function (req, res) {
  var params = {
    FunctionName: "torrent_info",
    InvocationType: "RequestResponse",
    Payload: JSON.stringify({ infohash: req.params.infohash }),
  };
  lambda.invoke(params, function (err, data) {
    if (err) {
      res.json(err);
    } else {
      console.log(JSON.parse(data.Payload));
      res.render('torrent-lambda.ejs', { data: JSON.parse(data.Payload) });
    }
  });
  // client.get({
  //   index: 'torrents',
  //   type: '_doc',
  //   id: req.params.infohash
  // }, function (error, response) {
  //   if (error) {
  //     res.send(error);
  //   } else {
  //     var data = response._source;
  //     return res.render('torrent', { title: data.name, torrent_data: data });
  //     res.send(response);
  //   }
  // });
});

/* GET reMap JSON. */
router.get('/reMap', function (req, res, next) {
  total_torrents = 0
  client.count({
    index: 'torrents',
    type: '_doc',
  }, function (error, response) {
    if (error) {
      console.log(error)
    } else {
      total_torrents = response.count;
      console.log("COUNT: ", + total_torrents);
    }
  });
  s3.getObject({ Bucket: 'boontorrent-dump', Key: 'latest.txt' }, function (err, data) {
    if (err) {
      console.log(err);
      return;
    }
    booncoordinates = [];
    key = data.Body.toString();
    console.log(key);
    s3.getObject({ Bucket: 'boontorrent-kinesis', Key: key }, function (err, data) {
      if (err) throw err
      var lines = data.Body.toString().split(/\n/).map(function (str, i) {
        if (str.trim() === '') return;
        var record = JSON.parse(str);
        if (record.location !== undefined && record.location !== null) {
          if (record.location.latitude !== undefined && record.location.latitude !== null) {
            var booncoord = { lat: record.location.latitude, lon: record.location.longitude, country: record.location.country };
            booncoordinates[i] = booncoord;
          }
        }
      })
      console.log(booncoordinates.length);

      return res.send({ coordinates: booncoordinates, torrents: total_torrents });
    })
  })
});

module.exports = router;
