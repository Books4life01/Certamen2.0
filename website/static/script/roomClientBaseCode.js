//Global variables
let curQuestion = 1;
let results = [];
let roomData = {};
const socket = io.connect('http://192.168.4.127:8080');
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
socket.on('roomResultsUpdate', data =>{
    results = data['resultList'];
    resetRoomData();
})

function resetRoomData(){
    //reset question num and type
    $("#questionTitle").text("Question #" + roomData.currentQuestion + ": " + ["Tossup","Bonus 1","Bonus 2"][roomData.curQuestionType]);
    
    //reset past Questions
    if(results.length > 0){
        $("#pastQuestions").empty();
        $("#pastQuestions").append($("<h1 ></h1>").text("Past Questions").css("text-align","center"));

        results.forEach(result => {
            if(result['questionNumber']>roomData['currentQuestion'])return;
            let question = $("<div class='pastQuestion'></div>").text("Tossup"+result['questionNumber'] ).attr("id", result['id']);
            question.on("mouseenter", (event)=>{
                $("#" + event.currentTarget.id).append($("<div class='hoverbox' id='hoverbox" + event.currentTarget.id + "'></div>").append($(`
                    <div class='center'>Tossup #${result['questionNumber']}</div>
                    <div>Question: ${result['tossupQuestion']}</div>
                    <div>Answer: ${result['tossupAnswer']}</div>
                
                `)))
            });
            question.on("mouseleave", (event)=>{
                $("#hoverbox" + event.currentTarget.id).remove();
            });
            $("#pastQuestions").append(question);
            // ['tossup','bonus1','bonus2'].forEach((type, index) =>{
            //      || result['questionNumber']==roomData['currentQuestion'] && index>= roomData['curQuestionType'])return;
            //     $("#pastQuestions").append(question);
            // })
            
        });
        //set up event listeners for all the pastQuesion  divs
        // $('.pastQuestion').on("mouseenter", (event)=>{
        //     console.log(event.currentTarget.id)
        //     $("#" + event.currentTarget.id).append($("<div class='hoverbox' id='hoverbox" + event.currentTarget.id + "'>Hello</div>"))
        // })
        // $('.pastQuestion').on("mouseleave", (event)=>{
        //     $("#hoverbox" + event.currentTarget.id).remove();
            
        // })
    }


}