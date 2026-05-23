module.exports.isLoggedIn = (req,res,next)=>{
    if(!req.isAuthenticated()){
        req.session.redirectUrl = req.originalUrl;
        req.flash("success", "You must be looged in to add new Listing");
        res.redirect("/login");
      }
      next();
};