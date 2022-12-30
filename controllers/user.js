const User = require("../models/user");

exports.checkUserByEmail = async (req, res) => {
  const { email }=req.body;
  const user= await User.findOne({email}).exec();
  res.json(user);  
};