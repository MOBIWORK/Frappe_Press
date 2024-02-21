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
			<img
				v-if="this.$i18n.locale == 'vi'"
				src="@/assets/icon_flag_vi.svg"
				alt="Icon Flag"
			/>
			<img v-else src="@/assets/icon_flag_en.svg" alt="Icon Flag" />
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
		}
	},
	data() {
		return {
			langSelected: this.$i18n.locale || 'vi'
		};
	}
};
</script>
