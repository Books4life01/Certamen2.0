let paused = false;
let liveQuestionReciever = "liveQuestionReciever";

//socket methods
socket.on("roomLiveQuestionUpdate", (data) =>{
    if(data.publicKey == roomKey || data.privateKey == roomKey){
        let actionType = data.actionType;
        console.log("action Type" + actionType);
        //iterate through keys and values in data and update the roomData 
        for( const [key,value] of Object.entries(data)){//this updates any values in roomData that appear in data
            if (key in roomData){
                roomData[key] = value;
            }
        }
        if (actionType == "startBroadcast"){
            $("#liveQuestionClientInfo").text("Press Space to Buzz in");
            $("#liveAnswerReciever").addClass("hidden");
        }
    
        else if (actionType == "nextChar"){
            $("#liveQuestionReciever").text(data.curLiveQuestion);
        }
        else if (actionType == "pause" ){
            console.log(data)
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
                $("#liveQuestionClientInfo").text("Submit Answer In: " + data.timer + " seconds");//update the timer for the client
                $("#liveQuestionHostInfo").text(data.player + " buzzed! They must Submit Answer In: " + data.timer + " seconds")//update the timer for the host

                //if we have run out of time and we are the player who buzzed in
                if(data.timer == 0 && !(player==undefined) && player['privateKey'] == data.playerInitiated['privateKey']){
                    submitAnswer();
                    $("#liveQuestionClientInfo").text("Time's Up! Answer Automatically Submitted");
                    setTimeout(() => {
                        $("#liveQuestionClientInfo").text("Time's Up! Answer Automatically Submitted");
                    }, 2000);
                    
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
            $("#liveQuestionHostInfo").text("Verify Answer");
            $("#liveQuestionClientInfo").text(`Answer by ${data.playerInitiated.name} awaiting Host Verification:`);

            //if we are the host end the timer by clearing the interval
            if(player == undefined)clearInterval(timer);

        }
        else if (actionType == "rejectAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            $("#playerScreen").removeClass("hidden");
            $("#liveQuestionClientInfo").text("Answer Rejected! Try Again");
            $("#liveQuestionHosttInfo").text("Answer Rejected! Question Continues");

            paused=false;

        }
        else if (actionType == "acceptAnswer"){
            //show the verifyAnswer div
            $("#verifyAnswer").addClass("hidden");
            $("#liveQuestionClientInfo").text("Answer Accepted!");
            $("#liveQuestionReciever").text(data.curLiveQuestion);
           

            
            paused=false;
        }
        data.playersAttempted.forEach(player => {
                if(player != ""){
                    console.log(player + "" + data.playerInitiated['privateKey'])
                    $("#" + player).css("color", "red");
                }
            });
        if(data.playerInitiated != ""){
            $("#" + data.playerInitiated['privateKey']).css("color", "yellow");
        }
        resetResults();
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

/**
 * Start an async timer on the host's computer which will send out the time remaining to the client
 * @param {*} seconds 
 * @param {*} player 
 */
function startAsyncTimer(seconds, playerInitiated={"name":"A Player"}){
    //emit StartTimer to the server
    socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "player":playerInitiated,"questionNum": curQuestion,"questionType": roomData.curQuestionType, "actionType":"startTimer","questionNum":curQuestion, "timeLeft": seconds})
    //timer is defined in roomHostBaseCods.js
    timer = setInterval(() =>{
        socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "player":playerInitiated,"questionNum": curQuestion,"questionType": roomData.curQuestionType, "actionType":"updateTimer","questionNum":curQuestion, "timeLeft": seconds})
        seconds--;
    }, seconds*100);
}
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
function submitAnswer(){
    if (!(player === undefined || roomData.playersAttempted.find((p) =>{p == player['privateKey']}))){//his only allows players who havent answered to submit an answer and prevents the host from submitting an answer
        socket.emit("liveQuestionUpdate", data = {"roomKey": roomKey, "player":player,"questionNum": curQuestion,"questionType": roomData.curQuestionType, "actionType":"attemptAnswer","questionNum":curQuestion, "attemptedAnswer":$("#answerInput").val()});
    }
}