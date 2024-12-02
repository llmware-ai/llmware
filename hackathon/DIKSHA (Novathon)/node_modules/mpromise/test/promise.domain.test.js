var Promise = require('../')
  , Domain = require('domain').Domain
  , assert = require('assert');


describe("domains", function () {
  it("exceptions should not breakout of domain boundaries", function (done) {
    if (process.version.indexOf('v0.10') != 0) return done();
    var d = new Domain;
    d.on('error', function (err) {
      assert.equal(err.message, 'gaga');
      done()
    });

    var p = new Promise();
    d.run(function () {
      p.then(
        function () {}
      ).then(
        function () { throw new Error('gaga'); }
      ).end();
    });

    process.nextTick(function () {
      p.fulfill();
    });
  });
});
