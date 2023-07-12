function drag(event){
    event.dataTransfer.setData("text", event.target.id);
    console.log("dragging:", event.target.id)
}
function drop(event){
    event.preventDefault();//prevents default action of dropping which is to block the drop
    var data = event.dataTransfer.getData("text");//retrieves the id of the element to drop  sent by the drag funcion
    //ensure the target is a droppable element and if it isnt retrive its parent element
    let target = event.target;
    console.log(target)
    while(!target.classList.contains("droppable") && !target.classList.contains("overflow-container")){
        target = target.parentElement;
    }
    console.log(target)

    //remove all children from the target element and if the child is draggable reappend it to the teams list
    Array.from(target.children).forEach((child) => {
        if(child.getAttribute("draggable")){
            child.classList.remove("selectedTeam");
            document.getElementById("teamsList").appendChild(child);
        }
        else target.removeChild(child);
    });

    //add the selected team class to the element being dropped
    let elem = document.getElementById(data);
    let parent = elem.parentElement;

    if(target.classList.contains("droppable"))elem.classList.add("selectedTeam");
    else elem.classList.remove("selectedTeam");
    
    //append the element to the drop target
    target.appendChild(elem);
    //if parent has droppable class 
    if(parent.classList.contains("droppable")){
       //add the "Add Team Here" text back
       let h1 = document.createElement("h1");
          h1.innerHTML = "Add Team Here";
       parent.appendChild(h1);
    }

    //update the server with the new team assignments
    let teamA = document.getElementById("Team A").children[1].children[0].id ;
    let teamB = document.getElementById("Team B").children[1].children[0].id;
    let teamC = document.getElementById("Team C").children[1].children[0].id;
    let teamD = document.getElementById("Team D").children[1].children[0].id;
    socket.emit("teamAssignmentUpdate", data = {
        "roomKey": roomKey,
        "teamA": teamA,
        "teamB": teamB,
        "teamC": teamC,
        "teamD": teamD
    });
}
//prevents default action of dropping which is to block the drop
function allowDrop(event){
    event.preventDefault();
}