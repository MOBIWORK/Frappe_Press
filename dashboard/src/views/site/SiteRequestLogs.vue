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
				:title="$t('Request_Logs')"
				:columns="[
					{ label: $t('Time'), name: 'time', class: 'w-2/12' },
					{ label: $t('Method'), name: 'method', class: 'w-1/12' },
					{ label: $t('Path'), name: 'path', class: 'w-5/12' },
					{ label: $t('Status_Code'), name: 'status', class: 'w-2/12' },
					{ label: $t('CPU_Time_(seconds)'), name: 'cpu_time', class: 'w-2/12' }
				]"
				:data="formatData"
				:filters="[sortFilter, dateFilter]"
			/>

			<div
				class="px-2 py-2 text-base text-gray-600"
				v-if="
					$resources.requestLogs.loading &&
					$resources.requestLogs.data.length == 0
				"
			>
				<LoadingText />
			</div>
			<div
				class="py-2 text-base text-gray-600"
				v-if="
					!$resources.requestLogs.loading &&
					$resources.requestLogs.data.length == 0
				"
			>
				{{ $t('no_data') }}
			</div>
			<Button
				v-if="$resources.requestLogs.data && $resources.requestLogs.data.length"
				:loading="$resources.requestLogs.loading"
				:loadingText="`${$t('loading')}...`"
				@click="start += 10"
			>
				{{ $t('load_more') }}
			</Button>
		</Card>
	</div>
	<div class="flex justify-center" v-else>
		<span class="mt-16 text-base text-gray-700">
			{{ $t('SiteRequestLogs_content_1') }}
		</span>
	</div>
</template>

<script>
import { DateTime } from 'luxon';
import Report from '@/components/Report.vue';

export default {
	name: 'SiteRequestLogs',
	props: ['site'],
	components: {
		Report
	},
	data() {
		return {
			date: null,
			sort: 'CPU Time (Descending)',
			start: 0,
			sortFilter: {},
			dateFilter: {
				name: 'date',
				type: 'date',
				value: null
			}
		};
	},
	watch: {
		'$i18n.locale'(val) {
			this.setValueFilter();
		},
		sort(value) {
			this.reset();
		}
	},
	mounted() {
		this.setValueFilter();
	},
	resources: {
		requestLogs() {
			return {
				url: 'press.api.analytics.request_logs',
				params: {
					name: this.site?.name,
					timezone: DateTime.local().zoneName,
					sort: this.sortFilter.value,
					date: this.dateFilter.value || this.today,
					start: this.start
				},
				auto: Boolean(this.today),
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
		setValueFilter() {
			let val_selected = 'CPU Time (Descending)';
			if (this.sortFilter?.value) {
				val_selected = this.sortFilter?.value;
			}
			let config = {
				name: 'sort',
				options: [
					{
						label: this.$t('Time_(Ascending)'),
						value: 'Time (Ascending)'
					},
					{
						label: this.$t('Time_(Descending)'),
						value: 'Time (Descending)'
					},
					{
						label: this.$t('CPU_Time_(Descending)'),
						value: 'CPU Time (Descending)'
					}
				],
				type: 'select',
				value: val_selected
			};
			this.sortFilter = config;
		},
		reset() {
			this.$resources.requestLogs.reset();
			this.start = 0;
		}
	},
	computed: {
		today() {
			return DateTime.local().toISODate();
		},
		formatData() {
			let requestData = this.$resources.requestLogs.data;
			let data = [];
			requestData.forEach(log => {
				log.time = this.formatDate(log.timestamp, 'TIME_24_WITH_SHORT_OFFSET');
				log.method = log.request.method;
				log.path = log.request.path;
				log.status = log.request.status_code;
				log.cpu_time = this.$formatCPUTime(log.duration);

				let row = [
					{ name: $t('Time'), value: log.time, class: 'w-2/12' },
					{ name: $t('Method'), value: log.method, class: 'w-1/12' },
					{ name: $t('Path'), value: log.path, class: 'w-5/12 break-all pr-2' },
					{ name: $t('Status_Code'), value: log.status, class: 'w-2/12' },
					{
						name: $t('CPU_Time_(seconds)'),
						value: log.cpu_time,
						class: 'w-2/12'
					}
				];
				data.push(row);
			});
			return data;
		}
	}
};
</script>
