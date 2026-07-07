// Gọi tự động nếu có phim_id truyền vào từ trang chủ
window.onload = function() {
    if(document.getElementById('phimSelect').value) {
        loadSuatChieu();
    }
};

let allShowtimes = [];

function resetDownstream(step) {
    if (step <= 2) {
        document.getElementById('ngayChieuContainer').style.display = 'none';
        document.getElementById('ngayChieuList').innerHTML = '';
    }
    if (step <= 3) {
        document.getElementById('suatChieuContainer').style.display = 'none';
        document.getElementById('suatChieuList').innerHTML = '';
        document.getElementById('maSuatInput').value = '';
    }
    if (step <= 4) {
        document.getElementById('gheContainer').style.display = 'none';
        document.getElementById('gheList').innerHTML = '';
        document.getElementById('maGheInput').value = '';
        document.getElementById('selectedGheText').innerText = 'Chưa chọn';
    }
}

function loadSuatChieu() {
    const phimId = document.getElementById('phimSelect').value;
    const cumRapContainer = document.getElementById('cumRapContainer');
    const cumRapList = document.getElementById('cumRapList');
    
    resetDownstream(2);
    cumRapContainer.style.display = 'none';
    
    if (!phimId) return;

    fetch(`/datve/api/suatchieu/${phimId}`)
        .then(res => res.json())
        .then(data => {
            allShowtimes = data;
            cumRapList.innerHTML = '';
            
            if (data.length === 0) {
                cumRapList.innerHTML = '<p class="inline-style-89">Hiện không có suất chiếu nào cho phim này.</p>';
                cumRapContainer.style.display = 'block';
                return;
            }
            
            const cinemas = {};
            data.forEach(sc => {
                if (!cinemas[sc.MaCumRap]) {
                    cinemas[sc.MaCumRap] = sc.TenCumRap;
                }
            });
            
            Object.keys(cinemas).forEach(maCumRap => {
                const btn = document.createElement('div');
                btn.style = `padding: 0.8rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; text-align: center; background: var(--bg-card); transition: all 0.2s; display: flex; align-items: center; justify-content: center; min-height: 60px;`;
                btn.innerHTML = `<strong style="color:var(--primary); font-size:1.1rem;">${cinemas[maCumRap]}</strong>`;
                
                btn.onclick = function() {
                    Array.from(cumRapList.children).forEach(c => {
                        c.style.borderColor = 'var(--border-color)';
                        c.style.background = 'var(--bg-card)';
                    });
                    btn.style.borderColor = 'var(--primary)';
                    btn.style.background = 'rgba(139, 92, 246, 0.1)';
                    renderNgayChieu(maCumRap);
                };
                cumRapList.appendChild(btn);
            });
            cumRapContainer.style.display = 'block';
        });
}

function renderNgayChieu(maCumRap) {
    resetDownstream(3);
    const container = document.getElementById('ngayChieuContainer');
    const list = document.getElementById('ngayChieuList');
    list.innerHTML = '';
    
    const dates = {};
    allShowtimes.filter(sc => sc.MaCumRap == maCumRap).forEach(sc => {
        const dateStr = sc.GioBatDau.split(' ')[0];
        if (!dates[dateStr]) dates[dateStr] = true;
    });
    
    Object.keys(dates).sort().forEach(dateStr => {
        const btn = document.createElement('div');
        btn.style = `padding: 0.8rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; text-align: center; background: var(--bg-card); transition: all 0.2s;`;
        
        const d = new Date(dateStr);
        const formatted = ("0" + d.getDate()).slice(-2) + '/' + ("0" + (d.getMonth() + 1)).slice(-2) + '/' + d.getFullYear();

        btn.innerHTML = `<strong style="font-size:1.1rem;">${formatted}</strong>`;
        
        btn.onclick = function() {
            Array.from(list.children).forEach(c => {
                c.style.borderColor = 'var(--border-color)';
                c.style.background = 'var(--bg-card)';
            });
            btn.style.borderColor = 'var(--primary)';
            btn.style.background = 'rgba(139, 92, 246, 0.1)';
            renderGioChieu(maCumRap, dateStr);
        };
        list.appendChild(btn);
    });
    container.style.display = 'block';
}

function renderGioChieu(maCumRap, dateStr) {
    resetDownstream(4);
    const container = document.getElementById('suatChieuContainer');
    const list = document.getElementById('suatChieuList');
    list.innerHTML = '';
    
    const times = allShowtimes.filter(sc => sc.MaCumRap == maCumRap && sc.GioBatDau.startsWith(dateStr));
    
    times.forEach(sc => {
        const timeStr = sc.GioBatDau.split(' ')[1];
        const btn = document.createElement('div');
        btn.style = `padding: 0.8rem 1rem; border: 1px solid var(--border-color); border-radius: 8px; cursor: pointer; text-align: center; background: var(--bg-card); transition: all 0.2s;`;
        btn.innerHTML = `<strong style="display:block; font-size:1.2rem; color:var(--primary); margin-bottom:5px;">${timeStr}</strong><span style="font-size:0.85rem; color:var(--text-muted); background:rgba(255,255,255,0.05); padding:3px 8px; border-radius:4px;">${sc.TenLoaiPhong}</span>`;
        
        btn.onclick = function() {
            Array.from(list.children).forEach(c => {
                c.style.borderColor = 'var(--border-color)';
                c.style.background = 'var(--bg-card)';
            });
            btn.style.borderColor = 'var(--primary)';
            btn.style.background = 'rgba(139, 92, 246, 0.1)';
            
            document.getElementById('maSuatInput').value = sc.MaSuatChieu;
            loadGhe(sc.MaSuatChieu);
        };
        list.appendChild(btn);
    });
    container.style.display = 'block';
}

let seatPrice = 0;
let fnbPrice = 0;
let allFnbItems = [];

function updateTotalPrice() {
    const formatter = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' });
    document.getElementById('selectedFnbText').innerText = formatter.format(fnbPrice);
    document.getElementById('totalPriceText').innerText = formatter.format(seatPrice + fnbPrice);
}

function loadFnb() {
    const fnbList = document.getElementById('fnbList');
    
    // If already loaded, just reset prices and return
    if (allFnbItems.length > 0) {
        // Only reset if they go back and choose a different seat maybe?
        // Let's not reset if they just navigate back and forth
        document.getElementById('step_booking').style.display = 'none';
        document.getElementById('step_fnb').style.display = 'block';
        document.getElementById('step_checkout').style.display = 'none';
        return;
    }

    fetch('/datve/api/dichvu')
        .then(res => res.json())
        .then(data => {
            allFnbItems = data;
            fnbList.innerHTML = '';
            
            data.forEach(item => {
                const card = document.createElement('div');
                card.style = `background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 15px; text-align: center; display: flex; flex-direction: column; justify-content: space-between;`;
                
                const formatter = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' });
                const priceStr = formatter.format(item.GiaBan);
                
                card.innerHTML = `
                    <div>
                        <h4 style="margin-bottom: 5px; color: #f8fafc;">${item.TenDichVu}</h4>
                        <p style="color: #f59e0b; font-weight: bold; margin-bottom: 15px;">${priceStr}</p>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                        <button type="button" class="btn-minus" style="width: 30px; height: 30px; border-radius: 50%; border: none; background: rgba(255,255,255,0.1); color: white; cursor: pointer;">-</button>
                        <input type="text" name="dv_${item.MaDichVu}" value="0" readonly class="fnb-input" style="width: 40px; text-align: center; background: transparent; border: none; color: white; font-weight: bold; font-size: 1.1rem;">
                        <button type="button" class="btn-plus" style="width: 30px; height: 30px; border-radius: 50%; border: none; background: var(--primary); color: white; cursor: pointer;">+</button>
                    </div>
                `;
                
                const input = card.querySelector('.fnb-input');
                const btnMinus = card.querySelector('.btn-minus');
                const btnPlus = card.querySelector('.btn-plus');
                
                btnMinus.onclick = () => {
                    let val = parseInt(input.value) || 0;
                    if (val > 0) {
                        input.value = val - 1;
                        fnbPrice -= parseFloat(item.GiaBan);
                        updateTotalPrice();
                    }
                };
                
                btnPlus.onclick = () => {
                    let val = parseInt(input.value) || 0;
                    if (val < 10) {
                        input.value = val + 1;
                        fnbPrice += parseFloat(item.GiaBan);
                        updateTotalPrice();
                    }
                };
                
                fnbList.appendChild(card);
            });
            
            document.getElementById('step_booking').style.display = 'none';
            document.getElementById('step_fnb').style.display = 'block';
            document.getElementById('step_checkout').style.display = 'none';
        });
}

document.getElementById('btnNextToFnb').onclick = () => {
    loadFnb();
};

document.getElementById('btnBackToBooking').onclick = () => {
    document.getElementById('step_fnb').style.display = 'none';
    document.getElementById('step_booking').style.display = 'block';
};

document.getElementById('btnSkipFnb').onclick = () => {
    document.getElementById('step_fnb').style.display = 'none';
    document.getElementById('step_checkout').style.display = 'block';
    if(document.getElementById('checkoutContainer')) {
        document.getElementById('checkoutContainer').style.display = 'block';
    }
};

document.getElementById('btnNextToCheckout').onclick = () => {
    document.getElementById('step_fnb').style.display = 'none';
    document.getElementById('step_checkout').style.display = 'block';
    if(document.getElementById('checkoutContainer')) {
        document.getElementById('checkoutContainer').style.display = 'block';
    }
};

document.getElementById('btnBackToFnb').onclick = () => {
    document.getElementById('step_checkout').style.display = 'none';
    document.getElementById('step_fnb').style.display = 'block';
};

function loadGhe(suatChieuId) {
    const container = document.getElementById('gheContainer');
    const list = document.getElementById('gheList');
    document.getElementById('maGheInput').value = '';
    document.getElementById('selectedGheText').innerText = 'Chưa chọn';
    document.getElementById('btnNextToFnb').style.display = 'none';
    seatPrice = 0;
    fnbPrice = 0;
    updateTotalPrice();

    fetch(`/datve/api/ghe/${suatChieuId}`)
        .then(res => res.json())
        .then(data => {
            const danh_sach_ghe = data.ghe;
            const so_cot = data.so_cot;
            
            list.style.gridTemplateColumns = `repeat(${so_cot}, 1fr)`;
            list.innerHTML = '';
            
            danh_sach_ghe.forEach(ghe => {
                const btn = document.createElement('div');
                btn.innerText = ghe.TenGhe;
                btn.style = `padding: 0.5rem; text-align: center; border-radius: 4px; cursor: pointer; font-weight: bold; border: 1px solid var(--border-color); transition: all 0.2s;`;
                
                // Xử lý giữ đúng vị trí tọa độ thật của ghế trên bản đồ
                const match = ghe.TenGhe.match(/^([A-Z]+)(\d+)$/);
                if (match) {
                    const rowStr = match[1];
                    const colNum = parseInt(match[2]);
                    
                    let rowNum = 0;
                    for (let i = 0; i < rowStr.length; i++) {
                        rowNum = rowNum * 26 + (rowStr.charCodeAt(i) - 64);
                    }
                    
                    btn.style.gridRow = rowNum;
                    btn.style.gridColumn = colNum;
                }

                if (ghe.DaBan === 1) {
                    btn.style.background = '#ef4444';
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                    btn.title = "Ghế đã được bán";
                } else {
                    // Chọn màu nền và viền tùy theo loại ghế
                    let defaultBg = 'rgba(255,255,255,0.05)';
                    let defaultBorder = 'rgba(255,255,255,0.2)';
                    
                    if (ghe.TenLoai === 'VIP') {
                        defaultBg = 'rgba(245, 158, 11, 0.15)';
                        defaultBorder = '#f59e0b';
                        btn.style.color = '#f59e0b';
                    } else if (ghe.TenLoai === 'Couple') {
                        defaultBg = 'rgba(236, 72, 153, 0.15)';
                        defaultBorder = '#ec4899';
                        btn.style.color = '#ec4899';
                    }
                    
                    btn.style.background = defaultBg;
                    btn.style.borderColor = defaultBorder;
                    btn.dataset.defaultBg = defaultBg;
                    btn.dataset.defaultBorder = defaultBorder;
                    
                    btn.onclick = function() {
                        // Reset all other available seats to their original color
                        Array.from(list.children).forEach(c => {
                            if(c.style.background !== 'rgb(239, 68, 68)' && c.dataset.defaultBg) { // not sold
                                c.style.background = c.dataset.defaultBg;
                                c.style.borderColor = c.dataset.defaultBorder;
                            }
                        });
                        
                        // Highlight the selected seat
                        btn.style.background = '#10b981';
                        btn.style.borderColor = '#10b981';
                        btn.style.color = '#fff';
                        
                        document.getElementById('maGheInput').value = ghe.MaGhe;
                        document.getElementById('selectedGheText').innerText = ghe.TenGhe + ` (${ghe.TenLoai})`;
                        
                        seatPrice = ghe.Gia;
                        updateTotalPrice();
                        
                        document.getElementById('btnNextToFnb').style.display = 'inline-block';
                    };
                }
                list.appendChild(btn);
            });
            container.style.display = 'block';
        });
}

// Cảnh báo khi người dùng vô tình bấm F5 (Reload) hoặc đóng trang
let isSubmitting = false;
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
    bookingForm.addEventListener('submit', () => {
        isSubmitting = true;
    });
}

window.addEventListener('beforeunload', function (e) {
    // Nếu chưa bấm thanh toán mà đã có chọn ghế/dữ liệu thì cảnh báo
    const selectedGhe = document.getElementById('maGheInput') ? document.getElementById('maGheInput').value : '';
    if (!isSubmitting && selectedGhe !== '') {
        e.preventDefault();
        e.returnValue = ''; // Standard cho trình duyệt hiển thị popup cảnh báo
    }
});
