const mongoose = require('mongoose');
const { ObjectId } = mongoose.Schema;

const historySchema = new mongoose.Schema({
    userId:{
        type:ObjectId, ref: "User"
    }, 
    audioUrl:{
        type:String, required:true
    },
    audioFormat:{
        type:String, required:true
    },
    audioName:{
        type:String, required:true
    },
    videoName:{
        type:String, required:true
    },
    comments:{
        type:String, required:true
    },
    subtitle:{
        type:String
    },
    text:{
        type:String
    }
}, { timestamps: true })

module.exports = mongoose.model("History", historySchema);