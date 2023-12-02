import Fuse from 'fuse.js';

const allAppCardNodes = document.getElementsByClassName('app-card');
const searchInput = document.getElementById('app-search-input');
const noResultsMessage = document.getElementById('no-results-message');

function debounce(func, timeout = 800) {
	let timer;
	return (...args) => {
		clearTimeout(timer);
		timer = setTimeout(() => {
			func.apply(this, args);
		}, timeout);
	};
}

const appList = [];
for (let node of allAppCardNodes) {
	appList.push({
		title: node.getAttribute('data-title'),
		description: node.getAttribute('data-description'),
		categories: node.getAttribute('data-categories'),
		name: node.id,
	});
}

// Initialize fuse.js
const options = {
	keys: ['title'], // Can add description later if required
	includeScore: true,
	shouldSort: true,
	minMatchCharLength: 2,
};
const fuse = new Fuse(appList, options);

function saveInput(e) {
	const searchText = e.target.value;
	var str_search = window.location.search;
	var arr_search = str_search.split('&');
	var new_str_search = '';

	if (arr_search[0].includes('?')) {
		var check_text_search = 0;
		for (const x in arr_search) {
			if (arr_search[x].includes('text_search')) {
				arr_search[x] = `text_search=${searchText}`;
				check_text_search += 1;
			}
		}
		if (check_text_search == 0) {
			arr_search[arr_search.length] = `text_search=${searchText}`;
		}

		new_str_search = arr_search.join('&');
	} else {
		new_str_search = `?text_search=${searchText}`;
	}

	location.href = '/marketplace/' + new_str_search;
}
const processChange = debounce((e) => saveInput(e));

searchInput.addEventListener('keyup', (e) => processChange(e));

// searchInput.addEventListener('input', (e) => {
// 	// TODO: Debounce/Throttle
// 	const searchText = e.target.value;
// 	var str_search = window.location.search;
// 	var arr_search = str_search.split('&');
// 	var new_str_search = '';

// 	if (arr_search[0].includes('?')) {
// 		var check_text_search = 0;
// 		for (const x in arr_search) {
// 			if (arr_search[x].includes('text_search')) {
// 				arr_search[x] = `text_search=${searchText}`;
// 				check_text_search += 1;
// 			}
// 		}
// 		if (check_text_search == 0) {
// 			arr_search[arr_search.length] = `text_search=${searchText}`;
// 		}

// 		new_str_search = arr_search.join('&');
// 	} else {
// 		new_str_search = `?text_search=${searchText}`;
// 	}

// 	location.href = '/marketplace/' + new_str_search;

// 	// const searchText = e.target.value;
// 	// if (!searchText) {
// 	// 	displayAllApps();
// 	// 	return;
// 	// }

// 	// const results = fuse.search(searchText);
// 	// updateAppList(results);
// });

function updateAppList(results) {
	for (let node of allAppCardNodes) {
		node.style.display = 'none';
	}

	if (results.length === 0) {
		noResultsMessage.style.display = '';
		return;
	} else {
		noResultsMessage.style.display = 'none';
	}

	// For sorting according to score
	for (let result of results) {
		let app = document.getElementById(result.item.name);
		app.style.display = '';
		document.querySelector('#all-apps-list').appendChild(app);
	}
}

function displayAllApps() {
	noResultsMessage.style.display = 'none';
	for (let node of allAppCardNodes) {
		node.style.display = '';
	}
}

const btns = document.querySelectorAll('.category-button');
console.log(btns);
btns.forEach((btn) => {
	btn.addEventListener('click', (e) => {
		const category = e.target.value;
		window.location.replace(
			location.origin + location.pathname + `?category=${category}`
		);
	});
});

// const removeCategoryBtn = document.getElementById('remove-category');
// removeCategoryBtn.addEventListener('click', (e) => {
// 	removeCategoryBtn.classList.add('hidden');
// 	window.location.replace(location.origin + location.pathname);
// });

function updateCategories(category) {
	let set = 0;
	for (let node of allAppCardNodes) {
		node.style.display = 'none';
	}

	for (let app of allAppCardNodes) {
		if (app.dataset.categories.includes(category)) {
			app.style.display = '';
			set = 1;
		}
	}

	if (set == 0) {
		for (let node of allAppCardNodes) {
			node.style.display = '';
		}
	}

	var button = document.querySelector(`button[value="${category}"]`);
	if (category) {
		if (button) {
			button.classList.add('text-[#212B36]', 'font-[600]');
			// removeCategoryBtn.classList.remove('hidden');
			// removeCategoryBtn.classList.add('flex');
			// document.getElementById('remove-category-name').innerText = category;
		}
	} else {
		if (button) {
			button.classList.add('text-[#212B36]', 'font-[600]');
		}
	}
}

var category = new URLSearchParams(window.location.search).get('category');
if (category != null && category.length > 0) {
	updateCategories(category);
} else if (category == null || category == '') {
	updateCategories('');
}
