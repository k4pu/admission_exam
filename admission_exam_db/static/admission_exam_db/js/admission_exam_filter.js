function filterExams() {
    const yearFilter = document.getElementById('exam-year-filterInput').value;
    const universityFilter = document.getElementById('university-name-filterInput').value.toLowerCase();

    const rows = document.querySelectorAll('.admission_exam_table tbody tr')

    rows.forEach(row => {
        const yearCell = row.querySelector('td.exam_year');
        const yearText = yearCell ? yearCell.textContent.trim() : '';
        const yearMatches = yearFilter === '' || yearText.indexOf(String(yearFilter)) !== -1;

        const universityText = row.querySelector('td.university').textContent.toLowerCase();
        const universityMatches = universityFilter === '' || universityText.includes(universityFilter);

        row.style.display = (yearMatches && universityMatches) ? '' : 'none';
        
    });
}

document.getElementById('exam-year-filterInput').addEventListener('input', filterExams);
document.getElementById('university-name-filterInput').addEventListener('input', filterExams);
