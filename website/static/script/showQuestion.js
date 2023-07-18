let paused = false;
let liveQuestionReciever = "liveQuestionReciever";
console.log("from showQuestionjs" + curQuestion)
//socket methods
socket.on("roomLiveQuestionUpdate", (data) =>{
    let actionType = data.actionType;
    console.log("liveQuestionUpdate recieved: " + actionType);
    console.log(data);

    if (actionType == "startBroadcast"){

    }
    else if (actionType == "nextChar"){
    }
    else if (actionType == "pause" ){
    }
    else if (actionType == "rejectAnswer"){
    }
    else if (actionType == "acceptAnswer"){
        
    }
    $("#liveQuestionReciever").text(data.curLiveQuestion);

    paused = data.liveQuestionPaused;
})


function startAsyncTimer(seconds){
    $("#submitAnswer").removeClass("hidden");
    var timer = setInterval(() =>{
        if (seconds > 0 && paused){
            seconds--;
            $("#buzzInfo").text("Submit Answer In: " + seconds + " seconds");
        }
        else{
            submitAnswer();
            $("#buzzInfo").text("Time's Up! Answer Submitted");
            $("#submitAnswer").addClass("hidden");
            clearInterval(timer)
            paused=false;
            setTimeout(() => {
                $("#buzzInfo").text("Answer Submitted!");
            }, 2000);

        }
    }, seconds*100);
}