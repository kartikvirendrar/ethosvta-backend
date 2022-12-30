const express = require("express");
const router = express.Router();

const { saveEmail } = require("../controllers/newsletter");

router.post("/saveemail", saveEmail);
module.exports = router;