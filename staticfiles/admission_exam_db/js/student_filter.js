document.getElementById('student-name-filterInput').addEventListener('input', function() {
    const filterValue = this.value.toLowerCase();
    const rows = document.querySelectorAll('.student-table tbody tr')

    rows.forEach(row => {
        const cells = row.getElementsByTagName('td');
        let match = false;

        for (let i = 0; i < cells.length; i++) {
            if (cells[i].textContent.toLowerCase().includes(filterValue)){
                match = true;
                break;
            }
        }

        row.style.display = match ? '' : 'none';

    });
})
