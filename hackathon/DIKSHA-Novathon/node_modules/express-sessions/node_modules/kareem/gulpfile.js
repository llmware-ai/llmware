var gulp = require('gulp');
var mocha = require('gulp-mocha');
var config = require('./package.json');
var jscs = require('gulp-jscs');

gulp.task('mocha', function() {
  return gulp.src('./test/*').
    pipe(mocha({ reporter: 'dot' }));
});

gulp.task('jscs', function() {
  return gulp.src('./index.js').
    pipe(jscs(config.jscsConfig));
});

gulp.task('watch', function() {
  gulp.watch('./index.js', ['jscs', 'mocha']);
});
