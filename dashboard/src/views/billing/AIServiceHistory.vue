<template>
	<Card
		:title="$t('ai_service_usage_history')"
		:subtitle="$t('des_ai_service_usage')"
	>
		<div class="mb-4 grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
			<FormControl
				class="w-full"
				:label="$t('start_time')"
				v-model="filters.start_time"
				type="date"
			></FormControl>
			<FormControl
				class="w-full"
				:label="$t('end_time')"
				v-model="filters.end_time"
				type="date"
			></FormControl>
			<FormControl
				class="w-full"
				:label="$t('service')"
				v-model="filters.service_name"
				type="text"
			></FormControl>
			<div class="flex items-end">
				<Tooltip :text="$t('clear_filter')">
					<Button theme="gray" variant="subtle" @click="clearFilter">
						<ClearFilterIcon class="h-4 w-4" />
					</Button>
				</Tooltip>
			</div>
		</div>
		<div>
			<div class="max-h-96 overflow-auto">
				<table class="table w-full border-separate">
					<thead>
						<tr class="text-base text-gray-600">
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('Time') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('service_name') }}
							</th>
							<th
								class="sticky top-0 min-w-56 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('description') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('processing_unit') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('unit_price') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('VAT') }}
							</th>
							<th
								class="sticky top-0 min-w-28 border-b bg-white px-2 py-4 text-left"
							>
								{{ $t('Amount') }}
							</th>
						</tr>
					</thead>
					<tbody class="text-center text-base text-gray-600" v-if="!dataTrans">
						<tr>
							<td class="px-2 py-4" colspan="7">
								<div class="flex justify-center">
									<LoadingText :text="$t('Loading') + '...'" />
								</div>
							</td>
						</tr>
					</tbody>
					<tbody v-else-if="dataTrans?.length">
						<tr
							v-for="d in dataTrans"
							:key="d.name"
							class="text-base text-gray-900"
						>
							<td class="border-b px-2 py-4">
								{{ this.$formatDateDetail(d.start_time) }}
							</td>
							<td class="border-b px-2 py-4 text-gray-700">
								{{ d.service_name }}
							</td>
							<td class="border-b px-2 py-4">
								{{ d.description }}
							</td>
							<td class="border-b px-2 py-4">
								{{ d.formatted.processing_unit }}
							</td>
							<td class="border-b px-2 py-4">{{ d.formatted.unit_price }}</td>
							<td class="border-b px-2 py-4">{{ d.formatted.vat }}%</td>
							<td class="border-b px-2 py-4">{{ d.formatted.amount }}</td>
						</tr>
					</tbody>
					<tbody class="text-center text-base text-gray-600" v-else>
						<tr>
							<td class="px-2 py-4" colspan="7">
								{{ $t('no_results') }}
							</td>
						</tr>
					</tbody>
				</table>
			</div>
			<div class="flex flex-wrap items-center justify-end py-2">
				<Pagination
					v-if="dataTrans?.length"
					:options="optionsPagination"
					@updatePage="updatePage"
				/>
			</div>
		</div>
	</Card>
</template>
<script>
import { notify } from '@/utils/toast';
import StatusOrder from '@/components/StatusOrder.vue';
import { translate } from '@/utils/index';
import { LoadingText } from 'frappe-ui';
import { watchDebounced } from '@vueuse/core';
import Pagination from '@/components/Table/Pagination.vue';
import ClearFilterIcon from '@/components/icons/ClearFilterIcon.vue';

export default {
	name: 'AIServiceHistory',
	components: {
		LoadingText,
		Pagination,
		ClearFilterIcon
	},
	data() {
		return {
			dataTrans: null,
			filters: this.setDefaultFilter(),
			optionsPagination: {
				currentPage: 1,
				totalPages: 0,
				pageSize: 20,
				total: 0
			}
		};
	},
	resources: {
		balances() {
			return {
				url: 'press.api.billing.get_ai_service_transaction_history',
				onSuccess(data) {
					this.optionsPagination = {
						currentPage: data?.pagination?.page,
						totalPages: data?.pagination.total_page,
						pageSize: data?.pagination.page_length,
						total: data?.pagination.total
					};
					this.dataTrans = data?.result;
				}
			};
		}
	},
	mounted() {
		watchDebounced(
			() => ({ ...this.filters }),
			val => {
				this.dataTrans = null;
				this.getHistory();
			},
			{ debounce: 300, maxWait: 1000, deep: true, immediate: true }
		);
	},
	inject: ['viewportWidth'],
	methods: {
		setDefaultFilter() {
			return {
				start_time: this.$startTimeOfMonth(),
				end_time: this.$endTimeOfMonth(),
				service_name: null,
				page: 1
			};
		},
		clearFilter() {
			this.filters = this.setDefaultFilter();
		},
		updatePage(page) {
			this.filters = {
				...this.filters,
				page: page
			};
		},
		getHistory() {
			this.$resources.balances.submit(this.filters);
		},
		getStatus(d) {
			let color = d.status == 'Settled' ? 1 : 3;
			return color;
		}
	}
};
</script>
