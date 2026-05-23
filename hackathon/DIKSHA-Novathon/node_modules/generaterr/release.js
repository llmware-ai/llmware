var shell = require('shelljs');

if (exec('git status --porcelain').output) {
  console.error('Git working directory not clean.');
  process.exit(2);
}

var versionIncrement = process.argv[process.argv.length -1];

if (versionIncrement != 'major' && versionIncrement != 'minor' && versionIncrement != 'patch') {
  console.error('Usage: node release.js major|minor|patch');
  process.exit(1);
}

exec('npm version ' + versionIncrement);

exec('npm test');
exec('git push');
exec('git push --tags');
exec('npm publish');

function exec(cmd) {
  var ret = shell.exec(cmd, { silent : true });

  if (ret.code !== 0) {
    console.error(ret.output);
    process.exit(1);
  }

  return ret;
}
