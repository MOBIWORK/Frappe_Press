// Lấy tham chiếu đến dropdown và các item
const languageItems = document.querySelectorAll('#languageMenu .dropdown-item');
const languageButton = document.getElementById('languageDropdown');

// Xác định ngôn ngữ từ URL
const params = new URLSearchParams(window.location.search);
const currentLang = params.get('lang') || 'vi';

// Cập nhật nút hiển thị ngôn ngữ hiện tại
const updateLanguageButton = (langCode) => {
	const selectedItem = [...languageItems].find(
		(item) => item.getAttribute('data-lang') === langCode
	);
	if (selectedItem) {
		languageButton.innerHTML = `${selectedItem.innerHTML}`;
	}
};

// Cập nhật ngay từ đầu
updateLanguageButton(currentLang);

// Xử lý sự kiện chọn ngôn ngữ
languageItems.forEach((item) => {
	item.addEventListener('click', (e) => {
		e.preventDefault(); // Ngăn reload trang
		const selectedLang = item.getAttribute('data-lang');

		if (selectedLang != currentLang) {
			// Cập nhật URL mà không reload
			const newUrl = `${window.location.pathname}?lang=${selectedLang}`;
			window.location.href = newUrl;
		}
	});
});
