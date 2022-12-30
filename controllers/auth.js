const User = require("../models/user");

exports.createOrUpdateUser = async (req, res) => {
  const {email} = req.user;
  const {name} = req.body;

  const user = await User.findOneAndUpdate(
    { email },
    { new: true }
  );
  if (user) {
    console.log("USER UPDATED", user);
    res.json(user);
  } else {
    const newUser = await new User({
      email,
      name,
    }).save();
    console.log("USER CREATED", newUser);
    res.json(newUser);
  }
};