<template>
	<FormControl
		type="select"
		:options="[
			{
				label: this.$t('vietnameses'),
				value: 'vi'
			},
			{
				label: this.$t('english'),
				value: 'en'
			}
		]"
		size="md"
		variant="outline"
		placeholder="Placeholder"
		label=""
		v-model="langSelected"
	>
		<template #prefix>
			<img :src="flagSelected" alt="Icon Flag" />
		</template>
	</FormControl>
</template>

<script>
export default {
	name: 'SelectLanguage',
	watch: {
		langSelected(value) {
			localStorage.setItem('lang', value);
			this.$i18n.locale = value;
			this.getFlag();
		},
		flagSelected(val, old) {
			// setTimeout(() => {
			// 	if (old != null) {
			// 		location.reload();
			// 	}
			// }, 1);
		}
	},
	data() {
		return {
			langSelected: this.$i18n.locale || 'vi',
			flagSelected: null
		};
	},
	mounted() {
		this.getFlag();
	},
	methods: {
		getFlag() {
			let flagOptions = {
				vi: '/src/assets/icon_flag_vi.svg',
				en: '/src/assets/icon_flag_en.svg'
			};
			this.flagSelected = flagOptions[this.langSelected];
		}
	}
};
</script>
