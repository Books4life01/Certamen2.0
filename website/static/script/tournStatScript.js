tournStats = {}


socket.on('tournStatData', function(data){
    if(data['tourn']['privateKey'] == tourn['privateKey']){
    tournStats = data;
    
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

        $("<div id='roomDetails' class='center'></div>").insertAfter($("#roomNumber"));
        //List Rooms
        tournStats['rooms'].forEach(room => {
            let roomStatData = $("<div class='roomStatData'></div>");
            roomStatData.append($("<div class='roomName'></div>").text(room['data']['name']).css("font-weight", "bold"));
            ['A', 'B', 'C', 'D'].forEach((letter) => {
                let key = "team" + letter;
                let teamKey = room['data'][key];
                if(teamKey != ""){
                    
                    let team = tournStats['teams'].find(tournTeam => tournTeam['privateKey'] == teamKey);
                    console.log(team)
                    roomStatData.append($("<div class='roomTeam'></div>").text("Team " + letter + ": " + team['name'] + " " + getStatsForTeam(teamKey)["rooms"][room["data"]["name"]])); 
                }
            });
            //roomStatData.append($("<div class='roomPlayers'></div>").text("Players: " + room['data']['players'].length));
            ($("#roomDetails")).append(roomStatData);
        });
    }



    
    




});

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
                playerStats['rooms'][room['data']['name']] = result['totalPoints'];
                playerStats['totalPoints']+=result['totalPoints'];
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
        room['results'].forEach(result => {
            if(result['teamAnsweredKey'] == teamKey){
                teamStats['rooms'][room['data']['name']] = result['totalPoints'];
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