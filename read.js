var filepath = ""

//class Dex
var EOT = 0x04
var ENQ = 0x05
var DLE = 0x10

var stateINIT = 0;
var stateWAITING_FOR_SLAVE_HANDSHAKE=1;
var stateWAITING_FOR_MASTER_HANDSHAKE=2;

var state = stateINIT;

function receiveChar(char, oup) {
    if(state == stateINIT) {
        if(char == ENQ) {
            console.log("Received ENQ in init")
            // Master
            state = stateWAITING_FOR_SLAVE_HANDSHAKE
            oup.write(new Buffer([ENQ]))
            // Slave
        }
    } else if(state == stateWAITING_FOR_SLAVE_HANDSHAKE) {
        console.log("Got char in slave handshake mode")
    } else if(state == stateWAITING_FOR_MASTER_HANDSHAKE) {
        console.log("Got char in master handshake mode")
        if(char == ENQ) {
            console.log("Got ENQ in master handshake");
            oup.write(new Buffer([DLE]))
            oup.write(new Buffer([0x30]))
            console.log("here")
        }
    }
}


if(process.argv[2] == "master") {
    filepath = "/dev/ptyp3"
} else if(process.argv[2] == "slave") {
    filepath = "/dev/ttyp3"
} else {
    return console.log("one of slave or master")
}

function open() {
    console.log("opening " + filepath)
    var fs = require('fs');
    var inp = fs.createReadStream(filepath);
    var oup = fs.createWriteStream(filepath);
    //inp.setEncoding('hex');

    inp.on('data', function (data) {
        console.log("got data, length=" + data.length + " " + data.toString('hex'));
        
        for(var i=0; i < data.length; i++) {
            receiveChar(data[i], oup)
        }
        //var buffer = new Buffer(result, 'binary');
        
    });

    inp.on('end', function() {
        console.log('stream is closed')
        open()
    })
    
    inp.on('error', function(err) { console.log("err: " + err)})
}

open()