<template>
	<Dialog
		:options="{ title: $t('change_language'), size: 'lg', position: 'top' }"
	>
		<template v-slot:body-content>
			<SelectLanguage></SelectLanguage>
		</template>
	</Dialog>
</template>

<script>
import SelectLanguage from './global/SelectLanguage.vue';
export default {
	name: 'SwitchLangDialog',
	components: {
		SelectLanguage
	}
};
</script>
