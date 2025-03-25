<template>
	<div class="min-w-[162px]">
		<Autocomplete
			:options="optionsLanguage"
			v-model="langSelected"
			placeholder="Select language"
			:hideSearch="true"
		>
			<template #prefix>
				<img :src="langSelected?.image" class="mr-2 h-4.5 w-7" />
			</template>
			<template #item-prefix="{ option }">
				<img :src="option.image.toString()" class="mr-2 h-4.5 w-7" />
			</template>
		</Autocomplete>
	</div>
</template>

<script setup>
import Autocomplete from '../frappe-ui/Autocomplete.vue';
import { watch, ref, onMounted } from 'vue';
import { translate, setLocaleI18n } from '@/utils/index';
import {
	defaultLanguage,
	fetchLanguage,
	changeLanguage
} from '@/composables/language';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const langSelected = ref();
const optionsLanguage = [
	{
		label: translate('Vietnamese'),
		value: 'vi',
		image: '/assets/press/images/icon_flag_vi.svg'
	},
	{
		label: translate('English'),
		value: 'en',
		image: '/assets/press/images/icon_flag_en.svg'
	}
];

onMounted(() => {
	let currentTeam = localStorage.getItem('current_team');
	if (currentTeam) {
		fetchLanguage.fetch();
	} else {
		let lang = getLanguageParams();
		if (['vi', 'en'].includes(lang)) {
			setDefaultLanguage(lang);
		}
	}
});

watch(
	defaultLanguage,
	val => {
		if (val) {
			langSelected.value = optionsLanguage.find(item => item.value === val);
		}
	},
	{
		immediate: true
	}
);

watch(langSelected, val => {
	setDefaultLanguage(val.value);
	let currentTeam = localStorage.getItem('current_team');
	if (currentTeam) {
		changeLanguage.submit({ lang: val.value });
	}
});

function getLanguageParams() {
	return route.query.lang;
}

function setLanguageParams(lang) {
	let language = route.query.lang;
	if (language && lang != language) {
		router.replace({
			path: route.path,
			query: { ...route.query, lang }
		});
	}
}

function setDefaultLanguage(lang) {
	localStorage.setItem('lang', lang);
	defaultLanguage.value = lang;
	setLocaleI18n(lang);
	setLanguageParams(lang);
}
</script>
