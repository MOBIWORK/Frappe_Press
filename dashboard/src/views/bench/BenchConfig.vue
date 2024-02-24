<template>
	<ConfigEditor
		v-if="bench && !bench?.public"
		:title="$t('Common_Site_Config')"
		:subtitle="$t('BenchConfig_content_1')"
		:configData="benchConfig"
		:updateConfigMethod="updateBenchConfigMethod"
	/>
</template>

<script>
import ConfigEditor from '@/components/ConfigEditor.vue';

export default {
	name: 'BenchConfig',
	components: {
		ConfigEditor
	},
	props: ['bench'],
	data() {
		return {
			editMode: false,
			isCommonSiteConfigFormDirty: false,
			isBenchConfigFormDirty: false
		};
	},
	methods: {
		benchConfig() {
			return {
				url: 'press.api.bench.bench_config',
				params: {
					name: this.bench?.name
				},
				auto: true,
				initialData: []
			};
		},
		updateBenchConfigMethod(updatedConfig) {
			return {
				url: 'press.api.bench.update_config',
				params: {
					name: this.bench?.name,
					config: JSON.stringify(updatedConfig)
				}
			};
		}
	}
};
</script>
