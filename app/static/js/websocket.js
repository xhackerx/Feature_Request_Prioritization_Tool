const socket = io();

socket.on('connect', () => {
    console.log('Connected to WebSocket server');
});

socket.on('features_update', (data) => {
    updateFeatureList(data.features);
});

function updateFeatureList(features) {
    const featureList = document.getElementById('feature-list');
    if (!featureList) return;

    featureList.innerHTML = '';
    features.forEach(feature => {
        const featureElement = document.createElement('div');
        featureElement.className = 'feature-item';
        featureElement.innerHTML = `
            <h3>${feature.title}</h3>
            <div class="score-info">
                <span class="priority-score">Priority: ${feature.priority_score.toFixed(2)}</span>
                <span class="impact">Impact: ${feature.user_impact}</span>
                <span class="effort">Effort: ${feature.effort_required}</span>
                <span class="alignment">Strategic: ${feature.strategic_alignment}</span>
            </div>
        `;
        featureList.appendChild(featureElement);
    });
}

// Request updates periodically
setInterval(() => {
    socket.emit('request_update');
}, 30000); // Update every 30 seconds