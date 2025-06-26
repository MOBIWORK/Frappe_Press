<template>
	<div class="flex flex-1 flex-col overflow-y-auto px-4 pt-3">

		<div class="max-w-xs mx-auto min-w-40">
			<Autocomplete
				:options="optionsLanguage"
				v-model="single"
				placeholder="Select language"
				:hideSearch="true"
			>
				<template #prefix>
					<img :src="single.image" class="mr-2 h-4.5 w-7" />
				</template>
				<template #item-prefix="{ option }">
					<img :src="option.image.toString()" class="mr-2 h-4.5 w-7" />
				</template>
			</Autocomplete>
		</div>
	</div>
</template>
<script setup>
import {
	defaultLanguage,
	fetchLanguage,
	changeLanguage,
} from '../composables/language.js';
import { Autocomplete } from 'frappe-ui';
import { ref, watch, onMounted } from 'vue';
import { session } from '../data/session';

const optionsLanguage = ref([
	{
		label: __('Vietnamese'),
		value: 'vi',
		image: '/assets/press/images/icon_flag_vi.svg',
	},
	{
		label: __('English'),
		value: 'en',
		image: '/assets/press/images/icon_flag_en.svg',
	},
]);
const single = ref();

onMounted(() => {
	let lang = localStorage.getItem('lang');
	if (session.user && !lang) {
		fetchLanguage.fetch();
	}
});

const setDefaultLanguage = (lang) => {
	localStorage.setItem('lang', lang);
	defaultLanguage.value = lang;
};

watch(
	defaultLanguage,
	(val) => {
		single.value = optionsLanguage.value.find((item) => item.value === val);
	},
	{
		immediate: true,
	}
);

watch(single, (val) => {
	if (val.value === defaultLanguage.value) return;

	setDefaultLanguage(val.value);
	if (session.user) {
		changeLanguage.submit(
			{ lang: val.value },
			{
				onSuccess: () => {
					window.location.reload();
				},
			}
		);
	} else {
		window.location.reload();
	}
});
</script>
