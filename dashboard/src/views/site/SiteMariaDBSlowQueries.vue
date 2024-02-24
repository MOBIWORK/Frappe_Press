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
				:columns="[
					{ label: $t('Timestamp'), name: 'timestamp', class: 'w-2/12' },
					{ label: $t('Query'), name: 'query', class: 'w-7/12' },
					{ label: $t('Duration'), name: 'duration', class: 'w-1/12' },
					{ label: $t('Rows_Examined'), name: 'examined', class: 'w-1/12' },
					{ label: $t('Rows_Sent'), name: 'sent', class: 'w-1/12' }
				]"
				:data="formatSlowQueries"
				:title="$t('Mariadb_Slow_Queries_Report')"
			/>
			<div
				class="px-2 py-2 text-base text-gray-600"
				v-if="
					$resources.slowQueries.loading &&
					$resources.slowQueries.data.length == 0
				"
			>
				<LoadingText />
			</div>
			<div
				class="py-2 text-base text-gray-600"
				v-if="
					!$resources.slowQueries.loading &&
					$resources.slowQueries.data.length == 0
				"
			>
				{{ $t('no_data') }}
			</div>
			<Button
				v-if="$resources.slowQueries.data && $resources.slowQueries.data.length"
				:loading="$resources.slowQueries.loading"
				:loadingText="`${$t('loading')}...`"
				@click="max_lines += 20"
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
	name: 'SiteMariaDBSlowQueries',
	props: ['site'],
	components: {
		Report
	},
	data() {
		return {
			filters: [
				{
					name: 'pattern',
					label: `${this.$t('search')}:`,
					type: 'text',
					value: this.pattern
				},
				{
					name: 'start',
					label: `${this.$t('from')}:`,
					type: 'datetime-local',
					value: ''
				},
				{
					name: 'end',
					label: `${this.$t('to')}:`,
					type: 'datetime-local',
					value: ''
				}
			],
			max_lines: 20
		};
	},
	watch: {
		'$i18n.locale'() {
			this.filters = [
				{
					name: 'pattern',
					label: `${this.$t('search')}:`,
					type: 'text',
					value: this.pattern
				},
				{
					name: 'start',
					label: `${this.$t('from')}:`,
					type: 'datetime-local',
					value: ''
				},
				{
					name: 'end',
					label: `${this.$t('to')}:`,
					type: 'datetime-local',
					value: ''
				}
			];
		},
		pattern() {
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
		slowQueries() {
			return {
				url: 'press.api.analytics.mariadb_slow_queries',
				params: {
					site: this.site?.name,
					start: this.startTime || this.today,
					end: this.endTime || this.today,
					pattern: this.pattern,
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
		reset() {
			this.$resources.slowQueries.reset();
		}
	},
	computed: {
		startTime() {
			return this.filters[1].value;
		},
		endTime() {
			return this.filters[2].value;
		},
		pattern() {
			return this.filters[0].value;
		},
		formatSlowQueries() {
			let data = [];
			this.$resources.slowQueries.data.forEach(row => {
				let time = this.formatDate(row.timestamp, 'TIME_24_WITH_SHORT_OFFSET');
				let out = [
					{ name: 'Timestamp', value: time, class: 'w-2/12' },
					{ name: 'Query', value: row.query, class: 'w-7/12' },
					{ name: 'Duration', value: row.duration, class: 'w-1/12' },
					{ name: 'Examined', value: row.rows_examined, class: 'w-1/12' },
					{ name: 'Sent', value: row.sent, class: 'w-1/12' }
				];
				data.push(out);
			});
			return data;
		}
	}
};
</script>
