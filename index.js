
//var com_path = "/dev/ptyp3"
var com_path="/dev/ptyp3"

var SerialPort = require("serialport").SerialPort;

//if (process.env.NODE_ENV == 'development') {
//    console.log("using virtual serial port")
// var SerialPort = require('virtual-serialport');
//}


var sp = new SerialPort(com_path, {
  //parser: serialport.parsers.raw,
  //baudRate: 9600,
  //bufferSize: 1
});
sp.on('data', function(data) {
      console.log('got data')
    //console.log('data received: ' + data);
  });  
sp.on('error', function(err) {
      console.log(err)
  })
sp.on("open", function () {
  console.log('open');
});

/*sp.open(function(error) {
if ( error ) {
    return console.log('failed to open: '+error);
  }
  console.log('file is opened')
  sp.on('data', function(data) {
      console.log('got data')
    //console.log('data received: ' + data);
  });
  console.log("registered data handler")
})*/

/*()
process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', process.exit.bind(process, 0));
*/