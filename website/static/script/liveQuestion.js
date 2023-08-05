let paused = false;
let liveQuestionReciever = "liveQuestionReciever";
let liveRoomPlayers = [];

//socket methods
socket.on("roomLiveQuestionUpdate", (data) =>{
    if(data.publicKey == roomKey || data.privateKey == roomKey){
        let actionType = data.actionType;

        //iterate through keys and values in data and update the roomData 
        for(const [key,value] of Object.entries(data)){//this updates any values in roomData that appear in data
            if (key in roomData){
                roomData[key] = value;
            }
        }

        if (actionType == "startBroadcast"){
            //Hide the answer reciever and show the question reciever
            $("#liveAnswerReciever").addClass("hidden");
        }
        else if (actionType == "nextChar"){
            //update the liveQuestionReciever: this happends in liveQuestionUpdate method()
            
        }
        else if (actionType == "pause" ){
            //pause emitting character updates
            paused = true;
            //if we are the host start the timer
            if(player == undefined){
                startAsyncTimer(10, playerInitiated=data.playerInitiated);
            }
        }
        else if(actionType == "updateTimer" || actionType == "startTimer" || actionType == "endTimer"){
            if(actionType == "endTimer"){}
            else{
                if(actionType == "startTimer" && !(player==undefined) && data.playerInitiated['privateKey']==player['privateKey']) $("#submitAnswer").removeClass("hidden");//If the timer is just starting show the submit answer button
                //and update the timer info
               
                //if we have run out of time and we are the player who buzzed in
                if(roomData.timer <= 0 && !(player==undefined) && player['privateKey'] == data.playerInitiated['privateKey']){
                    submitAnswer();   
                }
                
            }
        }
        else if(actionType== "attemptAnswer"){
            console.log("attemptAnswer" + data.curLiveQuestionAnswer)
            //show the verifyAnswer div
            $("#verifyAnswer").removeClass("hidden");
            $("#playerScreen").addClass("hidden");
            $("#submitAnswer").addClass("hidden");
            $("#liveAnswerReciever").removeClass("hidden").text(data.curLiveQuestionAnswer);

            //update the client and host Info
            
            //if we are the host end the timer by clearing the interval
            if(player == undefined)clearInterval(intervalTimer);

        }
        else if (actionType == "rejectAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            $("#playerScreen").removeClass("hidden");
            paused=false;
        }
        else if (actionType == "acceptAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            paused=false;
        }
        console.log({"action:":actionType, "client":roomData.clientInfo, "host":roomData.hostInfo, "player":data.playerInitiated, "timer":roomData.timer, "playersAttempted":roomData.playersAttempted});
        onRoomDataUpdate();
        resetResults();
        liveQuestionUpdate();
    }
    
});
socket.on("roomParticipantUpdate", (data)=>{
    if(data.publicKey==roomKey||data.privateKey==roomKey){
        if(data['participants'] == [] || data['participants'].length ==0)liveRoomPlayers = [];
        else{
            try{
                liveRoomPlayers = JSON.parse(data['participants']);
            }
            catch{
                console.log("ERROR PARSING PARTICIPANTS");
                console.log(data['participants']);
            }
        }
        $('.teamHolder>i').each((index, value)=>{
           value.remove();
        });
        ['A','B','C','D'].forEach((letter) =>{
            liveRoomPlayers.forEach((player)=>{
                if(roomData["team" + letter] == player['teamKey']){
                    if(letter == 'B' || letter == 'C')$('<i class="fa-solid fa-user"></i>').attr("title", player["name"]).attr("id", player['playerKey']).insertBefore('#' + letter + 'Label');
                    else $('<i class="fa-solid fa-user"></i>').attr("title", player["name"]).attr("id", player['playerKey']).insertAfter('#' + letter + 'Label');
                }
            })
        });
        liveQuestionUpdate();
    }
    
})

async function sendQuestion(text, type){
    //send the question to the server indicating the start of the broadcast
    socket.emit("liveQuestionUpdate", data = {
        "roomKey": roomKey,
        "questionNum": roomData.curQuestionNumber,
        "questionType": type,
        "fullQuestion": text, 
        "actionType": "startBroadcast",
    });
    while(text.length > 0){
        while(paused){
            await sleep(100);            
        }
        socket.emit("liveQuestionUpdate", data = {
            "roomKey": roomKey,
            "questionNum": roomData.curQuestionNumber,
            "questionType": type,
            "actionType": "nextChar",
            "nextChar": text[0]
        });
        text = text.substring(1);
        await sleep(100);
    }
    resetResults();
}

/**
 * Start an async timer on the host's computer which will send out the time remaining to the client
 * @param {*} seconds 
 * @param {*} player 
 */
function startAsyncTimer(seconds, playerInitiated={"name":"A Player"}){
    //emit StartTimer to the server
    socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "playerInitiated":playerInitiated,"questionNum": roomData.curQuestionNumber,"questionType": roomData.curQuestionType, "actionType":"startTimer","questionNum":roomData.curQuestionNumber, "timeLeft": seconds})
    //timer is defined in roomHostBaseCods.js
    console.log("starting timer");
    intervalTimer = setInterval(() =>{
        socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "playerInitiated":playerInitiated,"questionNum": roomData.curQuestionNumber,"questionType": roomData.curQuestionType, "actionType":"updateTimer","questionNum":roomData.curQuestionNumber, "timeLeft": seconds})
        seconds--;
        if(seconds < 0)clearInterval(intervalTimer, ()=>{console.log("cleared interval")});
    }, seconds*100);
    console.log(intervalTimer);
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
function submitAnswer(){
    if (!(player === undefined || roomData.playersAttempted.find((p) =>{p == player['privateKey']}))){//his only allows players who havent answered to submit an answer and prevents the host from submitting an answer
        socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "playerInitiated":player,"questionNum": roomData.curQuestionNumber,"questionType": roomData.curQuestionType, "actionType":"attemptAnswer","questionNum":roomData.curQuestionNumber, "attemptedAnswer":$("#answerInput").val()});
    }
}
//updates all html elements that display data about the liveQuestion
function liveQuestionUpdate(){
    $("#liveQuestionReciever").text(roomData.curLiveQuestion);
    $("#liveAnswerReciever").text(roomData.curLiveQuestionAnswer);
    $("#liveQuestionHostInfo").text(roomData.hostInfo);
    $("#liveQuestionClientInfo").text(roomData.clientInfo);

     //reset player icons 
     let filtered = roomData.playersAttempted.filter((element) =>{return element!=""});
     filtered.forEach((player, index) => {
        console.log(player)
        if(player != ""){
            //console.log(player + "" + data.playerInitiated['privateKey'])
            $("#" + player).css("color", "red");
        }
        //turn the last player who buzzed in yellow
        if(index == filtered.length - 1 && (roomData.curLiveQuestionAnswer != "" || roomData.timer != 0) )$("#" + player).css("color", "yellow");
    });
    

    //turn the player who got the question right green
    if (roomData.correctPlayer != null && roomData.correctPlayer != "")$("#" + roomData.correctPlayer).css("color", "green"); 

}