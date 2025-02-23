function filterStudents() {
    const classFilter = document.getElementById('homeroom-class-filterInput').value.toLowerCase();
    const numberFilter = document.getElementById('attendance-number-filterInput').value;
    const nameFilter = document.getElementById('student-name-filterInput').value.toLowerCase();
    const graduationFilter = document.getElementById('graduation-year-filterInput').value;

    const rows = document.querySelectorAll('.student-table tbody tr')

    rows.forEach(row => {
        const classCell = row.querySelector('td.homeroom_class');
        const classText = classCell ? classCell.textContent.toLowerCase() : ''
        const classMatches = classFilter === '' || classText.includes(classFilter);

        const numberCell = row.querySelector('td.attendance_number');
        const numberText = numberCell ? numberCell.textContent.trim() : ''
        const numberMatches = numberFilter === '' || numberText.indexOf(String(numberFilter)) !== -1;

        const nameText = row.querySelector('td.student_name').textContent.toLowerCase();
        const nameMatches = nameFilter === '' || nameText.includes(nameFilter) === true;

        const graduationCell = row.querySelector('td.graduation_year');
        const graduationText = graduationCell ? graduationCell.textContent.trim() : '';
        const graduationMatches = graduationFilter === '' || graduationText.indexOf(String(graduationFilter)) !== -1;

        row.style.display = (graduationMatches && classMatches && numberMatches && nameMatches) ? '' : 'none';
    });
}


document.getElementById('graduation-year-filterInput').addEventListener('input', filterStudents);
document.getElementById('homeroom-class-filterInput').addEventListener('input', filterStudents);
document.getElementById('attendance-number-filterInput').addEventListener('input', filterStudents);
document.getElementById('student-name-filterInput').addEventListener('input', filterStudents);
