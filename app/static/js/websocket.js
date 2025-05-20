const socket = new WebSocket(`ws://${window.location.host}/ws`);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    switch(data.type) {
        case 'vote':
            updateVoteCount(data.featureId, data.votes);
            break;
        case 'comment':
            addNewComment(data.comment);
            break;
        case 'assignment':
            updateAssignment(data.featureId, data.assignee);
            break;
    }
};

function emitVote(featureId, vote) {
    socket.send(JSON.stringify({
        type: 'vote',
        featureId: featureId,
        vote: vote
    }));
}

function emitComment(featureId, comment) {
    socket.send(JSON.stringify({
        type: 'comment',
        featureId: featureId,
        comment: comment
    }));
}