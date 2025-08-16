// آپلود فایل CSV
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', e.target.file.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(result.message || 'فایل با موفقیت آپلود شد!');
        loadETLs(); // به‌روزرسانی لیست
    } catch (error) {
        alert('خطا در آپلود فایل: ' + error.message);
    }
});

// بارگذاری لیست ETLها
async function loadETLs() {
    try {
        const response = await fetch('/etls');
        const etls = await response.json();
        
        const etlList = document.getElementById('etlList');
        etlList.innerHTML = '';
        
        Object.entries(etls).forEach(([etlName, tables]) => {
            const item = document.createElement('div');
            item.className = 'etl-item';
            item.innerHTML = 
                <div class="etl-name"></div>
                <div class="tables-list">جداول: </div>
            ;
            etlList.appendChild(item);
        });
    } catch (error) {
        alert('خطا در دریافت اطلاعات: ' + error.message);
    }
}

// رویداد دکمه به‌روزرسانی
document.getElementById('refreshBtn').addEventListener('click', loadETLs);

// بارگذاری اولیه
loadETLs();
