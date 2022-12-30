const express = require("express");
const router = express.Router();

const { checkUserByEmail } = require("../controllers/user");

router.post("/check-user-email", checkUserByEmail);
module.exports = router;