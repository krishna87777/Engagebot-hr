/**
 * Enhanced Sentiment Analysis JavaScript
 * Handles form submission and results display for employee sentiment analysis
 * with improved animations and visual feedback
 */
const { jsPDF } = window.jspdf;

document.addEventListener('DOMContentLoaded', function() {
    // Form elements
    const form = document.getElementById('sentiment-analysis-form');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');

    // Results elements
    const gaugeNeedle = document.getElementById('gauge-needle');
    const gaugeContainer = document.getElementById('gauge-container');
    const sentimentInterpretation = document.getElementById('sentiment-interpretation');
    const riskLevel = document.getElementById('risk-level');
    const riskText = document.getElementById('risk-text');
    const concernsList = document.getElementById('concerns-list');
    const positivesList = document.getElementById('positives-list');
    const recommendationsText = document.getElementById('recommendations-text');

    // Action buttons
    const downloadButton = document.getElementById('download-results');
    const newAnalysisButton = document.getElementById('new-analysis');

    // Handle form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Show loading indicator
            loadingIndicator.classList.remove('hidden');
            resultsContainer.classList.add('hidden');

            // Reset gauge animation
            if (gaugeNeedle) {
                gaugeNeedle.style.transform = 'translateX(-50%) rotate(90deg)';
                gaugeNeedle.style.transition = 'none';
            }

            // Get form data
            const feedbackType = document.getElementById('feedback-type').value;
            const feedbackText = document.getElementById('feedback-text').value;

            // Submit form via AJAX
            fetch('/api/analyze-sentiment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    feedback_type: feedbackType,
                    feedback: feedbackText
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server responded with an error');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading indicator
                loadingIndicator.classList.add('hidden');

                // Prepare for animation
                if (gaugeNeedle) {
                    gaugeNeedle.style.transition = 'transform 1.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                }

                // Display results with animation
                setTimeout(() => {
                    displayResults(data);
                    resultsContainer.classList.remove('hidden');

                    // Add entrance animation to results
                    animateResultsEntrance();
                }, 150);
            })
            .catch(error => {
                console.error('Error:', error);
                loadingIndicator.classList.add('hidden');
                alert('An error occurred while processing your request.');
            });
        });
    }

    // Function to animate results entrance
    function animateResultsEntrance() {
        const elements = document.querySelectorAll('.result-summary, .factors-section, .recommendations');
        elements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 150 * index);
        });
    }

    // Function to display results
    function displayResults(data) {
        // Store data for PDF generation
        window.lastSentimentData = data;

        // Set sentiment gauge rotation based on sentiment score (-1 to 1)
        // Convert to 0-180 degrees for the gauge
        const sentimentDegrees = ((data.sentiment_score + 1) / 2) * 180;

        // Update gauge needle with improved animation
        if (gaugeNeedle) {
            gaugeNeedle.style.transform = `translateX(-50%) rotate(${sentimentDegrees}deg)`;
        }

        // Update gauge color based on sentiment score
        updateGaugeColor(data.sentiment_score);

        // Set sentiment interpretation text with visual indicator
        const interpretation = data.interpretation || 'Neutral';
        sentimentInterpretation.textContent = interpretation;

        // Apply color class to sentiment interpretation
        updateSentimentColor(interpretation);

        // Set attrition risk level with animation
        const riskPercentages = {
            'Low': 33,
            'Medium': 66,
            'High': 100
        };

        const riskColors = {
            'Low': 'var(--success-color)',
            'Medium': 'var(--warning-color)',
            'High': 'var(--danger-color)'
        };

        const risk = data.attrition_risk || 'Medium';

        // Animate risk level
        if (riskLevel) {
            riskLevel.style.width = '0%';
            setTimeout(() => {
                riskLevel.style.width = `${riskPercentages[risk]}%`;
                riskLevel.style.backgroundColor = riskColors[risk];
            }, 200);
        }

        if (riskText) {
            riskText.textContent = `${risk} Risk`;
            riskText.className = ''; // Reset classes
            riskText.classList.add(`risk-${risk.toLowerCase()}`);
        }

        // Clear existing concerns and positives lists
        if (concernsList) concernsList.innerHTML = '';
        if (positivesList) positivesList.innerHTML = '';

        // Populate concerns list with staggered animation
        if (data.key_concerns && data.key_concerns.length > 0) {
            data.key_concerns.forEach((concern, index) => {
                const li = document.createElement('li');
                li.textContent = concern;
                li.style.opacity = '0';
                li.style.transform = 'translateX(-10px)';
                li.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                concernsList.appendChild(li);

                setTimeout(() => {
                    li.style.opacity = '1';
                    li.style.transform = 'translateX(0)';
                }, 100 * index);
            });
        } else {
            // Add a placeholder if no concerns
            const li = document.createElement('li');
            li.textContent = "No significant concerns detected";
            li.classList.add('placeholder-text');
            concernsList.appendChild(li);
        }

        // Populate positives list with staggered animation
        if (data.positive_factors && data.positive_factors.length > 0) {
            data.positive_factors.forEach((positive, index) => {
                const li = document.createElement('li');
                li.textContent = positive;
                li.style.opacity = '0';
                li.style.transform = 'translateX(-10px)';
                li.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                positivesList.appendChild(li);

                setTimeout(() => {
                    li.style.opacity = '1';
                    li.style.transform = 'translateX(0)';
                }, 100 * index);
            });
        } else {
            // Add a placeholder if no positives
            const li = document.createElement('li');
            li.textContent = "No specific positive factors highlighted";
            li.classList.add('placeholder-text');
            positivesList.appendChild(li);
        }

        // Set recommendations with improved formatting
        if (recommendationsText) {
            let recommendationsContent = '';

            if (data.recommendations) {
                // If recommendations is already formatted as a string
                recommendationsContent = data.recommendations;
            } else if (data.engagement_recommendations && data.engagement_recommendations.length > 0) {
                // If we have engagement_recommendations array, format it with bullet points
                recommendationsContent = "• " + data.engagement_recommendations.join("\n• ");
            } else {
                // Fallback if no recommendations found
                recommendationsContent = "• Continue monitoring employee engagement\n• Consider follow-up discussions for more detailed feedback";
            }

            // Split into lines for better animation
            const recLines = recommendationsContent.split("\n");
            recommendationsText.innerHTML = '';

            recLines.forEach((line, index) => {
                const p = document.createElement('p');
                p.textContent = line;
                p.style.opacity = '0';
                p.style.transform = 'translateY(10px)';
                p.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                recommendationsText.appendChild(p);

                setTimeout(() => {
                    p.style.opacity = '1';
                    p.style.transform = 'translateY(0)';
                }, 150 * index);
            });
        }
    }

    // Function to update gauge color based on sentiment score
    function updateGaugeColor(score) {
        // Don't proceed if gauge container doesn't exist
        if (!gaugeContainer) return;

        // Normalize score from -1,1 to 0,1
        const normalizedScore = (score + 1) / 2;

        let gaugeClass = '';
        if (normalizedScore < 0.33) {
            gaugeClass = 'gauge-negative';
        } else if (normalizedScore < 0.66) {
            gaugeClass = 'gauge-neutral';
        } else {
            gaugeClass = 'gauge-positive';
        }

        // Reset classes and add appropriate one
        gaugeContainer.className = 'score-gauge';
        gaugeContainer.classList.add(gaugeClass);
    }

    // Function to update sentiment text color
    function updateSentimentColor(interpretation) {
        if (!sentimentInterpretation) return;

        // Remove existing color classes
        sentimentInterpretation.classList.remove('text-negative', 'text-neutral', 'text-positive', 'text-very-positive', 'text-very-negative');

        // Add appropriate class
        const lowerInterpretation = interpretation.toLowerCase();
        if (lowerInterpretation.includes('very negative')) {
            sentimentInterpretation.classList.add('text-very-negative');
        } else if (lowerInterpretation.includes('negative')) {
            sentimentInterpretation.classList.add('text-negative');
        } else if (lowerInterpretation.includes('neutral')) {
            sentimentInterpretation.classList.add('text-neutral');
        } else if (lowerInterpretation.includes('very positive')) {
            sentimentInterpretation.classList.add('text-very-positive');
        } else if (lowerInterpretation.includes('positive')) {
            sentimentInterpretation.classList.add('text-positive');
        }
    }

    // Handle "New Analysis" button click
    if (newAnalysisButton) {
        newAnalysisButton.addEventListener('click', function(e) {
            e.preventDefault();

            // Reset form
            form.reset();

            // Hide results and scroll to form with smooth animation
            if (resultsContainer) {
                resultsContainer.style.opacity = '1';
                resultsContainer.style.transition = 'opacity 0.5s ease';

                setTimeout(() => {
                    resultsContainer.style.opacity = '0';

                    setTimeout(() => {
                        resultsContainer.classList.add('hidden');
                        resultsContainer.style.opacity = '1';
                        form.scrollIntoView({ behavior: 'smooth' });
                    }, 500);
                }, 100);
            }
        });
    }

    function generatePDF(data) {
        const doc = new jsPDF();

        let y = 10;

        doc.setFontSize(16);
        doc.text("Employee Sentiment Analysis Report", 10, y);
        y += 10;

        doc.setFontSize(12);
        doc.text(`Sentiment Score: ${data.sentiment_score}`, 10, y);
        y += 8;
        doc.text(`Sentiment Interpretation: ${data.interpretation}`, 10, y);
        y += 8;
        doc.text(`Attrition Risk: ${data.attrition_risk}`, 10, y);
        y += 8;

        doc.text("Summary:", 10, y);
        y += 8;
        const summaryLines = doc.splitTextToSize(data.summary || "No summary provided.", 180);
        doc.text(summaryLines, 10, y);
        y += summaryLines.length * 6;

        doc.text("Key Concerns:", 10, y);
        y += 8;
        const concerns = data.key_concerns?.length ? data.key_concerns : ["No significant concerns detected"];
        concerns.forEach(concern => {
            const lines = doc.splitTextToSize(`• ${concern}`, 180);
            doc.text(lines, 10, y);
            y += lines.length * 6;
        });

        doc.text("Positive Factors:", 10, y);
        y += 8;
        const positives = data.positive_factors?.length ? data.positive_factors : ["No specific positive factors highlighted"];
        positives.forEach(pos => {
            const lines = doc.splitTextToSize(`• ${pos}`, 180);
            doc.text(lines, 10, y);
            y += lines.length * 6;
        });

        doc.text("Engagement Recommendations:", 10, y);
        y += 8;
        const recs = data.engagement_recommendations?.length ? data.engagement_recommendations : [
            "Continue monitoring employee engagement",
            "Consider follow-up discussions for more detailed feedback"
        ];
        recs.forEach(rec => {
            const lines = doc.splitTextToSize(`• ${rec}`, 180);
            doc.text(lines, 10, y);
            y += lines.length * 6;
        });

        doc.save('sentiment_analysis_report.pdf');
    }

    // Handle "Download Report" button click with improved feedback
    if (downloadButton) {
        downloadButton.addEventListener('click', function(e) {
            e.preventDefault();

            // Visual feedback for download button
            this.classList.add('button-loading');

            setTimeout(() => {
                if (window.lastSentimentData) {
                    generatePDF(window.lastSentimentData);
                    this.classList.remove('button-loading');

                    // Show success message
                    const originalText = this.textContent;
                    this.textContent = "Downloaded!";
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                } else {
                    this.classList.remove('button-loading');
                    alert('No analysis data found. Please run a sentiment analysis first.');
                }
            }, 500);
        });
    }
});