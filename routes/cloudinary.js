const express = require("express");
const { uploadAudio } = require("../controllers/cloudinary");
const router = express.Router();

router.post("/uploadAudio", uploadAudio);

module.exports = router;