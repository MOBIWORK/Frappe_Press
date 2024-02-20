import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import vi from './locales/vi.json';

function loadLocaleMessages() {
	const locales = [{ en: en }, { vi: vi }];
	const messages = {};
	locales.forEach(lang => {
		const key = Object.keys(lang);
		messages[key] = lang[key];
	});
	return messages;
}

function loadLocale() {
	return localStorage.getItem('lang') || 'vi';
}

export default createI18n({
	locale: loadLocale(),
	fallbackLocale: 'vi',
	messages: loadLocaleMessages()
});
