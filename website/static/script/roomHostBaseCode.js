//Global variables
let curQuestion = 1;
let results = [];
let roomData = {};
const socket = io.connect('http://192.168.4.127:8080');

//Socket Handlers

socket.on('roomDataUpdate', data=>{
    if(data.privateKey == roomKey || data.publicKey == roomKey){
        console.log("Room Data Recieved from the Server")
        console.log(data);
        curQuestion = data.currentQuestion;
        curQuestionType = data.curQuestionType;
        roomData = data;
        $(".questionNum").text("Question #" + curQuestion);
        resetResults();
    }

});
socket.on("tournTeamsUpdate", (data) => {
    //Ensure that the room we are recieving data for is the room we are in
    if (data.tournKey == roomData.superTournament) {
        console.log("Tournament Teams Recieved from the Server")
        console.log(data);

        //clear the teams list
        $("#teamsList").empty().append("<h3>Available Teams</h3>");

        let teamsContainer = $("#teamsList");
        data.teams.forEach((team) => {
            let teamDiv = $("<div class='team'></div>");
            let teamName = $("<h4></h4>").text(team.name);
            teamDiv.append(teamName);
            teamDiv.addClass("team");
            teamDiv.attr("draggable", true);
            teamDiv.attr("id", team.privateKey);
            //create event listeners for draag start and end to add classes to the element being dragged
            teamDiv.on("dragstart", () =>teamDiv.addClass("dragging"));
            teamDiv.on("dragend", (event) =>{
                teamDiv.removeClass("dragging")
            });
            teamDiv.on("dragstart", () =>drag(event));
            teamsContainer.append(teamDiv);
        });
    }
});

socket.on("roomTeamsUpdate", (data) =>{
    //Ensure that the room we are recieving data for is the room we are in
    if (data.roomKey == roomKey){//roomKey is a global variable set in the html template
        let teams = data.teams;
        let droppableZones = document.getElementsByClassName("drop-zone");
        for(let i = 0; i<4; i++){
            let teamKey = teams[i];
            console.log("Team Key: " + teamKey);

            if(teamKey != "" && teamKey != null){
                let teamDiv = document.getElementById(teamKey);
                teamDiv.classList.add("selectedTeam");
                droppableZones[i].children[1].innerHTML = "";
                droppableZones[i].children[1].appendChild(teamDiv);
            }
        }
    }
});

socket.on("roomResultsUpdate", (data) =>{
    //Ensure that the room we are recieving data for is the room we are in
    if (data.roomKey == roomKey) {//roomKey is a global variable set in the html template

        console.log("Room Result Data Recieved from Server")
        console.log(data)
        results = data.resultList;
        //reset the result html stuff on the page to match the new results
        resetResults();
    }
    
});

socket.on("disconnect", () => {
    console.log("disconnected from server");
});