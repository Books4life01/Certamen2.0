let paused = false;
let liveQuestionReciever = "liveQuestionReciever";
//socket methods
socket.on("roomLiveQuestionUpdate", (data) =>{
    if(data.publicKey == roomKey || data.privateKey == roomKey){
        let actionType = data.actionType;
        console.log("action Type" + actionType);
        //update the room Data provided
        roomData.curLiveQuestionAnswer = data.curLiveQuestionAnswer;
        roomData.curLiveQuestion = data.curLiveQuestion;
        roomData.curQuestionType = data.curQuestionType;
        roomData.liveQuestionPaused = data.liveQuestionPaused 

        if (actionType == "startBroadcast"){
            $("#liveQuestionClientInfo").text("Press Space to Buzz in");
        }
    
        else if (actionType == "nextChar"){
            $("#liveQuestionReciever").text(data.curLiveQuestion);
        }
        else if (actionType == "pause" ){
            console.log(data)
            paused = true;
            startAsyncTimer(10, playerName=data.playerInitiated['name']);
            $("#" + data.playerInitiated['privateKey']).css("color", "yellow");
        }
        else if(actionType== "attemptAnswer"){
            console.log("attemptAnswer" + data.curLiveQuestionAnswer)
            //show the verifyAnswer div
            $("#verifyAnswer").removeClass("hidden");
            $("#liveAnswerReciever").text(data.curLiveQuestionAnswer);
        }
        else if (actionType == "rejectAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            $("#liveQuestionClientInfo").text("Answer Rejected! Try Again");
            paused=false;

        }
        else if (actionType == "acceptAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            $("#liveQuestionClientInfo").text("Answer Accepted!");
            $("#liveQuestionReciever").text(data.curLiveQuestion);
            paused=false;
        }
        if(data.forEach != ""){
            data.playersAttempted.forEach(player => {
                if(player != data.playerInitiated['privateKey'] && player != ""){
                    $("#" + player).css("color", "red");
                }
                
            });
        }
    }
    
});
socket.on("roomParticipantUpdate", (data)=>{
    if(data.publicKey==roomKey||data.privateKey==roomKey){
        let players = JSON.parse(data['participants']);
        console.log(players);
        $('.teamHolder>i').each((index, value)=>{
           value.remove();
        });
        ['A','B','C','D'].forEach((letter) =>{
            players.forEach((player)=>{
                console.log(roomData["team" + letter] + " " + player['teamKey']);
                if(roomData["team" + letter] == player['teamKey']){
                    console.log('#' + letter + 'Label');
                    if(letter == 'B' || letter == 'C')$('<i class="fa-solid fa-user"></i>').attr("title", player["name"]).attr("id", player['playerKey']).insertBefore('#' + letter + 'Label');
                    else $('<i class="fa-solid fa-user"></i>').attr("title", player["name"]).attr("id", player['playerKey']).insertAfter('#' + letter + 'Label');
                }
            })
        });
      
    }
    
})

async function sendQuestion(text, type){
    console.log(text);
    //send the question to the server indicating the start of the broadcast
    socket.emit("liveQuestionUpdate", data = {
        "roomKey": roomKey,
        "questionNum": curQuestion,
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
            "questionNum": curQuestion,
            "questionType": type,
            "actionType": "nextChar",
            "nextChar": text[0]
        });
        text = text.substring(1);
        await sleep(100);
    }
    results[curQuestion-1][["tossup", "bonus1", "bonus2"][type]+"Question"] = text;
    resetResults();
}


function startAsyncTimer(seconds, playerName="A player"){
    $("#submitAnswer").removeClass("hidden");
    var timer = setInterval(() =>{
        if (seconds > 0 && paused && roomData.curLiveQuestionAnswer == ""){
            seconds--;
            $("#liveQuestionClientInfo").text("Submit Answer In: " + seconds + " seconds");
            $("#liveQuestionHostInfo").text(playerName + " buzzed! They must Submit Answer In: " + seconds + " seconds");
        }
        else if(roomData.curLiveQuestionAnswer != ""){
            $("#liveQuestionClientInfo").text("Awaiting Host Verification");
            $("#liveQuestionHosttInfo").text("Verify Answer");

            clearInterval(timer)
        }
        else{
            //if this is the client, submit the answer
            if(!(typeof player === undefined))submitAnswer();
            $("#liveQuestionClientInfo").text("Time's Up! Answer Automatically Submitted");
            $("#liveQuestionHosttInfo").text("Verify Answer");
            $("#submitAnswer").addClass("hidden");
            clearInterval(timer)
            setTimeout(() => {
                $("#liveQuestionClientInfo").text("Awaiting Host Verification");
            }, 2000);

        }
    }, seconds*100);
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
function submitAnswer(){
    if (!(typeof player === undefined))socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "player":player,"questionNum": curQuestion,"questionType": roomData.curQuestionType, "actionType":"attemptAnswer","questionNum":curQuestion,  "attemptedAnswer":$("#answerInput").val()})
}