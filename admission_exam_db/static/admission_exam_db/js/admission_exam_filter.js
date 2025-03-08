function filterExams() {
    const yearFilter = document.getElementById('exam-year-filterInput').value;
    const universityFilter = document.getElementById('university-name-filterInput').value.toLowerCase();
    const facultyFilter = document.getElementById('faculty-name-filterInput').value.toLowerCase();
    const studentNameFilter = document.getElementById('student-name-filterInput').value.toLowerCase();
    const selectedResults = new Set()
    const checkboxes = document.querySelectorAll('input.result-filterChoice:checked')
    checkboxes.forEach(checkbox => {
        selectedResults.add(checkbox.value);
    })

    const rows = document.querySelectorAll('.admission_exam_table tbody tr')

    rows.forEach(row => {
        const yearCell = row.querySelector('td.exam_year');
        const yearText = yearCell ? yearCell.textContent.trim() : '';
        const yearMatches = yearFilter === '' || yearText.indexOf(String(yearFilter)) !== -1;

        const universityText = row.querySelector('td.university').textContent.toLowerCase();
        const universityMatches = universityFilter === '' || universityText.includes(universityFilter);

        const facultyText = row.querySelector('td.faculty').textContent.toLowerCase();
        const facultyMatches = facultyFilter === '' || facultyText.includes(facultyFilter);

        const studentNameText = row.querySelector('td.student_name').textContent.toLowerCase();
        const studentNameMatches = studentNameFilter === '' || studentNameText.includes(studentNameFilter);

        const resultText = row.querySelector('td.result').textContent;
        const resultMatches = selectedResults.has(resultText);

        row.style.display = (yearMatches && universityMatches && facultyMatches && studentNameMatches && resultMatches) ? '' : 'none';
        
    });
}

document.getElementById('exam-year-filterInput').addEventListener('input', filterExams);
document.getElementById('university-name-filterInput').addEventListener('input', filterExams);
document.getElementById('faculty-name-filterInput').addEventListener('input', filterExams);
document.getElementById('student-name-filterInput').addEventListener('input', filterExams);

// モーダル部分
//要素を取得
const modal = document.querySelector('.js-modal'),
      open = document.querySelector('.js-modal-open'),
      close = document.querySelector('.js-modal-close');

//「開くボタン」をクリックしてモーダルを開く
function modalOpen() {
  modal.classList.add('is-active');
}
open.addEventListener('click', modalOpen);

//「閉じるボタン」をクリックしてモーダルを閉じる
function modalClose() {
  modal.classList.remove('is-active');
}
close.addEventListener('click', modalClose);

//「モーダルの外側」をクリックしてモーダルを閉じる
function modalOut(e) {
  if (e.target == modal) {
    modal.classList.remove('is-active');
  }
}

addEventListener('click', modalOut);

// 複数チェックの実装
const passedCheckAllBox = document.getElementById('passed-choice')
const passedCheckboxes = document.querySelectorAll('.passed-filterChoice');

const rejectedCheckAllBox = document.getElementById('rejected-choice')
const rejectedCheckboxes = document.querySelectorAll('.rejected-filterChoice');

const yetCheckAllBox = document.getElementById('yet-choice')
const yetCheckboxes = document.querySelectorAll('.yet-filterChoice');

function checkAll(checkAllBox, checkboxes) {
    checkboxes.forEach(checkbox => {
        checkbox.checked = checkAllBox.checked;
        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
    });
}

// 各「全選択」チェックボックスにイベントリスナーを追加
passedCheckAllBox.addEventListener('change', () => checkAll(passedCheckAllBox, passedCheckboxes));
rejectedCheckAllBox.addEventListener('change', () => checkAll(rejectedCheckAllBox, rejectedCheckboxes));
yetCheckAllBox.addEventListener('change', () => checkAll(yetCheckAllBox, yetCheckboxes));

// 一つ一つのチェックボックスをクリックしたときの全選択チェックボックスの処理
function checkAllBoxCheckEventListenerAdd(checkAllBox, checkboxes) {
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            // 一つでもチェックが外れたとき
            if (!checkbox.checked) {
                checkAllBox.checked = false;
                return; //不要な処理をしない
            }
            // 一つ一つ全てチェックされたとき
            if (Array.from(checkboxes).every(cb => cb.checked)) {
                checkAllBox.checked = true;
            }
        })
    });
}
// EventListenerの追加
checkAllBoxCheckEventListenerAdd(passedCheckAllBox, passedCheckboxes)
checkAllBoxCheckEventListenerAdd(rejectedCheckAllBox, rejectedCheckboxes)
checkAllBoxCheckEventListenerAdd(yetCheckAllBox, yetCheckboxes)

const filterChoices = document.getElementsByClassName('result-filterChoice');
Array.from(filterChoices).forEach(choice => {
    choice.addEventListener('change', filterExams);
})

