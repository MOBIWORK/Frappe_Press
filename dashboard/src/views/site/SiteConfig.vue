<template>
	<ConfigEditor
		v-if="site"
		:title="$t('Site_Config')"
		:subtitle="$t('SiteConfig_content_1')"
		configName="site_config.json"
		:configData="siteConfig"
		:updateConfigMethod="updateSiteConfig"
	/>
</template>

<script>
import ConfigEditor from '@/components/ConfigEditor.vue';

export default {
	name: 'SiteConfig',
	components: {
		ConfigEditor
	},
	props: ['site'],
	data() {
		return {
			editMode: false,
			isDirty: false
		};
	},
	methods: {
		siteConfig() {
			return {
				url: 'press.api.site.site_config',
				params: { name: this.site?.name },
				auto: true,
				initialData: []
			};
		},
		updateSiteConfig(updatedConfig) {
			return {
				url: 'press.api.site.update_config',
				params: {
					name: this.site?.name,
					config: JSON.stringify(updatedConfig)
				}
			};
		}
	}
};
</script>
