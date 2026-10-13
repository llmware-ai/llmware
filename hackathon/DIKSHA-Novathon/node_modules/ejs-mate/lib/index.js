'use strict';

const ejs = require('ejs');
const fs = require('fs');
const path = require('path');
const Block = require('./block');

/**
 * Memory cache for resolved object names.
 */

var cache = {};

/**
 * Lookup partial path from base path of current template:
 *
 *   - partial `_<name>`
 *   - any `<name>/index`
 *   - non-layout `../<name>/index`
 *   - any `<root>/<name>`
 *   - partial `<root>/_<name>`
 *
 * Options:
 *
 *   - `cache` store the resolved path for the view, to avoid disk I/O
 *
 * @param {String} root, full base path of calling template
 * @param {String} partial, name of the partial to lookup (can be a relative path)
 * @param {Object} options, for `options.cache` behavior
 * @return {String}
 * @api private
 */

function lookup(root, partial, options) {
  const engine = options.settings['view engine'] || 'ejs';
  const desiredExt = '.' + engine;
  const ext = path.extname(partial) || desiredExt;
  const key = [root, partial, ext].join('-');
  const partialPath = partial;

  if (options.cache && cache[key]) {
    return cache[key];
  }

  // Make sure we use dirname in case of relative partials
  // ex: for partial('../user') look for /path/to/root/../user.ejs
  var dir = path.dirname(partial);
  var base = path.basename(partial, ext);

  // _ prefix takes precedence over the direct path
  // ex: for partial('user') look for /root/_user.ejs
  partial = path.resolve(root, dir, '_' + base + ext);
  if (fs.existsSync(partial)) {
    return options.cache ? cache[key] = partial : partial;
  }

  // Try the direct path
  // ex: for partial('user') look for /root/user.ejs
  partial = path.resolve(root, dir, base + ext);
  if (fs.existsSync(partial)) {
    return options.cache ? cache[key] = partial : partial;
  }

  // Try index
  // ex: for partial('user') look for /root/user/index.ejs
  partial = path.resolve(root, dir, base, 'index'+ext);
  if (fs.existsSync(partial)) {
    return options.cache ? cache[key] = partial : partial;
  }

  // Try relative to the app views
  if (!options._isRelativeToViews) {
    var views = options.settings.views;
    options._isRelativeToViews = true;

    if (!Array.isArray(views)) {
      views = [views];
    }

    for (var i = 0; i < views.length; i++) {
      partial = lookup(views[i], partialPath, options);

      if (partial) {
        // reset state for when the partial has a partial lookup of its own
        options._isRelativeToViews = false;

        return partial;
      }
    }
  }

  // FIXME:
  // * there are other path types that Express 2.0 used to support but
  //   the structure of the lookup involved View class methods that we
  //   don't have access to any more
  // * we have no tests for finding partials that aren't relative to
  //   the calling view

  return null;
}


/**
 * Render `view` partial with the given `options`. Optionally a
 * callback `fn(err, str)` may be passed instead of writing to
 * the socket.
 *
 * Options:
 *
 *   - `object` Single object with name derived from the view (unless `as` is present)
 *
 *   - `as` Variable name for each `collection` value, defaults to the view name.
 *     * as: 'something' will add the `something` local variable
 *     * as: this will use the collection value as the template context
 *     * as: global will merge the collection value's properties with `locals`
 *
 *   - `collection` Array of objects, the name is derived from the view name itself.
 *     For example _video.html_ will have a object _video_ available to it.
 *
 * @param  {String} view
 * @param  {Object|Array} options, collection or object
 * @return {String}
 * @api private
 */
function partial(view){
  // find view, relative to this filename
  // (FIXME: filename is set by ejs engine, other engines may need more help)
  var root = path.dirname(this.filename);
  var file = lookup(root, view, this);
  var key = file + ':string';
  if (!file) {
    throw new Error(`Could not find partial '${view}'`);
  }

  // read view
  var source = this.cache
    ? cache[key] || (cache[key] = fs.readFileSync(file, 'utf8'))
    : fs.readFileSync(file, 'utf8');

  return ejs.render(source, this);
}

/**
 * Apply the given `view` as the layout for the current template,
 * using the current options/locals. The current template will be
 * supplied to the given `view` as `body`, along with any `blocks`
 * added by child templates.
 *
 * `options` are bound  to `this` in renderFile, you just call
 * `layout('myview')`
 *
 * @param {String} view
 * @api private
 */
function layout(view){
  this._layoutFile = view;
}

/**
 * Return the block with the given name, create it if necessary.
 * Optionally append the given html to the block.
 *
 * The returned Block can append, prepend or replace the block,
 * as well as render it when included in a parent template.
 *
 * @param {String} name
 * @param {String} html
 * @return {Block}
 * @api private
 */
function block(name, html) {
  // bound to the blocks object in renderFile
  var blk = this[name];
  if (!blk) {
  // always create, so if we request a
  // non-existent block we'll get a new one
    blk = this[name] = new Block();
  }

  if (html) {
    blk.append(html);
  }

  return blk;
}

/**
 * Express 3.x Layout & Partial support for EJS.
 *
 * The `partial` feature from Express 2.x is back as a template engine,
 * along with support for `layout` and `block/script/stylesheet`.
 *
 *
 * Example index.ejs:
 *
 *   <% layout('boilerplate') %>
 *   <h1>I am the <%=what%> template</h1>
 *   <% script('foo.js') %>
 *
 *
 * Example boilerplate.ejs:
 *
 *   <html>
 *     <head>
 *       <title>It's <%=who%></title>
 *       <%-scripts%>
 *     </head>
 *     <body><%-body%></body>
 *   </html>
 *
 *
 * Sample app:
 *
 *    var express = require('express')
 *      , app = express();
 *
 *    // use ejs-locals for all ejs templates:
 *    app.engine('ejs', require('ejs-locals'));
 *
 *    // render 'index' into 'boilerplate':
 *    app.get('/',function(req,res,next){
 *      res.render('index', { what: 'best', who: 'me' });
 *    });
 *
 *    app.listen(3000);
 *
 * Example output for GET /:
 *
 *   <html>
 *     <head>
 *       <title>It's me</title>
 *       <script src="foo.js"></script>
 *     </head>
 *     <body><h1>I am the best template</h1></body>
 *   </html>
 *
 */

function compile(file, options, cb) {

  // Express used to set options.locals for us, but now we do it ourselves
  // (EJS does some __proto__ magic to expose these funcs/values in the template)
  if (!options.locals) {
    options.locals = {};
  }

  if (!options.locals.blocks) {
    // one set of blocks no matter how often we recurse
    var blocks = {};
    options.blocks = blocks;
    options.block = block.bind(blocks);
  }

  // override locals for layout/partial bound to current options
  options.locals.layout  = layout.bind(options);
  options.locals.partial = partial.bind(options);

  try {
    var fn = ejs.compile(file, options);
  } catch(ex) {
    cb(ex);
    return;
  }

  cb(null, fn.toString());
}

// var renderFile = function (file, locals, options) {
//   return new Promise((resolve, reject) => {
//     ejs.renderFile(file, locals, options, (err, html) => {
//       if (err) {
//         return reject(err);
//       }
//       resolve(html);
//     });
//   });
// };

function renderFile(file, options, fn){
  // Express used to set options.locals for us, but now we do it ourselves
  // (EJS does some __proto__ magic to expose these funcs/values in the template)
  if (!options.locals) {
    options.locals = {};
  }

  if (!options.locals.blocks) {
    // one set of blocks no matter how often we recurse
    var blocks = {};
    options.locals.blocks = blocks;
    options.block = block.bind(blocks);
  }

  // override locals for layout/partial bound to current options
  options.layout  = layout.bind(options);
  options.partial = partial.bind(options);
  options.filename = file;

  ejs.renderFile(file, options, function(err, html) {
    if (err) {
      return fn(err,html);
    }

    var layout = options.locals._layoutFile;

    // for backward-compatibility, allow options to
    // set a default layout file for the view or the app
    // (NB:- not called `layout` any more so it doesn't
    // conflict with the layout() function)
    if (layout === undefined) {
      layout = options._layoutFile;
    }

    if (layout) {

      // use default extension
      var engine = options.settings['view engine'] || 'ejs',
        desiredExt = '.'+engine;

      // apply default layout if only "true" was set
      if (layout === true) {
        layout = path.sep + 'layout' + desiredExt;
      }
      if (path.extname(layout) !== desiredExt) {
        layout += desiredExt;
      }

      // clear to make sure we don't recurse forever (layouts can be nested)
      delete options.locals._layoutFile;
      delete options._layoutFile;
      // make sure caching works inside ejs.renderFile/render
      options.filename;

      if (layout.length > 0) {
        var views = options.settings.views;
        var l = layout;

        if (!Array.isArray(views)) {
          views = [views];
        }

        for (var i = 0; i < views.length; i++) {
          layout = path.join(views[i], l);

          // use the first found layout
          if (fs.existsSync(layout)) {
            break;
          }
        }
      }

      // now recurse and use the current result as `body` in the layout:
      options.body = html;
      renderFile(layout, options, fn);
    } else {
      // no layout, just do the default:
      fn(null, html);
    }
  });

}

renderFile.compile = compile;
renderFile.partial = partial;
renderFile.block = block;
renderFile.layout = layout;

module.exports = renderFile;
