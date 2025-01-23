// autocomplete.js
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('university-faculty-autocomplete');
    const resultsDiv = document.getElementById('autocomplete-results');

    input.addEventListener('input', async () => {
        const query = input.value;
        if (query.length > 1) {
            const response = await fetch(`/admission_exam_db/api/university_faculty?q=${encodeURIComponent(query)}`);
            const results = await response.json();

            resultsDiv.innerHTML = ''; // 結果をクリア
            results.forEach(item => {
                const div = document.createElement('div');
                div.textContent = item.name;
                div.classList.add('autocomplete-item');
                div.addEventListener('click', () => {
                    input.value = item.id; // 選択した候補をフィールドに設定
                    resultsDiv.innerHTML = ''; // 候補をクリア
                });
                resultsDiv.appendChild(div);
            });
        } else {
            resultsDiv.innerHTML = ''; // クエリが短すぎる場合は候補をクリア
        }
    });

    // フォーカスが外れた場合に候補を非表示にする
    input.addEventListener('blur', () => {
        setTimeout(() => {
            resultsDiv.innerHTML = '';
        }, 100);
    });

    // 候補がクリックされた場合に blur を優先させない
    resultsDiv.addEventListener('mousedown', (event) => {
    event.preventDefault();
});
});
