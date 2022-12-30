const NL = require("../models/newsletter");

exports.saveEmail = async (req, res) => {
    try {
      const { email } = req.body;
      res.json(await new NL({ email }).save());
    } catch (err) {
      console.log(err);
      res.status(400).send("Saving emailid failed");
    }
};
