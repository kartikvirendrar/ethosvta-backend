const mongoose = require('mongoose');

const nLSchema = new mongoose.Schema({
    email:{
        type:String, required:true
    }
})

module.exports = mongoose.model("NL", nLSchema);