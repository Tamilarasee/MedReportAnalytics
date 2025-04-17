document.addEventListener('DOMContentLoaded', function() {
    // Function to highlight medical terms in text
    function highlightMedicalTerms() {
        const reportTextElements = document.querySelectorAll('.report-text');
        const medicalTerms = Array.from(document.querySelectorAll('.medical-term-item')).map(el => el.textContent.trim());
        
        if (medicalTerms.length === 0 || reportTextElements.length === 0) {
            return;
        }
        
        reportTextElements.forEach(element => {
            let html = element.innerHTML;
            
            // Sort terms by length (longest first) to avoid partial replacements
            medicalTerms.sort((a, b) => b.length - a.length);
            
            medicalTerms.forEach(term => {
                // Create a regex that matches the term with word boundaries
                const regex = new RegExp(`\\b${term}\\b`, 'gi');
                
                // Replace the term with a highlighted version
                html = html.replace(regex, `<span class="medical-term">$&</span>`);
            });
            
            element.innerHTML = html;
        });
    }
    
    // Call the highlight function if we're on a results page
    if (document.querySelector('.medical-term-item')) {
        highlightMedicalTerms();
    }
    
    // Enable all tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Handle file upload validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.value;
            
            if (fileName) {
                const fileExtension = fileName.split('.').pop().toLowerCase();
                if (fileExtension !== 'pdf') {
                    alert('Please select a PDF file.');
                    this.value = '';
                }
            }
        });
    }
    
    // Add animation for card hover effect
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'transform 0.3s ease';
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});
