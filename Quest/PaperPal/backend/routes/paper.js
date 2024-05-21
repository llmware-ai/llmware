const express = require("express");
const router = express.Router();

const {
  Model,
  testing,
  qna
} = require("../controllers/paper");

router.post("/model", Model);
router.get("/test", testing);
router.post("/qna", qna)

module.exports = router;
