import { ref } from 'vue';
import { createResource } from 'frappe-ui';

export const defaultLanguage = ref(localStorage.getItem('lang') || 'vi');
export const showLoading = ref(false);

export const fetchLanguage = createResource({
	url: 'press.api.language.get_language',
	cache: 'Language',
	onSuccess: data => {
		defaultLanguage.value = data;
	}
});

export const changeLanguage = createResource({
	url: 'press.api.language.change_language',
	onError(err) {
		console.log(err);
	}
});

export const showLanguage = ref(false);

export const setShowLanguage = (value) => {
	showLanguage.value = value;
}