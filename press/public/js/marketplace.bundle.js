import Fuse from 'fuse.js';

const allAppCardNodes = document.getElementsByClassName('app-card');
const searchInput = document.getElementById('app-search-input');
// const noResultsMessage = document.getElementById('no-results-message');

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
// const options = {
// 	keys: ['title'], // Can add description later if required
// 	includeScore: true,
// 	shouldSort: true,
// 	minMatchCharLength: 2,
// };
// const fuse = new Fuse(appList, options);

function changeValueInput(e) {
	const searchText = e.target.value;
	var str_search = window.location.search;
	var arr_search = str_search.split('&');
	var new_str_search = '';

	if (arr_search[0].includes('?')) {
		var check_text_search = 0;
		for (const x in arr_search) {
			if (arr_search[x].includes('text_search=')) {
				var text = arr_search[x].split('=');
				arr_search[x] = text[0] + `=${searchText}`;
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
	// console.log(new_str_search);
	location.href = '/marketplace' + new_str_search;
}
const processChange = debounce((e) => changeValueInput(e));

if (searchInput) {
	searchInput.addEventListener('input', (e) => processChange(e));
}

// searchInput.addEventListener('input', (e) => {
// 	// TODO: Debounce/Throttle
// 	const searchText = e.target.value;
// 	if (!searchText) {
// 		displayAllApps();
// 		return;
// 	}

// 	const results = fuse.search(searchText);
// 	updateAppList(results);
// });

// function updateAppList(results) {
// 	for (let node of allAppCardNodes) {
// 		node.style.display = 'none';
// 	}

// 	if (results.length === 0) {
// 		noResultsMessage.style.display = '';
// 		return;
// 	} else {
// 		noResultsMessage.style.display = 'none';
// 	}

// 	// For sorting according to score
// 	for (let result of results) {
// 		let app = document.getElementById(result.item.name);
// 		app.style.display = '';
// 		document.querySelector('#all-apps-list').appendChild(app);
// 	}
// }

// function displayAllApps() {
// 	noResultsMessage.style.display = 'none';
// 	for (let node of allAppCardNodes) {
// 		node.style.display = '';
// 	}
// }

const btns = document.querySelectorAll('.category-button');

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

const elementApps = document.getElementById('all-apps-list');

function getApps() {
	fetch('/api/method/press.api.marketplace.get_marketplace_apps')
		.then((response) => {
			// Check if the request was successful (status code 200-299)
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}

			// Parse the response body as JSON
			return response.json();
		})
		.then((data) => {
			// Handle the parsed data
			const apps = data.message.data;
			if (apps.length) {
				var html = '';
				var textReiew = '';
				var badge = '';
				var image = '';

				apps.forEach((app) => {
					if (app.ratings_summary.total_num_reviews == 1) {
						textReiew = 'review';
					} else {
						textReiew = 'reviews';
					}

					if (app.subscription_type == 'Freemium') {
						badge = `
							<span
								class="inline-block px-3 py-1 text-sm text-purple-800 rounded-md cursor-default bg-purple-200"
							>
								Freemium
							</span>
						`;
					} else if (app.subscription_type == 'Paid') {
						badge = `
							<span
								class="inline-block px-3 py-1 text-sm text-green-800 rounded-md cursor-default bg-green-200"
							>
								Paid
							</span>
						`;
					} else {
						badge = `
							<span
								class="inline-block px-3 py-1 text-sm text-gray-100 rounded-md cursor-default bg-gray-400"
							>
								Free
							</span>
						`;
					}

					if (app.image) {
						image = `
							<img
								alt="${app.title} Logo"
								src="${app.image}"
								class="image-app rounded-lg"
							/>
						`;
					} else {
						image = `
							<div
								class="flex items-center justify-center text-gray-600 font-bold image-app border border-gray-200 rounded-lg text-title"
							>
								${app.title[0]}
							</div>
						`;
					}

					html += `
					<a
						href="/${app.route}"
						id="${app.name}"
						data-title="${app.title}"
						data-description="${app.description}"
						data-categories="${app.categories}"
						class="app-card flex flex-col border hover:border-blue-300 justify-between p-6 box-shadow-custom cursor-pointer transition focus:outline-none focus:border-blue-500 focus:shadow-outline"
					>
						<div>
							<div class="mb-2">
								${badge}
							</div>
							<div class="flex">
								${image}
							</div>
							<h3 class="mt-3 font-semibold text-gray-800">
								${app.title}
							</h3>
						</div>
						<div class="flex items-center text-base text-gray-700 my-2">
							<div class="flex items-center">
								<img
									class="h-4 opacity-80"
									src="/assets/press/images/icon_star.svg"
								/>
								<span class="ml-1">${app.ratings_summary.avg_rating}</span>
							</div>
							<div class="flex items-center">
								<img
									class="h-4 opacity-80"
									src="/assets/press/images/tally.svg"
								/>
							</div>
							<div class="ml-2 flex items-center">
								${app.ratings_summary.total_num_reviews} ${textReiew}
							</div>
						</div>
						<p class="text-base text-gray-500 line-clamp-2">
							${app.description}
						</p>
					</a>
					`;
				});
				elementApps.innerHTML = html;
				document.getElementById('empty-card').classList.add('hidden');
			} else {
				document.getElementById('empty-card').classList.remove('hidden');
			}
		})
		.catch((error) => {
			// Handle errors that occurred during the fetch
			console.error('Fetch error:', error);
		});
}

// if (elementApps) {
// 	getApps();
// }

// document.addEventListener('DOMContentLoaded', function () {
// 	var breakpointLoad = document.getElementById('breakpoint-load');
// 	var breakpointLoad = breakpointLoad.offsetTop;
// 	window.addEventListener('scroll', function () {
// 		// Lấy vị trí hiện tại của thanh cuộn
// 		var scrollPosition = window.scrollY;
// 		// Kiểm tra nếu vị trí cuộn đã vượt qua phần tử #section-load
// 		if (scrollPosition > breakpointLoad) {
// 			// Thực hiện sự kiện khi cuộn đến #section-load
// 			console.log('Scrolled to #section-load. Do something here.');

// 			// Thêm code xử lý sự kiện của bạn ở đây
// 		}
// 	});
// });
