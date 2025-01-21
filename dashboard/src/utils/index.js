import i18n from '@/i18n';

export const translate = (key, params) => {
	return i18n.global.t(key, params);
};
