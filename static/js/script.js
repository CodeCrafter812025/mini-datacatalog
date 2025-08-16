document.addEventListener('DOMContentLoaded', function() {
    // آپلود فایل CSV
    const uploadForm = document.getElementById('uploadForm');
    const uploadMessage = document.getElementById('uploadMessage');
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('csvFile');
        formData.append('file', fileInput.files[0]);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                uploadMessage.innerHTML = 
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        <i class="bi bi-check-circle-fill"></i> 
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                ;
                loadETLs(); // به‌روزرسانی لیست
            } else {
                uploadMessage.innerHTML = 
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="bi bi-exclamation-triangle-fill"></i> خطا: 
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                ;
            }
        } catch (error) {
            uploadMessage.innerHTML = 
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                    <i class="bi bi-exclamation-triangle-fill"></i> خطا در ارتباط با سرور
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            ;
        }
    });
    
    // بارگذاری لیست ETLها
    async function loadETLs() {
        try {
            const response = await fetch('/etls');
            const etls = await response.json();
            
            const etlList = document.getElementById('etlList');
            etlList.innerHTML = '';
            
            if (Object.keys(etls).length === 0) {
                etlList.innerHTML = 
                    <div class="col-12 text-center py-4">
                        <div class="alert alert-warning">
                            <i class="bi bi-info-circle-fill"></i> هیچ ETLی یافت نشد
                        </div>
                    </div>
                ;
                return;
            }
            
            Object.entries(etls).forEach(([etlName, tables]) => {
                const col = document.createElement('div');
                col.className = 'col-md-6 col-lg-4 mb-3';
                
                const tablesBadges = tables.map(table => 
                    <span class="table-badge"></span>
                ).join('');
                
                col.innerHTML = 
                    <div class="card etl-card h-100">
                        <div class="card-body">
                            <div class="etl-name">
                                <i class="bi bi-gear-fill"></i> 
                            </div>
                            <div class="tables-list">
                                <strong>جداول:</strong><br>
                                
                            </div>
                        </div>
                    </div>
                ;
                
                etlList.appendChild(col);
            });
        } catch (error) {
            const etlList = document.getElementById('etlList');
            etlList.innerHTML = 
                <div class="col-12 text-center py-4">
                    <div class="alert alert-danger">
                        <i class="bi bi-exclamation-triangle-fill"></i> خطا در دریافت اطلاعات
                    </div>
                </div>
            ;
        }
    }
    
    // رویداد دکمه به‌روزرسانی
    document.getElementById('refreshBtn').addEventListener('click', loadETLs);
    
    // بارگذاری اولیه
    loadETLs();
});
