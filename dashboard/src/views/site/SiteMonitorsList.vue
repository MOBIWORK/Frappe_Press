<template>
	<!-- <div class="grid grid-cols-1 gap-5 sm:grid-cols-3"> -->
	<div v-if="$route.fullPath.endsWith('/monitor')" class="flex flex-col gap-3">
		<div
			class="hover:bg-gray-100 sm:rounded-md sm:border sm:border-gray-100 sm:px-2 sm:py-1 sm:shadow"
		>
			<router-link :to="{ name: 'SiteRequestLogs', params: { siteName } }">
				<div class="py-2 text-gray-900 sm:px-2">{{ $t('Request_Logs') }}</div>
			</router-link>
		</div>
		<div
			class="hover:bg-gray-100 sm:rounded-md sm:border sm:border-gray-100 sm:px-2 sm:py-1 sm:shadow"
		>
			<router-link :to="{ name: 'SiteBinaryLogs', params: { siteName } }">
				<div class="py-2 text-gray-900 sm:px-2">
					{{ $t('mariadb_binary_log_report') }}
				</div>
			</router-link>
		</div>
		<div
			class="hover:bg-gray-100 sm:rounded-md sm:border sm:border-gray-100 sm:px-2 sm:py-1 sm:shadow"
		>
			<router-link :to="{ name: 'MariaDBProcessList', params: { siteName } }">
				<div class="py-2 text-gray-900 sm:px-2">
					{{ $t('Mariadb_Process_List') }}
				</div>
			</router-link>
		</div>
		<div
			class="hover:bg-gray-100 sm:rounded-md sm:border sm:border-gray-100 sm:px-2 sm:py-1 sm:shadow"
		>
			<router-link
				:to="{
					name: 'SiteMariaDBSlowQueries',
					params: { siteName }
				}"
			>
				<div class="py-2 text-gray-900 sm:px-2">
					{{ $t('Mariadb_Slow_Queries_Report') }}
				</div>
			</router-link>
		</div>
		<div
			class="hover:bg-gray-100 sm:rounded-md sm:border sm:border-gray-100 sm:px-2 sm:py-1 sm:shadow"
		>
			<router-link :to="{ name: 'SiteDeadlockReport', params: { siteName } }">
				<div class="py-2 text-gray-900 sm:px-2">{{ $t('Deadlock') }}</div>
			</router-link>
		</div>
	</div>
	<router-view v-slot="{ Component }">
		<component v-if="site" :is="Component" :site="site"></component>
	</router-view>
</template>
<script>
import Report from '@/components/Report.vue';

export default {
	name: 'SiteMonitorsList',
	props: ['site', 'siteName'],
	components: {
		Report
	}
};
</script>
