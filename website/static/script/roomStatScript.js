
function updateRoomStatistics(){
    if(roomData == undefined )return;
    let teams = roomTeams.map(team => ({"name":team.name, "key":team.privateKey,"points":0}));
    
    results.forEach(result => {
        let team = teams.find(team => team.key == result.teamAnsweredKey)
        if(team != undefined){
            team.points = team.points + result.totalPoints;
        }
    });
    teams.sort((a,b) => (a.points > b.points) ? -1 : ((b.points > a.points) ? 1 : 0));
    
    html = `
    `;
    counter = 1;
    teams.forEach(team => {
        if(team.name != undefined)html+= `<div class="teamRanking center">#${counter} ${team.name}: ${team.points}</div>`;
        counter++;
    });
    $("#roomStatisticInfo").empty();
    $("#roomStatisticInfo").append(html);

}