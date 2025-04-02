/*document.addEventListener('DOMContentLoaded', function() {
    const customerForm = document.getElementById('customerForm');
    const submitBtn = document.getElementById('submitBtn');
    const predictBtn = document.getElementById('predictBtn');
    const resultsCard = document.getElementById('resultsCard');
    const predictionCard = document.getElementById('predictionCard');
    const customerData = document.getElementById('customerData');
    const churnPredictionEl = document.getElementById('churnPrediction');
    const churnProbabilityEl = document.getElementById('churnProbability');
    const cltvPredictionEl = document.getElementById('cltvPrediction');
    const customerValueEl = document.getElementById('customerValue');
    const insightsText = document.getElementById('insightsText');

    // Fetch customer data
    customerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const customerId = document.getElementById('customerId').value.trim();
        if (!customerId) {
            alert('Please enter a Customer ID.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loader"></div>'; // Loading effect

        fetch(`http://127.0.0.1:5000/api/customer/${customerId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Customer ID not found');
                }
                return response.json();
            })
            .then(data => {
                console.log("✅ Customer Data Received:", data);
                displayCustomerData(data);
                resultsCard.style.display = 'block';
                predictionCard.style.display = 'none';
            })
            .catch(error => {
                alert(error.message);
                resultsCard.style.display = 'none';
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span class="btn-text">Analyze</span><i class="fas fa-chart-line"></i>';
            });
    });

    // Display customer data
    function displayCustomerData(data) {
        customerData.innerHTML = `
            <h4>Customer Details</h4>
            
            <p><strong>Name:</strong> ${data.Gender ?? 'N/A'}</p>
            <p><strong>City:</strong> ${data.City ?? 'N/A'}</p>
            <p><strong>State:</strong> ${data.State ?? 'N/A'}</p>
            <p><strong>Churn Label:</strong> ${data["Churn Label"] ?? 'N/A'}</p>
            <p><strong>Churn Score:</strong> ${data["Churn Score"] ?? 'N/A'}</p>
            <p><strong>Churn Reason:</strong> ${data["Churn Reason"] ?? 'N/A'}</p>
            <p><strong>CLTV:</strong> $${data.CLTV ?? 'N/A'}</p>
            <p><strong>Contract:</strong> ${data.Contract ?? 'N/A'}</p>
            <p><strong>Monthly Charges:</strong> $${data["Monthly Charges"] ?? 'N/A'}</p>
            <p><strong>Total Charges:</strong> $${data["Total Charges"] ?? 'N/A'}</p>
            <p><strong>Tenure:</strong> ${data["Tenure Months"] ?? 'N/A'} months</p>
        `;
    }

    // Predict button click
    predictBtn.addEventListener('click', function() {
        const customerId = document.getElementById('customerId').value.trim();
        if (!customerId) {
            alert('Please analyze a customer first.');
            return;
        }

        predictBtn.disabled = true;
        predictBtn.innerHTML = '<div class="loader"></div>';

        fetch('http://127.0.0.1:5000/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "CustomerID": customerId })
        })
        .then(response => response.json())
        .then(data => {
            displayPrediction(data);
            predictionCard.style.display = 'block';
            resultsCard.style.display = 'none';
        })
        .catch(error => {
            alert('Error predicting: ' + error.message);
            predictionCard.style.display = 'none';
        })
        .finally(() => {
            predictBtn.disabled = false;
            predictBtn.innerHTML = '<span class="btn-text">Predict</span><i class="fas fa-predict"></i>';
        });
    });

    // Display prediction results
    function displayPrediction(data) {
        churnPredictionEl.textContent = data.churn_prediction ? 'Yes' : 'No';
        churnProbabilityEl.textContent = `Probability: ${data.churn_probability !== undefined ? (data.churn_probability * 100).toFixed(2) : 'N/A'}%`;
        cltvPredictionEl.textContent = `$${data.cltv_prediction !== undefined ? data.cltv_prediction.toFixed(2) : 'N/A'}`;
        customerValueEl.textContent = `Tier: ${data.customer_value || 'N/A'}`;

        insightsText.innerHTML = '';
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const insightItem = document.createElement('div');
                insightItem.className = 'insight-item';
                insightItem.innerHTML = `<i class="fas fa-chevron-right"></i> <span>${rec}</span>`;
                insightsText.appendChild(insightItem);
            });
        }
    }
});*/

/*app2.js */

document.addEventListener('DOMContentLoaded', function() {
    const customerForm = document.getElementById('customerForm');
    const submitBtn = document.getElementById('submitBtn');
    const predictBtn = document.getElementById('predictBtn');
    const resultsCard = document.getElementById('resultsCard');
    const predictionCard = document.getElementById('predictionCard');
    const customerData = document.getElementById('customerData');
    const churnPredictionEl = document.getElementById('churnPrediction');
    const churnProbabilityEl = document.getElementById('churnProbability');
    const cltvPredictionEl = document.getElementById('cltvPrediction');
    const customerValueEl = document.getElementById('customerValue');
    const insightsText = document.getElementById('insightsText');

    // Fetch customer data
    customerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const customerId = document.getElementById('customerId').value.trim();
        if (!customerId) {
            alert('Please enter a Customer ID.');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<div class="loader"></div>';

        fetch(`/api/customer/${encodeURIComponent(customerId)}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || 'Customer not found'); });
                }
                return response.json();
            })
            .then(data => {
                if (data.status !== 'success') {
                    throw new Error(data.error || 'Failed to fetch customer data');
                }
                displayCustomerData(data.customer);
                resultsCard.style.display = 'block';
                predictionCard.style.display = 'none';
            })
            .catch(error => {
                alert(error.message);
                resultsCard.style.display = 'none';
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span class="btn-text">Analyze</span><i class="fas fa-chart-line"></i>';
            });
    });
    // Display customer data
    function displayCustomerData(data) {
        customerData.innerHTML = `
            <h4>Customer Details</h4>
            <div class="customer-details-grid">
                <div class="detail-item">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">${data.Gender || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">City:</span>
                    <span class="detail-value">${data.City || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">State:</span>
                    <span class="detail-value">${data.State || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Churn Label:</span>
                    <span class="detail-value">${data['Churn Label'] || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Churn Score:</span>
                    <span class="detail-value">${data['Churn Score'] || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Churn Reason:</span>
                    <span class="detail-value">${data['Churn Reason'] || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">CLTV:</span>
                    <span class="detail-value">${data.CLTV ? '$' + data.CLTV : 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Contract:</span>
                    <span class="detail-value">${data.Contract || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Monthly Charges:</span>
                    <span class="detail-value">${data['Monthly Charges'] ? '$' + data['Monthly Charges'] : 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Total Charges:</span>
                    <span class="detail-value">${data['Total Charges'] ? '$' + data['Total Charges'] : 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Tenure:</span>
                    <span class="detail-value">${data['Tenure Months'] || 'N/A'} months</span>
                </div>
            </div>
        `;
    }

    // Predict button click
    predictBtn.addEventListener('click', function() {
        const customerId = document.getElementById('customerId').value.trim();
        if (!customerId) {
            alert('Please analyze a customer first.');
            return;
        }

        predictBtn.disabled = true;
        predictBtn.innerHTML = '<div class="loader"></div>';

        fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "CustomerID": customerId })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Prediction failed'); });
            }
            return response.json();
        })
        .then(data => {
            if (data.status !== 'success') {
                throw new Error(data.error || 'Prediction failed');
            }
            displayPrediction(data);
            predictionCard.style.display = 'block';
            resultsCard.style.display = 'none';
        })
        .catch(error => {
            alert('Error: ' + error.message);
            predictionCard.style.display = 'none';
        })
        .finally(() => {
            predictBtn.disabled = false;
            predictBtn.innerHTML = '<span class="btn-text">Predict</span><i class="fas fa-magic"></i>';
        });
    });

    // Display prediction results
    function displayPrediction(data) {
        // Update churn prediction
        churnPredictionEl.textContent = data.churn_prediction ? 'High Risk' : 'Low Risk';
        churnPredictionEl.className = data.churn_prediction ? 'prediction-bad' : 'prediction-good';
        
        // Update probability
        churnProbabilityEl.textContent = `${data.churn_probability !== undefined ? (data.churn_probability * 100).toFixed(2) : 'N/A'}%`;
        churnProbabilityEl.style.color = data.churn_prediction ? '#ff4d4d' : '#4CAF50';
        
        // Update CLTV
        cltvPredictionEl.textContent = data.cltv_prediction !== undefined ? `$${data.cltv_prediction.toFixed(2)}` : 'N/A';
        
        // Update customer value
        customerValueEl.textContent = data.customer_value || 'N/A';
        customerValueEl.className = data.customer_value === 'Premium' ? 'value-premium' : 'value-standard';
        
        // Update recommendations
        insightsText.innerHTML = '';
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(rec => {
                const insightItem = document.createElement('div');
                insightItem.className = 'insight-item';
                insightItem.innerHTML = `<i class="fas fa-lightbulb"></i> <span>${rec}</span>`;
                insightsText.appendChild(insightItem);
            });
        } else {
            insightsText.innerHTML = '<div class="no-recommendations">No specific recommendations for this customer</div>';
        }
    }
});
