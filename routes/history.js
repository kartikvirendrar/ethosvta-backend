const express = require("express");
const router = express.Router();
const { saveHistory, getHistoryById, getHistoryforUser, updateComments, addSubtitleText } = require("../controllers/history");

router.post("/savehistory", saveHistory);
router.post("/gethistorybyid", getHistoryById);
router.post("/gethistoryforuser", getHistoryforUser);
router.post("/updatecommentsbyid", updateComments);
router.post("/addsubtext", addSubtitleText);
module.exports = router;