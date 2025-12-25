let dealerChart, modelChart, serviceChart;

function fetchCharts() {
    const filters = {
        dealer_id: document.getElementById('dealerDropdown').value,
        model: document.getElementById('modelDropdown').value,
        min_price: Number(document.getElementById('minPrice').value),
        max_price: Number(document.getElementById('maxPrice').value)
    };

    fetch('/get_charts', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(filters)
    })
    .then(res => res.json())
    .then(data => {
        // Dealer Bar Chart
        const dealerLabels = data.dealer.map(d => d._id);
        const dealerCounts = data.dealer.map(d => d.count);
        if(dealerChart) dealerChart.destroy();
        dealerChart = new Chart(document.getElementById('dealerChart'), {
            type: 'bar',
            data: { labels: dealerLabels, datasets: [{ label: 'Cars per Dealer', data: dealerCounts, backgroundColor: 'teal' }] }
        });

        // Model Pie Chart
        const modelLabels = data.model.map(d => d._id);
        const modelCounts = data.model.map(d => d.count);
        if(modelChart) modelChart.destroy();
        modelChart = new Chart(document.getElementById('modelChart'), {
            type: 'pie',
            data: { labels: modelLabels, datasets: [{ label: 'Model Distribution', data: modelCounts, backgroundColor: ['red','blue','green','orange'] }] }
        });

        // Service Line Chart
        const serviceLabels = data.service.map(d => d._id);
        const serviceCosts = data.service.map(d => d.total_cost);
        if(serviceChart) serviceChart.destroy();
        serviceChart = new Chart(document.getElementById('serviceChart'), {
            type: 'line',
            data: { labels: serviceLabels, datasets: [{ label: 'Service Costs', data: serviceCosts, borderColor: 'purple', fill: false }] }
        });
    });
}


document.getElementById('minPrice').addEventListener('input', () => {
    document.getElementById('minPriceVal').innerText = document.getElementById('minPrice').value;
});
document.getElementById('maxPrice').addEventListener('input', () => {
    document.getElementById('maxPriceVal').innerText = document.getElementById('maxPrice').value;
});

// Apply filters button
document.getElementById('applyFilters').addEventListener('click', fetchCharts);

// Initial load
fetchCharts();
