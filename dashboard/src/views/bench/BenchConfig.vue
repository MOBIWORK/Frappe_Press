<template>
	<ConfigEditor
		v-if="bench && !bench?.public"
		title="Cấu hình trang web chung"
		subtitle="Thêm và cập nhật các cặp giá trị khóa cho tệp common_site_config.json và bench_config.json của bench của bạn."
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
