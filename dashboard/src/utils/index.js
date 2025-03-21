import i18n from '@/i18n';

export const translate = (key, params) => {
	return i18n.global.t(key, params);
};

export const getLocaleI18n = () => {
	return i18n.global.locale;
};

export const setLocaleI18n = lang => {
	i18n.global.locale = lang;
};
