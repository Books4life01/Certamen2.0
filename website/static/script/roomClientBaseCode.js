//Global variables
let curQuestion = 1;
let results = [];
let roomData = {};
const socket = io.connect('http://172.16.68.165:8080');
//Document Ready
$(document).ready(() => {
    //call template specific document ready function
    documentReady();

    //requestion room Refresh
    socket.emit('roomClientConnect', data = {"roomKey": roomKey, "playerKey": player.privateKey});
    socket.emit("roomDataRefreshRequest", data = {"roomKey": roomKey});
});

//Socket Handlers
socket.on('roomDataUpdate', data=>{
    if(data.privateKey == roomKey || data.publicKey == roomKey){
        console.log("Room Data Recieved from the Server")
        console.log(data);
        curQuestion = data.currentQuestion;
        roomData = data;
        $(".questionNum").text("Question #" + curQuestion);
        resetRoomData();
    }
});

function resetRoomData(){
    //reset question num and type
    $("#questionTitle").text("Question #" + roomData.currentQuestion + ": " + ["Tossup","Bonus 1","Bonus 2"][roomData.curQuestionType]);
    
}