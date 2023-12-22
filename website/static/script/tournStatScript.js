tournStats = {}


socket.on('tournStatData', function(data){
    if(data['tourn']['privateKey'] == tourn['privateKey']){
    tournStats = data;

    //Clear all the previous stats
    $("#topPlayers").empty();
    $("#topTeams").empty();
    $("#tournRooms").empty();
    $("#tournPlayers").empty();
    $("#tournTeams").empty();


    
    //update the leaderboards on the statistics page
    let topPlayers = getTopNPlayers(20);
    let topTeams = getTopNTeams(20);
    let fontSize = 1.5;

    //add top players divs to the horizantal movers
        topPlayers.forEach((player, index) =>{
            // $(".horizantalMover.first").append($("<div class='playerRanking'></div>").text(`#${index+1}:${topPlayers[index]['name']} ${topPlayers[index]['totalPoints']}`));
            // $(".horizantalMover.last").append($("<div class='playerRanking'></div>").text(`#${index+1}: ${topPlayers[index]['name']} ${topPlayers[index]['totalPoints']}`));
            $("#topPlayers").append($("<div class='playerRanking'></div>").text(`#${index+1}:${topPlayers[index]['name']} ${topPlayers[index]['totalPoints']}`));
        })
        // $(".horizantalMover.first").css("animation-duration", 16*topPlayers.length + "s");       
        // $(".horizantalMover.last").css("animation-duration", 16*topPlayers.length + "s");
        // $(".horizantalMover.last").css("animation-delay", 8*topPlayers.length + "s");

        topTeams.forEach((player, index) =>{
            // $(".verticalMover.first").append($("<div class='teamRanking'></div>").text(`#${index+1}:${topTeams[index]['name']} ${topTeams[index]['totalPoints']}`));
            // $(".verticalMover.last").append($("<div class='teamRanking'></div>").text(`#${index+1}: ${topTeams[index]['name']} ${topTeams[index]['totalPoints']}`));
            $("#topTeams").append($("<div class='teamRanking'></div>").text(`#${index+1}: ${topTeams[index]['name']} ${topTeams[index]['totalPoints']}`)).css("font-size", `${fontSize}rem`);
        })
        // $(".verticalMover.first").css("animation-duration", 16*topTeams.length + "s");       
        // $(".verticalMover.last").css("animation-duration", 16*topTeams.length + "s");
        // $(".verticalMover.last").css("animation-delay", 8*topTeams.length + "s");


        $("#tournStatsLabel").text(tourn["name"]);

        //General Data
        $("#roomNumber").text("Rooms: " + tournStats['rooms'].length);
        $("#playerNumber").text("Players: " + tournStats['players'].length);
        $("#teamNumber").text("Teams: " + tournStats['teams'].length);
        $("#tournRooms").append( $("<div id='roomDetails' class='center'></div>"));
        //List Rooms
        tournStats['rooms'].forEach(room => {
            let roomStatDiv = $("<div class='roomStatData'></div>");
            let roomStatDataContainer = $(`<div class='roomStatData collapse' id=R:${room['data']['publicKey']}></div>`);
            let roomStatData = $("<div class='card card-body'></div>");
            roomStatData.append($("<div ></div>").text("Live Players: " +( parseInt(room['data']['teamAPlayers']) + parseInt(room['data']['teamBPlayers']) + parseInt(room['data']['teamCPlayers']) + parseInt(room['data']['teamDPlayers']))));
            roomStatData.append($("<div></div>").text("Current Question: " + room['data']['curQuestionNumber']));
            roomStatData.append($("<div></div>").text("Status: " + ((room['data']['isLive'])?"LIVE":"OFFLINE")));
            roomStatData.append($("<div></div>").text("TEAMS: "));
            roomStatDiv.append($(`<button class='roomName' type='button'data-bs-toggle='collapse' data-bs-target=#R:${room['data']['publicKey']} aria-expanded='false' aria-controls=R:${room['data']['publicKey']}>></button>`).text(room['data']['name']).css("font-weight", "bold"));
            ['A', 'B', 'C', 'D'].forEach((letter) => {
             
                let key = "team" + letter;
                let teamKey = room['data'][key];
                if(teamKey != ""){
                    
                    let team = tournStats['teams'].find(tournTeam => tournTeam['privateKey'] == teamKey);
                    roomStatData.append($("<div class='roomTeam'></div>").text("Team " + letter + ": " + team['name'] + " " + getStatsForTeam(teamKey)["rooms"][room["data"]["name"]])); 
                }
            });
           
            //create a button that allosw you to download the room data
            roomStatData.append($(`<button type="button" class="button">Download Room Data</button>`).on("click", function(){
                downloadData(room,`${room['data']['name']} Data.txt`);
            }));
            roomStatDataContainer.append(roomStatData);
            roomStatDiv.append(roomStatDataContainer);
            //roomStatData.append($("<div class='roomPlayers'></div>").text("Players: " + room['data']['players'].length));
            ($("#roomDetails")).append(roomStatDiv);
        });

        //List Players
        tournStats['players'].forEach(player => {
            let playerStatDiv = $("<div class='playerStatData'></div>").append($(`<button type='button'data-bs-toggle='collapse' data-bs-target=#P:${player["privateKey"]} aria-expanded='false' aria-controls=P:${player["privateKey"]} ></button>`).text(player['name']).css("font-weight", "bold"));
            playerStatDiv.append($(`<div class='collapse' id=P:${player["privateKey"]}></div>`).append($(`<div class='card card-body'></div>`).append($("<div></div>").text("Points: " + getStatsForPlayer(player['publicKey'])['totalPoints'])).append($("<div></div>").text("Team: " + tournStats['teams'].find(team => team['privateKey'] == player['superTeam'])['name'])).append($("<div></div>")).append($(`<button type="button" class="button">Download Player Data</button>`).on("click", function(){downloadData(player,`${player['name']} Data.txt`);}))));
            
            $("#tournPlayers").append(playerStatDiv);
        });
         //List Players
         tournStats['teams'].forEach(team => {
            let teamStatDiv = $("<div class='teamStatData'></div>").append($(`<button type='button'data-bs-toggle='collapse' data-bs-target=#P:${team["privateKey"]} aria-expanded='false' aria-controls=P:${team["privateKey"]} ></button>`).text(team['name']).css("font-weight", "bold"));
            teamStatDiv.append($(`<div class='collapse' id=P:${team["privateKey"]}></div>`).append($(`<div class='card card-body'></div>`).append($("<div></div>").text("Points: " + getStatsForTeam(team['privateKey'])['totalPoints'])).append($("<div></div>")).text(
                ["1","2","3","4"].map((playerLetter) => {
                    const player = tournStats['players'].find(player => player['privateKey'] == team['player' + playerLetter])
                    return `P${playerLetter}` + (player?player['name']:"NONE") + "<br>";

                }).join("")
            ).append($(`<button type="button" class="button">Download Team Data</button>`).on("click", function(){downloadData(team,`${team['name']} Data.txt`);}))));
            
            $("#tournTeams").append(teamStatDiv);
        });
    }



    
    




});
function downloadData(data, fileName){
    let blob = new Blob([JSON.stringify(data, null, 2)], { type: 'text/plain' });
        // Create a link element and trigger the download
    var downloadLink = document.createElement('a');
    downloadLink.href = window.URL.createObjectURL(blob);
    downloadLink.download = fileName;
    downloadLink.click();
}

function reloadTournStats(){
    $("")
}
/**
 * 
 * @param {} playerKey the public key of 
 */
function getStatsForPlayer(playerKey){
    playerStats = {
        "name":tournStats["players"].find(player => player['publicKey'] == playerKey)['name'],
        "privateKey": tournStats['players'].find(player => player['publicKey'] == playerKey)['privateKey'], 
        "rooms":{},
        "totalPoints":0
    }
    tournStats['rooms'].forEach(room => {
        room['results'].forEach(result => {
            if(result['playerAnsweredKey'] == playerStats['privateKey']){
                playerStats['rooms'][room['data']['name']] = 10;
                playerStats['totalPoints']+=10;
            }
        });
    })
    return playerStats;
}
/**
 * 
 * @param {*} teamKey  private key of the team
 * @returns 
 */
function getStatsForTeam(teamKey){
    teamStats = {
        "name":tournStats["teams"].find(team => team['privateKey'] == teamKey)['name'],
        "privateKey": tournStats['teams'].find(team => team['privateKey'] == teamKey)['privateKey'],
        "rooms":{},
        "totalPoints":0
    }
    tournStats['rooms'].forEach(room => {
        teamStats['rooms'][room['data']['name']] = 0;
        room['results'].forEach(result => {
            if(result['teamAnsweredKey'] == teamKey){
                teamStats['rooms'][room['data']['name']] += parseInt(result['totalPoints']);
                teamStats['totalPoints']+=result['totalPoints'];
            }
        });
    });
    return teamStats;
}
function getTopNTeams(n){
    topTeams = [];
    tournStats['teams'].forEach(team => {
        let teamStats = getStatsForTeam(team['privateKey']);
        topTeams.push(teamStats);
    });
    //sort the teams by points
    topTeams.sort((a,b) => (a.totalPoints > b.totalPoints) ? -1 : ((b.totalPoints > a.totalPoints) ? 1 : 0));
    return topTeams.slice(0,n);
}
function getTopNPlayers(n){
    topPlayers = [];
    tournStats['players'].forEach(player => {
        let playerStats = getStatsForPlayer(player['publicKey']);
        topPlayers.push(playerStats);
    });
    //sort and slice the player Stats by points
    topPlayers.sort((a,b) => (a.totalPoints > b.totalPoints) ? -1 : ((b.totalPoints > a.totalPoints) ? 1 : 0));
    return topPlayers.slice(0,n);
}