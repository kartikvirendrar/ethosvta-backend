const cloudinary=require("cloudinary").v2;

cloudinary.config({
    cloud_name:process.env.CLOUDINARY_CLOUD_NAME,
    api_key:process.env.CLOUDINARY_API_KEY,
    api_secret:process.env.CLOUDINARY_API_SECRET,
});

exports.uploadAudio = async (req,res) => {
    try {
    let result= await cloudinary.uploader.upload(req.body.audio, { resource_type: "auto", folder: "ethosAudioFiles/", public_id:`${Date.now()}`, format:req.body.format, timeout:100000})
    res.json({
        public_id:result.public_id,
        url:result.secure_url
    });
} catch (err) {
    console.log(err);
    res.status(400).send("Saving video on cloudinary failed");
  }
}