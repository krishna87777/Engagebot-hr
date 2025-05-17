const { jsPDF } = window.jspdf;

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('resume-screening-form');
    const fileInput = document.getElementById('resume');
    const fileNameDisplay = document.getElementById('file-name');
    const loadingIndicator = document.getElementById('loading');
    const resultsContainer = document.getElementById('results');

    const matchPercentage = document.getElementById('match-percentage');
    const experienceMatch = document.getElementById('experience-match');
    const educationMatch = document.getElementById('education-match');
    const skillsMatchedList = document.getElementById('skills-matched-list');
    const skillsMissingList = document.getElementById('skills-missing-list');
    const recommendationsText = document.getElementById('recommendations-text');
    const recommendationsList = document.getElementById('recommendations-list');

    const downloadButton = document.getElementById('download-results');
    const newScreeningButton = document.getElementById('new-screening');

    if (fileInput && fileNameDisplay) {
        fileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                fileNameDisplay.textContent = this.files[0].name;
            } else {
                fileNameDisplay.textContent = 'No file selected';
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            loadingIndicator.classList.remove('hidden');
            resultsContainer.classList.add('hidden');

            const formData = new FormData(form);

            fetch('/api/screen-resume', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Server responded with an error');
                    });
                }
                return response.json();
            })
            .then(data => {
                loadingIndicator.classList.add('hidden');
                displayResults(data);
                resultsContainer.classList.remove('hidden');

                // Smooth scroll to results
                resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            })
            .catch(error => {
                loadingIndicator.classList.add('hidden');
                alert(`An error occurred: ${error.message}`);
            });
        });
    }

    function displayResults(data) {
        // Main match score
        matchPercentage.textContent = `${data.match_score}%`;

        const scoreCircle = document.querySelector('.score-circle');
        if (scoreCircle) {
            scoreCircle.style.setProperty('--score-height', `${data.match_score}%`);

            // Add color class based on score
            scoreCircle.className = 'score-circle';
            if (data.match_score >= 80) {
                scoreCircle.classList.add('score-high');
            } else if (data.match_score >= 60) {
                scoreCircle.classList.add('score-medium');
            } else {
                scoreCircle.classList.add('score-low');
            }
        }

        // Experience and education matches
        experienceMatch.textContent = `Experience: ${data.experience_match ? 'Match' : 'No Match'}`;
        educationMatch.textContent = `Education: ${data.education_match ? 'Match' : 'No Match'}`;

        experienceMatch.previousElementSibling.className = data.experience_match ?
            'fas fa-check-circle' : 'fas fa-times-circle';
        educationMatch.previousElementSibling.className = data.education_match ?
            'fas fa-check-circle' : 'fas fa-times-circle';

        experienceMatch.previousElementSibling.style.color = data.experience_match ?
            'var(--success-color)' : 'var(--danger-color)';
        educationMatch.previousElementSibling.style.color = data.education_match ?
            'var(--success-color)' : 'var(--danger-color)';

        // Skills analysis
        skillsMatchedList.innerHTML = '';
        skillsMissingList.innerHTML = '';

        // Sort skills alphabetically for better readability
        const sortedMatchedSkills = [...data.skills_matched].sort();
        const sortedMissingSkills = [...data.skills_missing].sort();

        sortedMatchedSkills.forEach(skill => {
            const li = document.createElement('li');
            li.textContent = skill;
            li.className = 'skill-item skill-matched';
            skillsMatchedList.appendChild(li);
        });

        sortedMissingSkills.forEach(skill => {
            const li = document.createElement('li');
            li.textContent = skill;
            li.className = 'skill-item skill-missing';
            skillsMissingList.appendChild(li);
        });

        // AI Recommendations section
        if (recommendationsList) {
            recommendationsList.innerHTML = '';

            // Generate AI recommendations based on analysis
            const recommendations = generateRecommendations(data);

            recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                li.className = 'recommendation-item';
                recommendationsList.appendChild(li);
            });

            // Show recommendations section
            const recommendationsSection = document.getElementById('ai-recommendations-section');
            if (recommendationsSection) {
                recommendationsSection.classList.remove('hidden');
            }
        }

        // If there's a specific recommendations text from the API
        if (recommendationsText && data.recommendations) {
            recommendationsText.textContent = data.recommendations;
        }
        //console.log(data);
    }

    function generateRecommendations(data) {
        const recommendations = [];

        // Recommend based on overall match score
        if (data.match_score < 60) {
            recommendations.push("Consider exploring candidates with more relevant skills for this position.");
        } else if (data.match_score >= 80) {
            recommendations.push("This candidate appears to be a strong match for the position. Consider moving forward with an interview.");
        } else {
            recommendations.push("This candidate has some relevant skills but may need additional training in certain areas.");
        }

        // Recommend based on experience match
        if (!data.experience_match) {
            recommendations.push("The candidate lacks the required experience level. Consider discussing their practical knowledge in key areas during an interview.");
        }

        // Recommend based on missing skills
        if (data.skills_missing && data.skills_missing.length > 0) {
            if (data.skills_missing.length <= 2) {
                recommendations.push(`The candidate is missing ${data.skills_missing.join(" and ")}. Consider assessing their ability to learn these skills quickly.`);
            } else if (data.skills_missing.includes("Business Analysis")) {
                recommendations.push("Consider providing Business Analysis training if hiring this candidate.");
            } else {
                recommendations.push(`The candidate is missing ${data.skills_missing.length} required skills. Evaluate their learning capacity and willingness to acquire new skills.`);
            }
        }

        // Add a generic recommendation if none were generated
        if (recommendations.length === 0) {
            recommendations.push("Review the candidate's background and consider how well they might fit with your team culture.");
        }

        return recommendations;
    }

    if (newScreeningButton) {
        newScreeningButton.addEventListener('click', function (e) {
            e.preventDefault();
            form.reset();
            fileNameDisplay.textContent = 'No file selected';
            resultsContainer.classList.add('hidden');
            form.scrollIntoView({ behavior: 'smooth' });
        });
    }

    if (downloadButton) {
        downloadButton.addEventListener('click', function (e) {
            e.preventDefault();
            generatePDF();
        });
    }

    function generatePDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const candidateName = document.getElementById('file-name').textContent || 'Candidate';
    const jobTitle = document.getElementById('job-description')?.value || 'Position';
    const date = new Date().toLocaleDateString();

    let y = 10;

    doc.setFontSize(18);
    doc.setTextColor(40, 40, 100);
    doc.text("Resume Screening Report", 10, y);
    y += 10;

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Candidate: ${candidateName}`, 10, y); y += 7;
    doc.text(`Position: ${jobTitle}`, 10, y); y += 7;
    doc.text(`Date: ${date}`, 10, y); y += 10;

    const matchScore = document.getElementById('match-percentage')?.textContent || "N/A";
    const expMatch = document.getElementById('experience-match')?.textContent || "N/A";
    const eduMatch = document.getElementById('education-match')?.textContent || "N/A";

    doc.setFontSize(14);
    doc.setTextColor(60, 60, 60);
    doc.text("Match Overview", 10, y); y += 8;

    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Match Score: ${matchScore}`, 10, y); y += 6;
    doc.text(`${expMatch}`, 10, y); y += 6;
    doc.text(`${eduMatch}`, 10, y); y += 10;

    doc.setFontSize(14);
    doc.setTextColor(60, 60, 60);
    doc.text("Matched Skills", 10, y); y += 8;

    const matchedSkills = [...document.querySelectorAll('#skills-matched-list li')].map(li => li.textContent);
    if (matchedSkills.length === 0) matchedSkills.push("No skills matched.");

    matchedSkills.forEach(skill => {
        const lines = doc.splitTextToSize(`• ${skill}`, 180);
        doc.text(lines, 10, y);
        y += lines.length * 6;
    });

    y += 4;
    doc.setFontSize(14);
    doc.setTextColor(60, 60, 60);
    doc.text("Missing Skills", 10, y); y += 8;

    const missingSkills = [...document.querySelectorAll('#skills-missing-list li')].map(li => li.textContent);
    if (missingSkills.length === 0) missingSkills.push("None");

    missingSkills.forEach(skill => {
        const lines = doc.splitTextToSize(`• ${skill}`, 180);
        doc.text(lines, 10, y);
        y += lines.length * 6;
    });

    y += 4;
    doc.setFontSize(14);
    doc.setTextColor(60, 60, 60);
    doc.text("Recommendations", 10, y); y += 8;

    const recs = [...document.querySelectorAll('#recommendations-list li')].map(li => li.textContent);
    if (recs.length === 0) recs.push("No specific recommendations provided.");

    recs.forEach(rec => {
        const lines = doc.splitTextToSize(`• ${rec}`, 180);
        doc.text(lines, 10, y);
        y += lines.length * 6;
    });

    y += 10;
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Generated by HR-Tech AI on ${new Date().toLocaleString()}`, 10, y);

    doc.save(`resume_screening_${candidateName.replace(/\s/g, '_')}.pdf`);
}

});