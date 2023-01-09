const history = require("../models/history");

exports.saveHistory = async (req, res) => {
    try {
      const { userId, audioUrl, audioFormat, audioName, videoName, comments } = req.body;
      res.json(await new history({ userId, audioUrl, audioFormat, audioName, videoName, comments }).save());
    } catch (err) {
      console.log(err);
      res.status(400).send("Saving audio history failed");
    }
};

exports.updateComments = async (req, res) => {
  try {
    const { commId, comments } = req.body;
    res.json(await history.findByIdAndUpdate(commId, {comments: comments}).exec());
  } catch (err) {
    console.log(err);
    res.status(400).send("Updating comments failde");
  }
};

exports.addSubtitleText = async (req, res) => {
  console.log("sss");
  try {
    const { commId, subtitle, text} = req.body;
    res.json(await history.findByIdAndUpdate(commId, {subtitle: subtitle, text: text}).exec());
  } catch (err) {
    console.log(err);
    res.status(400).send("Adding subtitles and text failed");
  }
};

exports.getHistoryById = async (req, res) => {
  const { histId }=req.body;
  const hist= await history.findById(histId).exec();
  res.json(hist);  
};

exports.getHistoryforUser = async (req, res) => {
  const { uId }=req.body;
  if (uId === process.env.ADMIN_ID) {
    const hist= await history.find().exec();
    res.json(hist);  
  }else{
    const hist= await history.find({userId:uId}).exec();
    res.json(hist);
  }
};

