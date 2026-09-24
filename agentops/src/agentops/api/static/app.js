document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('incidentForm');
    const submitBtn = document.getElementById('submitBtn');
    const timeline = document.getElementById('timeline');
    const statusBadge = document.getElementById('workflowStatus');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // UI Loading State
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        timeline.innerHTML = ''; // clear timeline
        statusBadge.textContent = 'RUNNING...';
        statusBadge.style.color = 'var(--accent-blue)';

        const payload = {
            service: document.getElementById('service').value,
            requested_autonomy_tier: parseInt(document.getElementById('tier').value),
            description: document.getElementById('description').value
        };

        try {
            const response = await fetch('/v1/incidents/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('API request failed');

            const data = await response.json();
            renderTrace(data.events);

            statusBadge.textContent = 'COMPLETED';
            statusBadge.style.color = 'var(--success)';

        } catch (error) {
            console.error(error);
            statusBadge.textContent = 'FAILED';
            statusBadge.style.color = 'var(--danger)';
            addTimelineItem('system', 'ERROR', { error: error.message }, 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('loading');
        }
    });

    function renderTrace(events) {
        // Render events sequentially for a cool animated effect
        let delay = 0;
        
        events.forEach((event, index) => {
            setTimeout(() => {
                let type = 'success';
                if (event.status === 'WAITING_FOR_APPROVAL') type = 'warning';
                if (event.status === 'DENIED' || event.status === 'FAILED') type = 'danger';

                addTimelineItem(event.node, event.status, event.details, type);
            }, delay);
            delay += 600; // 600ms stagger
        });
    }

    function addTimelineItem(node, status, details, type) {
        const item = document.createElement('div');
        item.className = `timeline-item ${type}`;
        
        let detailsHtml = '';
        if (details) {
            for (const [key, value] of Object.entries(details)) {
                let displayVal = value;
                if (Array.isArray(value)) displayVal = value.map(v => JSON.stringify(v)).join('<br>');
                detailsHtml += `<div class="detail-row"><strong>${key.toUpperCase()}:</strong> ${displayVal}</div>`;
            }
        }

        item.innerHTML = `
            <div class="item-header">
                <span class="node-name">${node} Agent</span>
                <span class="node-status">${status}</span>
            </div>
            ${detailsHtml ? `<div class="item-content">${detailsHtml}</div>` : ''}
        `;
        
        timeline.appendChild(item);
        
        // Scroll to bottom
        const panel = timeline.closest('.panel');
        panel.scrollTop = panel.scrollHeight;
    }
});
