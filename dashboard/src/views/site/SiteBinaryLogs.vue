<template>
	<div
		class="flex items-center justify-center"
		v-if="$resources.getPlan?.loading"
	>
		<LoadingText />
	</div>
	<div v-else-if="$resources.getPlan?.data?.monitor_access">
		<Card>
			<Report
				:filters="filters"
				:columns="colTable"
				:data="formatData"
				:title="$t('mariadb_binary_log_report')"
			/>
			<div
				class="px-2 py-2 text-base text-gray-600"
				v-if="$resources.binaryLogs.loading"
			>
				<LoadingText />
			</div>
			<div
				class="py-2 text-base text-gray-600"
				v-else-if="$resources.binaryLogs.data.length == 0"
			>
				{{ $t('no_data') }}
			</div>
			<Button
				v-if="$resources.binaryLogs.data && $resources.binaryLogs.data.length"
				:loading="$resources.binaryLogs.loading"
				:loadingText="`${$t('loading')}...`"
				@click="max_lines += 10"
			>
				{{ $t('load_more') }}
			</Button>
		</Card>
	</div>
	<div class="flex justify-center" v-else>
		<span class="mt-16 text-base text-gray-700">
			{{ $t('SiteBinaryLogs_content_1') }}
		</span>
	</div>
</template>

<script>
import Report from '@/components/Report.vue';

export default {
	name: 'SiteBinaryLogs',
	props: ['site'],
	components: { Report },
	data() {
		return {
			colTable: [
				{ label: this.$t('Timestamp'), name: 'timestamp', class: 'w-3/12' },
				{ label: this.$t('Query'), name: 'query', class: 'w-9/12' }
			],
			filters: [
				{
					name: 'pattern',
					label: `${this.$t('search')}:`,
					type: 'text',
					value: this.pattern
				},
				{
					name: 'start_datetime',
					label: `${this.$t('from')}:`,
					type: 'datetime-local',
					value: ''
				},
				{
					name: 'end_datetime',
					label: `${this.$t('To')}:`,
					type: 'datetime-local',
					value: ''
				}
			],
			today: new Date().toISOString().slice(0, 10),
			max_lines: 100
		};
	},
	watch: {
		'$i18n.locale'() {
			this.setValueChangeLang();
		},
		patternFilter() {
			this.reset();
		},
		startTime() {
			this.reset();
		},
		endTime() {
			this.reset();
		}
	},
	resources: {
		binaryLogs() {
			return {
				url: 'press.api.analytics.binary_logs',
				params: {
					name: this.site?.name,
					start_time: this.startTime || this.today,
					end_time: this.endTime || this.today,
					pattern: this.patternFilter,
					max_lines: this.max_lines
				},
				auto: true,
				pageLength: 10,
				keepData: true,
				initialData: []
			};
		},
		getPlan() {
			return {
				url: 'press.api.site.current_plan',
				params: {
					name: this.site?.name
				},
				auto: true
			};
		}
	},
	methods: {
		setValueChangeLang() {
			this.colTable = [
				{ label: this.$t('Timestamp'), name: 'timestamp', class: 'w-3/12' },
				{ label: this.$t('Query'), name: 'query', class: 'w-9/12' }
			];

			this.filters = [
				{
					name: 'pattern',
					label: `${this.$t('search')}:`,
					type: 'text',
					value: this.pattern
				},
				{
					name: 'start_datetime',
					label: `${this.$t('from')}:`,
					type: 'datetime-local',
					value: ''
				},
				{
					name: 'end_datetime',
					label: `${this.$t('To')}:`,
					type: 'datetime-local',
					value: ''
				}
			];
		},
		reset() {
			this.$resources.binaryLogs.reset();
		}
	},
	computed: {
		startTime() {
			return this.filters[1].value;
		},
		endTime() {
			return this.filters[2].value;
		},
		patternFilter() {
			return this.filters[0].value;
		},
		formatData() {
			let binaryData = this.$resources.binaryLogs.data;
			let data = [];
			binaryData.forEach(row => {
				let timestamp = this.formatDate(
					row.timestamp,
					'TIME_24_WITH_SHORT_OFFSET'
				);
				let out = [
					{ name: 'Timestamp', value: timestamp, class: 'w-3/12' },
					{ name: 'Query', value: row.query, class: 'w-9/12' }
				];
				data.push(out);
			});
			return data;
		}
	}
};
</script>
