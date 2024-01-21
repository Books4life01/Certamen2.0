//Global variables
let results = [];
let roomData = {};
let roomTeams = [];


//golbal timer for the wuestion timeout: used in liveQuestion.js
var intervalTimer;


//Document Ready
$(document).ready(() => {
    //call template specific document ready function
    documentReady();

    //requestion room Refresh
    socket.emit('roomHostConnect', data = {"roomKey": roomKey});
    socket.emit("roomDataRefreshRequest", data = {"roomKey": roomKey});
});

//Socket Handlers
socket.on('roomDataUpdate', data=>{
    if(data.privateKey == roomKey || data.publicKey == roomKey){
        //update the global room data
        roomData = data;
        //call template specific room data update function
        onRoomDataUpdate();
        if(results.length>0)resetResults();
        updateRoomStatistics();

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
        roomTeams = data.teams
        let teams = data.teams.map(team => team.privateKey);
        let droppableZones = document.getElementsByClassName("drop-zone");
        for(let i = 0; i<4; i++){
            let teamKey = teams[i];

            if(teamKey != "" && teamKey != null){
                let teamDiv = document.getElementById(teamKey);
                teamDiv.classList.add("selectedTeam");
                droppableZones[i].children[1].innerHTML = "";
                droppableZones[i].children[1].appendChild(teamDiv);
            }
        }
        updateRoomStatistics();
    }
});
socket.on("teamDataUpdate", (data)=>{
    //ensure the team we are recieving data for is a team in the room
    if([roomData.teamA, roomData.teamB, roomData.teamC, roomData.teamD].includes(data.privateKey)){
        //update the team data if it is already in the room Teams DataObject
        roomData.teamsData[data.privateKey] = data;
        //call template specific team data update function
        onRoomTeamsDataUpdate(data);
        updateRoomStatistics();
    }
})

socket.on("roomResultsUpdate", (data) =>{
    //Ensure that the room we are recieving data for is the room we are in
    if (data.roomKey == roomKey) {//roomKey is a global variable set in the html template

        console.log("Room Result Data Recieved from Server")
        console.log(data)
        results = data.resultList;
        //reset the result html stuff on the page to match the new results
        resetResults();
        updateRoomStatistics();
    }
    
});

socket.on("disconnect", () => {
    console.log("disconnected from server");
});